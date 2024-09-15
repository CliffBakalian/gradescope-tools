import multiprocessing as mp
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

import logging
import re
import os
import time as libtime
from utils import get_driver

"""
driver: a selenium driver 

returns (course name:string, course_id:string) tuple list

Go to homepage and get the courses you are in for the current semester. 
the find element will just get the first courseList (the current term)
"""
def scrapeCourses(driver):
  expected = "https://www.gradescope.com/account" 
  try:
    driver.get(expected)
  except:
    driver.close()
    logging.error("Course Scrape Failed: could not get page)")
    exit(1)

  currentTerm = driver.find_element(By.CLASS_NAME,
                                     "courseList--coursesForTerm")
  courseList = currentTerm.find_elements(By.CLASS_NAME,"courseBox")
  logging.info("Got the Courses for the current term")
  shortname = "courseBox--shortname"
  
  '''
  for each course in the semester, make a list of (course name, link) tuples
  the len check is becasuse the last one in the list is the "create new 
  course" option if you are an instructor. 
  '''
  courses = [(elem.find_element(By.CLASS_NAME, shortname).text, 
              re.search('(\d+)$',elem.get_attribute('href')).group(1)) 
              for elem in courseList 
                if len(elem.find_elements(By.CLASS_NAME, shortname)) > 0]
  return courses

"""
driver: a selenium driver 
course: string of course ID

returns (assignment name:string, id:string) tuple list

Go to the assignments page and go through the list of assignments 
"""
def scrapeAssignments(driver,course):
  expected = "https://www.gradescope.com/courses/"+course+"/assignments" 
  try:
    driver.get(expected)
  except:
    driver.close()
    logging.error("Assignment Scrape Failed: failed to get page)")
    exit(1)

  # gradescpope has a lot of hidden tables. ID is unique to the page
  try:
    assignmentTable = driver.find_element(By.CLASS_NAME, 
                                           "table-assignments")
  except:
    driver.close()
    logging.error("Assignment Scrape Failed: failed to find table assignments)")
    exit(1)

  try:
    # now we can get the assignmentsrow because we are in the unique ID
    assignmentList = assignmentTable.find_elements(By.CLASS_NAME, 
                                              "js-assignmentTableAssignmentRow")
    table = "table--primaryLink"
    # gradescope layout is weird. in this case, they had a seperate <a> tag
    # which then had the href value
  except:
    driver.close()
    logging.error("Assignment Scrape Failed: failed to find table assignments)")
    exit(1)
  assignments = [(elem.find_element(By.CLASS_NAME, table).text, 
                  re.search('(\d+)$',
                  elem.find_element(By.TAG_NAME,"a").get_attribute('href')).group(1)) 
                    for elem in assignmentList]
  return assignments
    
"""
driver: a selenium driver 
course: string of course ID
assignment: string of the assignment ID

this will open the 'review_grades' page for the assignment and return a tuple 
list of (student name, link to last submission) for everyone who submitted
"""

def scrapeLatestSubmission(driver, course, assignment):
  expected = ("https://www.gradescope.com/courses/"+course+
             "/assignments/"+assignment+
             "/review_grades")
  try:
    driver.get(expected)
  except:
    driver.close()
    logging.error("Latest Submission  Scrape Failed: could not get page)")
    exit(1)

  #this seems like a terrible id name. Gradescope should change in the future
  #but then this script would break.
  try:
    submissionTable = driver.find_element(By.ID, "DataTables_Table_0").find_element(By.TAG_NAME,"tbody") 
    rows = submissionTable.find_elements(By.CLASS_NAME,"table--primaryLink")
  except:
    logging.error("Could not find the submission table or could not link info. Check ID or url")
    driver.close()
    exit(1)

  # assuming the first link the name and submission link
  try:
    # I have no idea why a primary link would not have an "a" tag after 
    # looking at the source, but I know by converting from find_element
    # to find_elements, then checking list length > 0 works for some reason
    links = list(map(lambda row: row.find_elements(By.TAG_NAME,"a"),rows))
    submissions = [(link[0].text,link[0].get_attribute('href')[-9:]) 
                    for link in links if len(link) > 0] 
  except:
    logging.error("Failed to find the link. Check to make sure there is an actual submission")
    return None
  logging.info("got the submissions")
  return submissions

"""
driver: a selenium driver 
course: string of course ID
assignmnet: string of the assignment ID

returns (name:string, 
         section:string, 
         due_date:ISO 8601 date string,
         late_due_date:ISO 8601 date string
        ) list

Go to the extension page and get the extensions

Section is added because some people have same first and last name and
hopefully section will catch it. Unfortunately the extension page does not
have any info about UID

I personally don't use the late due date but might be useful later
"""
def scrapeExtensions(driver, course, assignment):
  expected = "https://www.gradescope.com/courses/"+course+"/assignments/"+assignment+"/extensions"
  try:
    driver.get(expected)
  except:
    driver.close()
    logging.error("Extension Scrape Failed: could not get page)")
    exit(1)

  try:
    submissionTable = driver.find_element(By.ID, "DataTables_Table_0").find_element(By.TAG_NAME,"tbody") 
    rows = submissionTable.find_elements(By.TAG_NAME,"tr")
  except:
    logging.error("Could not find the extension table or could not link info. Check ID or url")
    driver.close()

  extensions = []
  for row in rows:
    try:
      cols = row.find_elements(By.TAG_NAME,"td")
      name_col = cols[0]
      section_col = cols[2]
      due_date_col = cols[4]
      late_due_date_col = cols[5]
    except:
      logging.error("table malformed I think")
      driver.close()
      exit(1)
    name = name_col.text
    section = section_col.text
    try:
      due_date = due_date_col.find_element(By.TAG_NAME,"time").get_attribute("datetime")
    except:
      due_date = None
    try:
      late_due_date = late_due_date_col.find_element(By.TAG_NAME,"time").get_attribute("datetime")
    except:
      late_due_date = None
    extensions.append((name,section,due_date,late_due_date))
  return extensions

