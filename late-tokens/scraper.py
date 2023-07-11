from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

import logging
import re
import os

from utils import checkPage

'''
I don't think I actually use this
'''
def getAssignment(browser,assignment,course=None):
  if not course:
    base = browser.current_url
  else:
    base = "https://www.gradescope.com/courses/"+course
  expected = base + "/assignments/" + assignment
  browser.get(expected)
  landing_pages = ["submissions", "grade", "review_grades", "submission_batches", "rubric/edit", "outline/edit"]
  if reduce(lambda a,b: a or checkPage(browser,b),[True] + landing_pages):
    logging.info("Assignments Page Found")
    return browser
  else:
    browser.close()
    logging.error("Assignments Page Not Found: check course ID")

'''
if you are at gradescope's homepage after calling login() we want to get all
the courses you are in for the current semester. 
the find element will just get the first courseList (the current term)
'''
def scrapeCourses(browser):
    expected = "https://www.gradescope.com/account" 
    if checkPage(browser,expected):
      currentTerm = browser.find_element(By.CLASS_NAME, "courseList--coursesForTerm")
      courseList = currentTerm.find_elements(By.CLASS_NAME,"courseBox")
      logging.info("Got the Courses for the current term")
      shortname = "courseBox--shortname"
      
      '''
      for each course in the semester, make a list of (course name, link) tuple
      the len check is becasuse the last one in the list is the "create new 
      course" option if you are an instructor. 
      '''
      courses = [(elem.find_element(By.CLASS_NAME, shortname).text, elem.get_attribute('href')) for elem in courseList if len(elem.find_elements(By.CLASS_NAME, shortname)) > 0]
      return courses
    else:
      browser.close()
      logging.error("Course Scrape Failed: not on homepage)")

'''
so you can feed this a course, or just iterate through the courses returned from
scrapeCourses.
If you provide a course, make sure the course is a valid id.
Then go the assignments page and go through the list of assignments to make a
(assignment name, link) tuple list
'''
def scrapeAssignments(browser,course=None):
    if course:
      expected = "https://www.gradescope.com/courses/"+course+"/assignments" 
    browser = getAssignmentsPage(browser,course)
    if not course or checkPage(browser,expected):
      # gradescpope has a lot of hidden tables. ID is unique to the page
      assignmentTable = browser.find_element(By.ID, "assignments-instructor-table")
      # now we can get the assignmentsrow because we are in the unique ID
      assignmentList = assignmentTable.find_elements(By.CLASS_NAME, "js-assignmentTableAssignmentRow")
      table = "table--primaryLink"
      # gradescope layout is weird. in this case, they had a seperate <a> tag
      # which then had the href value
      assignments = [(elem.find_element(By.CLASS_NAME, table).text, elem.find_element(By.TAG_NAME,"a").get_attribute('href')) for elem in assignmentList]
      return assignments
    else:
      browser.close()
      logging.error("Assignments page Not Found: check course ID")

'''
this will open the 'review_grades' page for the assignment and return a tuple 
list of (student name, link to last submission) for everyone who submitted
'''
def scrapeLatestSubmission(browser,course=None,assignment=None):
  if course and assignment:
    expected = "https://www.gradescope.com/courses/"+course+"/assignments/"+assignment+"/review_grades"
  browser = getAssignmentGradesPage(browser,course,assignment)
  if (not (course or assignment)) or checkPage(browser,expected):
    #this seems like aterrible id name. Gradescope should change in the future
    #but then this script would break.
    try:
      submissionTable = browser.find_element(By.ID, "DataTables_Table_0").find_element(By.TAG_NAME,"tbody") 
      rows = submissionTable.find_elements(By.CLASS_NAME,"table--primaryLink")
    except:
      logging.error("Could not find the submission table or could not link info. Check ID or url")
      browser.close()
    else:
      # assuming the first link the name and submission link
      try:
        # I have no idea why a primary link would not have an "a" tag after 
        # looking at the source, but I know by converting from find_element
        # to find_elements, then checking list length > 0 works for some reason
        links = list(map(lambda row: row.find_elements(By.TAG_NAME,"a"),rows))
        submissions = [(link[0].text,link[0].get_attribute('href')[-9:]) for link in links if len(link) > 0] 
      except:
        logging.error("Failed to find the link. Check to make sure there is an actual submission")
        return None
      else:
        logging.info("got the submissions")
        return submissions
  else:
    browser.close()
    logging.error("Error finding the 'review_grades' page. Make sure course and assignment IDs are correct")
    logging.error("Course: "+ course + "\tAssignment: " + assignment)
    
