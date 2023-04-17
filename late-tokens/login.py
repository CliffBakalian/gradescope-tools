import logging
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from dotenv import dotenv_values

from utils import setup, checkPage
from scraper import scrapeAssignments, scrapeCourses, scrapeLatestSubmission, scrapeAllSubmissions

config = dotenv_values(".env")

def login(browser):
  try: 
    #find the email and password parts of the login form on graedscope's site
    browser.get('https://www.gradescope.com/login')
    username=browser.find_element("id","session_email");
    password=browser.find_element("id","session_password");
    login=browser.find_element("name", "commit")

    username.send_keys(config["USERNAME"]);
    password.send_keys(config["PASSWORD"]);
    login.click() # login

    '''
    make sure you actually logged in. It will redirect you if your credentials
    are wrong.
    '''
    expected = "https://www.gradescope.com/account" 
    if checkPage(browser,expected):
      logging.info("Login Successful")
      return browser
    else:
      browser.close()
      logging.error("Login Failed: incorrect credentials)")
  except Exception as e:
    browser.close()
    logging.error("Could not find elements on Login page or gradescope is down")
    logging.error(e)


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
this theoretically takes a course, goes through all of its assignments, 
goes through all submissions for that assignment, and gets all submission 
history and score of it all.
returns a map of course -> assignment -> user -> scores
then prints that to file
'''
def getItAll(driver):
  #get the assignments
  course = str(config['COURSE'])
  assignments = scrapeAssignments(driver,course)
  #get a list of (name,assignmentIDs)
  assigns = {}
  for name,link in assignments:
    users = {}
    assignment = link[-7:]
    #get a list of (student, submissionIDs)
    submissions = scrapeLatestSubmission(driver,course,assignment)
    for name,link in submissions:
      scores = {}
      user = link[-9:]
      # get a list of (time, score)
      results = scrapeAllSubmissions(driver,course,assignment,user)
      #map student name to (time,score)
      scores[name] = results
    users[name] = scores
  assigns[course] = users

  with open('results.json','w') as f:
    json.dump(assigns,f)

'''
start by setting up a logger to make sure everything runs smoothly
then we setup the driver and login to gradescope. Then get all data
'''

logging.basicConfig(filename='debug.log', level=logging.INFO)
driver = login(setup())
getItAll(driver)

'''
This all seems to work independently
idk if it works together tho.

courses = scrapeCourses(driver)
print(courses)
assignments = scrapeAssignments(driver,str(config['COURSE']))
print(assignments)
submissions = scrapeLatestSubmission(driver,str(config['COURSE']),str(config['TEST_ASSIGNMENT']))
print(submissions)
results = scrapeAllSubmissions(driver,str(config['COURSE']),str(config['TEST_ASSIGNMENT']),str(config['TEST_USER']))
print(results)
'''
