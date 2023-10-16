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

'''
this causes my laptop to freeze up. Haven't tried on big boi
'''
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

def update_assignments(course):
  course_file=course+".json"
  f = open(course_file)
  if not f:
    err = "Could not find " + course_json
    logging.error(err)
    print(err)
    exit(1)
  try:
    course = json.load(f)
  except json.JSONDecodeError:
    err = course_file+ " is malformed"
    logging.error(err)
    print(err)
    exit(1)
  f.close()
  link = course['link']
  assignments = scrapeAssignments(driver,link)
  #store_assignments(course,link)

def update_questions(course,assignment=None):
  course_file=course+".json"
  f = open(course_file)
  if not f:
    err = "Could not find " + course_json
    logging.error(err)
    print(err)
    exit(1)
  try:
    course = json.load(f)
  except json.JSONDecodeError:
    err = course_file+ " is malformed"
    logging.error(err)
    print(err)
    exit(1)
  f.close()
  course_link = course['link']
  for assign in course['assignments']:
    if not assignment or assign['name'] == assignment:
      alink = assign['link']
      questions = scrapeQuestions(driver,course_link,alink)
      store_questions(course['name'],assign['name'],questions)

def update_counts(course,assignment_id,question=None):
  assign_file=assignment_id+".json"
  f = open(assign_file)
  if not f:
    err = "Could not find " + assign_file
    logging.error(err)
    print(err)
    exit(1)
  try:
    assign = json.load(f)
  except json.JSONDecodeError:
    err = assign_file+ " is malformed"
    logging.error(err)
    print(err)
    exit(1)
  f.close()
  course_file=course+".json"
  f = open(course_file)
  if not f:
    err = "Could not find " + course_file
    logging.error(err)
    print(err)
    exit(1)
  try:
    coursejson = json.load(f)
  except json.JSONDecodeError:
    err = course_file+ " is malformed"
    logging.error(err)
    print(err)
    exit(1)
  f.close()
  course_id = coursejson['link']
  if question:
    for q in assign['questions']:
      if q['link'] == question:
        counts = scrapeCount(driver,course_id,question)
        q['counts'] = counts
  else:
    for assignment in coursejson['assignments']:
      if assignment['link'] == assignment_id:
        for q in assignment['questions']:
          counts = scrapeCount(driver,course_id,q['link'])
          store_assignment(assignment_id,q['name'],counts)
