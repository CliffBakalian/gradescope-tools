from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException

import logging
import re
import os

from utils import checkPage

'''
if you are at gradescope's homepage after calling login() we want to get all
the courses you are in for the current semester. 
the find element will just get the first courseList (the current term)

returns a [(course name, course link)] tuple
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
      courses = [(elem.find_element(By.CLASS_NAME, shortname).text, 
                 elem.get_attribute('href').split("/")[-1]) 
                 for elem in courseList if len(elem.find_elements(By.CLASS_NAME, shortname)) > 0]
      return courses
    else:
      browser.close()
      logging.error("Course Scrape Failed: not on homepage)")

'''
so you can feed this a course, or just iterate through the courses returned from
scrapeCourses.
If you provide a course, make sure the course is a valid id.
Then go the assignments page and go through the list of assignments to make a
(assignment name, link, published?) tuple list
'''
def scrapeAssignments(browser,course=None):
  if course:
    expected = "https://www.gradescope.com/courses/"+course+"/assignments" 
  browser = getAssignmentsPage(browser,course)
  if not course or checkPage(browser,expected):
    TABLE_NAME= "table-assignments"
    assignmentTable = browser.find_element(By.CLASS_NAME, TABLE_NAME)
    # now we can get the assignments row, each row has name, link, published, bumber of submissions, etc
    assignmentList = assignmentTable.find_elements(By.CLASS_NAME, "js-assignmentTableAssignmentRow")

    ret = []
    for elem in assignmentList:
      name = elem.find_element(By.CLASS_NAME, "table--primaryLink").text
      # gradescope layout is weird. in this case, they had a seperate <a> tag
      # which then had the href value. 
      # link looks like https://gradescope..../assignments/ASSIGNMENT_ID, we want just the ASSIGNMENT_ID 
      link = elem.find_element(By.TAG_NAME,"a").get_attribute('href').split("/")[-1]
      complete = False
      try:
        complete = elem.find_element(By.CLASS_NAME,"workflowCheck-incomplete") == []
      except NoSuchElementException:
        complete = True
      ret.append((name,link,complete))
    return ret 
  else:
    browser.close()
    logging.error("Assignments page for " + assignment + " Not Found: check course ID")
'''
Each assignment has a series of questions (even projects).
Has a name, a link, and how much is graded
return this info as a (name, link, percent graded) tuple
'''
def scrapeQuestions(browser,course,assignment):
  expected = "https://www.gradescope.com/courses/"+course+"/assignments/" + assignment + "/grade" 
  browser.get(expected)
  if checkPage(browser,expected):
    TABLE_NAME = "gradingDashboard"
    questionTable = browser.find_element(By.CLASS_NAME, TABLE_NAME) #table 
    #every row has this class. idk why
    questionList = questionTable.find_elements(By.CLASS_NAME, "table--row-resetTopBorder") 

    ret = []
    for elem in questionList:
      # need to get link to submissions. The first link is good enough
      try:
        titleColumn = elem.find_element(By.TAG_NAME,"a")
        # link will point to 'courses/COURSE_ID/questions/QUESTION_ID/grade. We want QUESTION_ID
        link = titleColumn.get_attribute('href').split("/")[-2]
        # text is the name of the question
        name = titleColumn.text
        # the percent graded falls under this progressPercent column 
        # the format is "Percent graded for question x:\ny%" so we split on \n and get rid of the % sign
        percentDone = int(elem.find_element(By.CLASS_NAME, "gradingDashboard--progressPercent").text.split("\n")[1][:-1])
        ret.append((name,link,percentDone))
      except:
        print("Could not scrape question for course: " + course + "assignment: " + assignment)
    return ret
  else:
    browser.close()
    logging.error("Question page for " + assignment + " Not Found: check course ID")

'''
Each question submission has table of questions, the points, and the grader. 
We only care about the grader.
return a dict of (grader_name: count)
the url here does not use assignmne,but course and question id
'''
def scrapeCount(browser,course,question):
  expected = "https://www.gradescope.com/courses/"+course+"/questions/" + question+ "/submissions" 
  browser.get(expected)
  if checkPage(browser,expected):
    TABLE_NAME = "question_submissions"
    ret = {}
    try:
      questionTable = browser.find_element(By.ID, TABLE_NAME).find_element(By.TAG_NAME,"tbody") #table  only one that uses an id, weird.
      # this table alternames names "odd" and "even". No other table does. Weird.
      questionList = questionTable.find_elements(By.TAG_NAME, "tr") 

      for elem in questionList:
        # need to get name. It is the third column in the table 
        third_column = elem.find_elements(By.TAG_NAME,"td")[2]
        name = third_column.text
        if name != '':
          if name in ret:
            ret[name] += 1
          else:
            ret[name] = 1
    except:
      print("Could not scrape count for course: " + course + "question: " + question)
    return ret
  else:
    browser.close()
    logging.error("Question page for " + course + " Not Found: check course ID")
  return {}


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
    logging.error("Course " + course + " Not Found: check course ID")

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
    logging.error("Assignment Page for the course " + course + " Not Found: check course ID")