"""
driver: a selenium driver 
course: string of course ID
assignmnet: string of the assignment ID
submission: string of submission ID

returns (submission_time:ISO 8601 date string,
         score:string (in float format)
        ) list

This will open the 'submission history box' for the assignment and 
return a tuple list of (date submitted, score). For assignments like quizzes and
exams, there is no score column, so the score will be None (despite the score
being recorded. This score can be found when downloading the grades for the 
semester. however, I only really need submission history for projects. quizzes 
and exams, there should be only 1.
"""
def scrapeAllSubmissions(driver,course,assignment,submission):
  expected = ("https://www.gradescope.com/courses/"+course+
             "/assignments/"+assignment+
             "/submissions/"+submission)
  try:
    driver.get(expected)
  except: 
    driver.close()
    logging.error("History Scrape Failed: could not get page for " + submission)
    exit(1)

  # get the bar of buttons at the bottom
  try:
    buttonsbar = driver.find_element(By.CLASS_NAME, "actionBar--actionList")
    buttons = buttonsbar.find_elements(By.TAG_NAME,"button")
    button = None
    for b in buttons:
      if b.text == "Submission History":
        button = b
        logging.info("found button")
        break
    if not button:
      logging.error("Could not find the submission history button (submission:" + 
                    submission +")")
  except:
    logging.error("Could not find the button bar. make sure all IDS are correct (submission:" + submission+")")
    driver.close()
    exit(1)

  try:
    button.click()
  except:
    logging.error("Failed to click button (submission: " + submission+ ")")
    driver.close()
    exit(1)
    
  try:
    '''
    tried different classnames but the body loads with a header 
    but the data says "loading history"...
    Since we need to wait for history submissions to load 
    we can't wait for table-submissionhistory--body or row, 
    wait until the last submission loads
    which is 'table--row-emph'
    '''

    WebDriverWait(driver,timeout=120).until(lambda b: b.find_element(By.CLASS_NAME,"table--row-emph"))
  except:
    logging.error("Failed to find history table. button did not fire or something (submission: " + submission + ")")
    driver.close()
    exit(1)

  try:
    # now that table loaded, we can actually get the rows. We take off the
    # first one because that is just the header
    rows = driver.find_elements(By.CLASS_NAME,"table-submissionHistory--row")[1:]
    results = [(row.find_element(By.TAG_NAME,"time").get_attribute("datetime"),
               row.find_elements(By.TAG_NAME,"td")[3].text) 
                 for row in rows]
    return results 
  except:
    logging.error("Failed to get time or score. check tag names I guess (submission:" + submission + ")")
    driver.close()
    exit(1)




""" --------------------------------- CACHE ------------------------------- """




"""
driver: a selenium driver 
course: string of course ID
assignment: string of the assignment ID

Writes the results of scrapeExtensions(driver,course,assignment) to
assignment/assignment.exts
"""
def cache_extension(driver,course,assignment):
  logging.info("Caching "+assignment + "extentions")
  # make the assignment directory if does not exist
  if not os.path.exists(assignment):
    os.mkdir(assignment)
    logging.info("made "+assignment+" folder")

  exts = scrapeExtensions(driver,course,assignment)
  with open(os.path.join(assignment,assignment+'.exts'),'w') as f:
    if exts:
      for s,l,d,ld in exts:
        f.write(str(s)+","+str(l)+","+str(d)+","+str(ld)+"\n") 
  logging.info("Cached extensions for " + str(assignment) + " !")

"""
driver: a selenium driver 
course: string of course ID
assignment: string of the assignment ID

Writes the results of scrapeLatestSubmission(driver,course,assignment) to
assignment/assignment.cache
"""
def cache_student_submissions(driver,course,assignment):
  logging.info("Caching latest subs for "+assignment)
  cache = scrapeLatestSubmission(driver,course,assignment)
  if not os.path.exists(assignment):
    logging.info("made "+assignment+" folder")
    os.mkdir(assignment)
  with open(os.path.join(assignment,assignment+'.cache'),'w') as f:
    for s,l in cache:
      f.write(str(s)+","+str(l)+"\n") 
  logging.info("Cached!")
  return cache

"""
driver: a selenium driver 
course: string of course ID
assignment: string of the assignment ID
submission: string of submission ID
student: name of student

Caches all student's history for that assignment
"""
def cacheSingleStudentHistory(driver,course,assignment,submission,student):
  # make the assignment directory if does not exist
  if not os.path.exists(assignment):
    logging.info("made "+assignment+" folder")
    os.mkdir(assignment)

  hist = scrapeAllSubmissions(driver,course,assignment,submission)
  student_file = os.path.join(assignment,student+"."+assignment)
  with open(str(student_file),'w') as f:
    for (time,score) in subs:
      f.write(time+","+score+"\n") 
  logging.info("Cached!")


""" --------------------------- Multiprocessing --------------------------- """




"""
#driver: a selenium driver 
course: string of course ID
assignment: string of the assignment ID
submission_with_names: (string,string) list-the result of calling
                       scrapeLatestSubmissions

this will go through all (name,submission) pairs in submission_with_names and
cache each student's submissions via the Pool class of multiprocessing
"""
def cache_histories(course,assignment,submissions_with_names):
  def worker(x):
    (student,submission) = x
    driver = get_driver()
    cacheSingleStudentHistory(driver,course,assignment,submission,student)
  processes = mp.Pool(mp.cpu_count())
  processes.map(worker,submissions_with_names)
