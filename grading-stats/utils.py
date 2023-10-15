from selenium import webdriver
from dotenv import dotenv_values
import logging
import json

'''
Just some utility functions. 
'''

def get_driver():
  config = dotenv_values(".env")
  username = config["USERNAME"];
  password = config["PASSWORD"];

  logging.basicConfig(filename='debug.log', level=logging.INFO)
  driver = login(setup(),username,password)
  return driver

def login(browser,uname,pword):
  try: 
    #find the email and password parts of the login form on graedscope's site
    browser.get('https://www.gradescope.com/login')
    logging.info("got login url")
    username=browser.find_element("id","session_email");
    logging.info("found session email")
    password=browser.find_element("id","session_password");
    logging.info("found session password")
    login=browser.find_element("name", "commit")
    logging.info("found commit")

    username.send_keys(uname);
    password.send_keys(pword);
    logging.info("about to click login")
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

def setup():
  try:
    fireFoxOptions = webdriver.firefox.options.Options()
    fireFoxOptions.add_argument("--headless")
    browser = webdriver.Firefox(options=fireFoxOptions)
    logging.info("Setup Successful")
    return browser
  except Exception as e:
    browser.close()
    logging.error("Setup Failed")
    logging.error(e)

def checkPage(browser,url):
  try:
    actual = browser.current_url;
    logging.info("about to check page")
    logging.info("act: "+actual)
    logging.info("url: "+url)
    #IDK I NEED TO FIX THIS!!!!
    return True
    if actual == url or actual[:-1] == url or actual[:-2] == url:
      return True 
    else:
      logging.error("check for " + url + " failed")
      logging.error("actual   " + actual)
      logging.error("expected " + url)
      return False
  except Exception as e:
    browser.close()
    logging.error("check for " + url + " failed due to Selenium")
    logging.error(e)

'''
this will store course info and only course info
if you want to add assignments or graders you will
need to call add_assignment
'''
def store_courses(courses):
  for (name,link) in courses:
    course = {}
    course['name'] = name
    course['link'] = link
    course['assignments'] = []
    course['graders'] = []
    with open(name+".json","w") as coursejson:
      coursejson.write(json.dumps(course,indent=2))

'''
given a course name and assignment data
store the assignment data for a course.
CANNOT be used to update
'''
def store_assignments(course,assignments):
  course_file = course+".json"
  f = open(course_file)
  if not f:
    err = "Could not find " + course_json
    logging.error(err)
    print(err)
    exit(1)
  try:
    course = json.load(f)
  except json.JSONDecodeError:
    err = course_file+ " file is malformed"
    logging.error(err)
    print(err)
    exit(1)
  f.close()
  for (name,link,published) in assignments:
    assignment = {}
    assignment['name'] = name
    assignment['link'] = link
    assignment['published'] = published
    assignment['questions'] = []
    course['assignments'].append(assignment)
    assignjson = open(name.replace("/","_")+".json","w")
    assign = {}
    assign['questions'] = []
    assignjson.write(json.dumps(assign,indent=2))
    assignjson.close()
  with open(course_file,"w") as coursejson:
    coursejson.write(json.dumps(course,indent=2))

'''
given a course name, assignment name and question data
store the question data for the assignment.
CANNOT be used to update question data
'''
def store_questions(course,assignment,questions):
  course_file = course+".json"
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

  for assign in course['assignments']:
    if assign['name'] == assignment:
      qs = []
      for (name,link,pdone) in questions:
        question = {}
        question['name'] = name
        question['link'] = link
        question['percentdone'] = pdone
        qs.append(question) 
      assign['questions'] = qs
  with open(course_file,"w") as coursejson:
    coursejson.write(json.dumps(course,indent=2))

'''
given an assignment name, a question title and the counts of graders
store the counts in assignment_name.json
can be used to update counts
'''
def store_assignment(assignment,question,counts):
  assignment_file = assignment.replace("/","_")+".json"
  f = open(assignment_file)
  if not f:
    err = "Could not find " + course_json + ". Will make"
    logging.error(err)
    print(err)
    assignmnet = {'questions':[]}
  try:
    if f:
      assignment = json.load(f)
  except json.JSONDecodeError:
    err = assignment_file+ " is malformed"
    logging.error(err)
    print(err)
    exit(1)
  f.close()

  found = False
  for q in assignment['questions']:
    if q['name'] == question:
      found = True
      q['counts'] = counts
  if not found:
    assignment['questions'].append({'name':question,'counts':counts})
  with open(assignment_file,"w") as assignmentjson:
    assignmentjson.write(json.dumps(assignment,indent=2))

