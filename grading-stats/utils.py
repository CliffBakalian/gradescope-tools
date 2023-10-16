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
    #browser.close()
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
    #browser.close()
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
    #browser.close()
    logging.error("check for " + url + " failed due to Selenium")
    logging.error(e)

def write_coursejson(coursejson):
  with open(coursejson['name']+".json","w") as coursefile:
    coursefile.write(json.dumps(coursejson,indent=2))

'''
this will store course info and only course info
if you want to add assignments or graders you will
need to call add_assignment
'''
def store_courses(courses):
  if courses:
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
  coursejson = get_course_json(course)
  for (name,link,published) in assignments:
    assignment = {}
    assignment['name'] = name
    assignment['link'] = link
    assignment['published'] = published
    assignment['questions'] = []
    coursejson['assignments'].append(assignment)

    assignjson = open(link+".json","w")
    assign = {}
    assign['questions'] = []
    assignjson.write(json.dumps(assign,indent=2))
    assignjson.close()
  with open(course+".json","w") as coursefile:
    coursefile.write(json.dumps(coursejson,indent=2))

'''
given a course name, assignment name and question data
store the question data for the assignment.
CANNOT be used to update question data
'''
def store_questions(course,assignment,questions):
  coursejson = get_course_json(course)
  for assign in coursejson['assignments']:
    if assign['name'] == assignment:
      assignjson = get_assignment_json(assign['link'],True)
      qs = []
      for (name,link,pdone) in questions:
        question = {}
        question['name'] = name
        question['link'] = link
        question['percentdone'] = pdone
        qs.append(question) 

        aquestion = {}
        aquestion['name'] = name
        aquestion['link'] = link
        aquestion['counts'] = {}
        assignjson['questions'].append(aquestion)

      with open(assign['link']+".json","w") as assignfile:
        assignfile.write(json.dumps(assignjson,indent=2))
      assign['questions'] = qs
  with open(course+".json","w") as coursefile:
    coursefile.write(json.dumps(coursejson,indent=2))

'''
given an assignment id, a question title and the counts of graders
store the counts in assignment_name.json
can be used to update counts
'''
def store_counts(assignment_id,question,counts):
  assignment = get_assignment_json(assignment_id)
  for q in assignment['questions']:
    if q['name'] == question:
      found = True
      q['counts'] = counts
  with open(assignment_id+".json","w") as assignmentjson:
    assignmentjson.write(json.dumps(assignment,indent=2))

def get_course_json(course):
  course_file=course+".json"
  try:
    f = open(course_file)
  except:
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
  return coursejson

def get_assignment_json(assignment_id,make=False):
  assign_file=assignment_id+".json"
  try:
    f = open(assign_file)
  except:
    if not make:
      err = "Could not find " + assign_file
      logging.error(err)
      print(err)
      exit(1)
    else:
      err = "Could not find " + assign_file + ". Will make."
      logging.error(err)
      print(err)
      return {"questions":[]}
  try:
    assignjson = json.load(f)
  except json.JSONDecodeError:
    err = assign_file+ " is malformed"
    logging.error(err)
    print(err)
    exit(1)
  f.close()
  return assignjson
