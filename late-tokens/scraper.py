from selenium.webdriver.common.by import By
import logging

from utils import checkPage

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