'''
this will open the 'submission history box' for the assignment and user and 
return a tuple list of (date submitted, score). For assignments like quizzes and
exams, there is no score column, so the score will be None (despite the score
being recorded. This score can be found when downloading the grades for the 
semester. however, I only really need submission history for projects. quizzes 
and exams, there should be only 1.
'''

def scrapeAllSubmissions(browser,course=None,assignment=None,user=None):
  if course and assignment and user:
    #idk why this needs the # symbol
    #expected = "https://www.gradescope.com/courses/"+course+"/assignments/"+assignment+"/submissions/"+user+"#"
    # now it doesn't?
    expected = "https://www.gradescope.com/courses/"+course+"/assignments/"+assignment+"/submissions/"+user
  browser = getSubmissionPage(browser,course,assignment,user)
  logging.info("about to check page")
  if (not (course or assignment or user)) or checkPage(browser,expected+"#"):
    # get the bar of buttons at the bottom
    logging.info("About to scrape all subs")
    try:
      buttonsbar = browser.find_element(By.CLASS_NAME, "actionBar--actionList")
      buttons = buttonsbar.find_elements(By.TAG_NAME,"button")
      button = None
      for b in buttons:
        if b.text == "Submission History":
          button = b
          logging.info("found button")
          break
      if not button:
        logging.error("Could not find the submission history button.")
    except:
      logging.error("Could not find the button bar. make sure all IDS are correct")
      browser.close()
    else:
      try:
        button.click()
        logging.info("clicked button")
        # tried different classnames but the body loads with a header but still 
        # needs to load so can't wait for table-submissionhistory--body or row, 
        # wait until the last submission loads
        WebDriverWait(browser,timeout=10).until(lambda b: b.find_element(By.CLASS_NAME,"table--row-emph"))
        logging.info("waited for box to appear")
      except:
        logging.error("Failed to find history table. button did not fire or something")
        browser.close()
        return None
      else:
        try:
          # now that table loaded, we can actually get the rows. We take off the
          # first one because that is just the header
          rows = browser.find_elements(By.CLASS_NAME,"table-submissionHistory--row")[1:]
          results = [(row.find_element(By.TAG_NAME,"time").get_attribute("datetime"),row.find_elements(By.TAG_NAME,"td")[3].text) for row in rows]
        except:
          logging.error("Failed to get time or score. check tag names I guess")
          browser.close()
          return None
        else:
          logging.info("got the submissions")
          return results 
  else:
    browser.close()
    logging.error("Error finding the submission page. Make sure course, assignment and user IDs are correct")
    logging.error("Course: "+ course + "\tAssignment: " + assignment + "\tUser: " + user)

'''
this is just something to get to the submission page for a specific user and assignment 
'''
def getSubmissionPage(browser,course=None,assignment=None,user=None):
  if course and assignment and user : # all info given
    logging.info("getting submission page for " + user)
    url = "https://www.gradescope.com/courses/"+course+"/assignments/"+assignment+"/submissions/"+user
    logging.info("user: " + user)
    browser.get(url)
    logging.info("got submission page for " + user)
  expected = browser.current_url
  logging.info("checking expected for " + expected)
  if checkPage(browser,expected):
    logging.info("submission Found")
    return browser
  else:
    browser.close()
    logging.error("submission not found: check course,assignment,or user ID")
    logging.error("url: "+url)

