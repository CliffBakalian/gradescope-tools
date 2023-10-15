import logging
from dotenv import dotenv_values
from selenium import webdriver
from selenium.webdriver.common.by import By

from utils import * #login, setup, store_courses
from scraper import *

config = dotenv_values(".env")
username = config["USERNAME"]
password = config["PASSWORD"]
TEST_COURSE = config['TEST_COURSE']
TEST_ASSIGNMENT = config['TEST_ASSIGNMENT']
TEST_QUESTION = config['TEST_QUESTION']

test = False

'''
start by setting up a logger to make sure everything runs smoothly
then we setup the driver and login to gradescope. Then get all data
'''
logging.basicConfig(filename='debug.log', level=logging.INFO)
driver = login(setup(),username,password)

if test:
  courses = scrapeCourses(driver)
  assert(courses == [('CMSC330', 'https://www.gradescope.com/courses/561034'), ('CMSC330 Sandbox', 'https://www.gradescope.com/courses/598515'), ('cmsc389t-fall23', 'https://www.gradescope.com/courses/590767')])

#store_courses(scrapeCourses(driver))
#store_assignments("CMSC330",scrapeAssignments(driver,TEST_COURSE))
#store_questions("CMSC330","Exam 1",scrapeQuestions(driver,TEST_COURSE,TEST_ASSIGNMENT))
#print(scrapeQuestions(driver,TEST_COURSE,TEST_ASSIGNMENT))
#print(scrapeCount(driver,TEST_COURSE,TEST_QUESTION))
#store_assignment("Exam 1","Question 11: 2(b) Regex Engineering",scrapeCount(driver,TEST_COURSE,TEST_QUESTION))
def do_it_all():
  courses = scrapeCourses(driver)
  store_courses(courses)
  for (name,link) in courses:
    assignments = scrapeAssignments(driver,link)
    store_assignments(name,assignments)
    for (aname,alink,_) in assignments:
      questions = scrapeQuestions(driver,link,alink)
      store_questions(name,aname,questions)
      for (qname,qlink,_) in questions:
        counts = scrapeCount(driver,link,qlink)
        store_assignment(aname,qname,counts)
do_it_all()
