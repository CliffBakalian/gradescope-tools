from selenium import webdriver
from selenium.webdriver.common.by import By
#from selenium.webdriver.common.keys import Keys

from dotenv import dotenv_values

import logging
from utils import setup, checkPage

from scraper import scrapeAssignments, scrapeCourses

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
start by setting up a logger to make sure everything runs smoothly
then we setup the driver and login to gradescope
'''

logging.basicConfig(filename='debug.log', level=logging.INFO)
driver = login(setup())

'''
courses = scrapeCourses(driver)
print(courses)
assignments = scrapeAssignments(driver,str(config['COURSE']))
print(assignments)
'''