'''
this is just something to get to the grades page for a specific assignment
'''
def getAssignmentGradesPage(browser,course=None,assignment=None):
  # have to do regex because default landing page is not always the review_grades one
  url_re = re.compile("https://www.gradescope.com/courses/(\d{6})/assignments/(\d{7})/.+")
  if course and assignment: # course and assignment given
    url = "https://www.gradescope.com/courses/"+course+"/assignments/"+assignment
    browser.get(url)
  expected = browser.current_url
  matched = re.fullmatch(url_re,expected)
  if matched:
    course = matched.group(1)
    assignment = matched.group(2)
    url = "https://www.gradescope.com/courses/"+course+"/assignments/"+assignment+"/review_grades"
    browser.get(url) 
    logging.info("Found grades page for: "+url)
    return browser
  else:
    browser.close()
    logging.error("Could not find assignment page. Looking at: " + expected)

'''
this is just something to get to a specific course homepage
'''
def getCoursePage(browser,course):
  expected = "https://www.gradescope.com/courses/"+course
  browser.get(expected)
  if checkPage(browser,expected):
    logging.info("Course Found")
    return browser
  else:
    browser.close()
    logging.error("Course Not Found: check course ID")

'''
this is just something to get to a specific course's assignment page 
'''
def getAssignmentsPage(browser,course=None):
  if not course:
    base = browser.current_url
  else:
    base = "https://www.gradescope.com/courses/"+course
  expected = base + "/assignments"
  browser.get(expected)
  if checkPage(browser,expected):
    logging.info("Assignments Page Found: "+ expected)
    return browser
  else:
    browser.close()
    logging.error("Assignments Page Not Found: check course ID")

'''
takes a course, and an assignment and caches's it. 
caller has to loop through all assignments
'''
def cache(driver,course,assignment):
  logging.info("Caching latest subs for "+str(assignment))
  cache = scrapeLatestSubmission(driver,str(course),str(assignment))
  if not os.path.exists(assignment):
    logging.info("made "+assignment+" folder")
    os.mkdir(assignment)
  with open(os.path.join(assignment,assignment+'.cache'),'w') as f:
    for s,l in cache:
      f.write(str(s)+","+str(l)+"\n") 
  logging.info("Cached!")
  return cache

'''
just reads the cache of latest submissions
'''
def last_sub_cache(assignment):
  if not os.path.exists(os.path.join(assignment,assignment+'.cache')):
    logging.info("failed to find cache file for " + assignment)
    return None
  ret = []
  with open(os.path.join(assignment,assignment+".cache")) as cache:
    for line in cache:
      info = line.split(",") 
      ret.append((info[0],info[1]))
  return ret

'''
takes in an assignment and course and caches all student's history  
for that assignment
'''
def cache_history(driver,course,assignment,update=False):
  logging.info("Caching "+assignment + "history")
  # make the assignment directory if does not exist
  if not os.path.exists(assignment):
    logging.info("made "+assignment+" folder")
    os.mkdir(assignment)
  if update: 
    latest = cache(driver,course,assignment)
  else:
    latest = last_sub_cache(assignment)
    if not latest:
      latest = cache(driver,course,assignment)
  for (name,sublink) in latest:
    student_file = os.path.join(assignment,name+"."+assignment)
    subs = scrapeAllSubmissions(driver,course,assignment,sublink)
    with open(str(student_file),'w') as f:
      for (time,score) in subs:
        f.write(str(time)+","+str(score)+"\n") 
      logging.info("Cached history for "+name)
  logging.info("Cached!")

def get_all_submissions(driver,course,assignment,name,user):
  if not os.path.exists(os.path.join(assignment,name+'.'+assignment)):
    print("could not find cache")
    student_file = os.path.join(assignment,name+"."+assignment)
    ret = scrapeAllSubmissions(driver,course,assignment,user) 
    with open(str(student_file),'w') as f:
      for (time,score) in ret:
        f.write(str(time)+","+str(score)+"\n") 
    return ret
  ret = []
  with open(os.path.join(assignment,name+'.'+assignment)) as cache:
    for line in cache:
      info = line.split(",") 
      ret.append((info[0],info[1]))
  return ret
