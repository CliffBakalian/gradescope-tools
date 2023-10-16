from utils import * 
from scraper import *

'''
this causes my laptop to freeze up. Haven't tried on big boi
'''
def do_it_all(driver):
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


'''
given a course, will synchronize all gradescope assignments with the local 
file.
This can be used for update since previous assignment data will not be touched.

edge case: renaming an assignment
'''
def update_assignments(driver,course):
  course = get_course_json(course)
  link = course['link']
  assignments = scrapeAssignments(driver,link)
  local = [x['name'] for x in course['assignments']]
  for (name,link,pub) in assignments:
    if name not in local:
      assignment = {}
      assignment['name'] = name
      assignment['link'] = link
      assignment['published'] = pub
      assignment['questions'] = []
      course['assignments'].append(assignment)
  write_coursejson(course)

'''
given a course, and an optional assignment, will update the question
information.
If no assignment is given, update all assignmnet questions
This is used for updating because it will overwrite all question information
'''
def update_questions(driver,course,assignment=None):
  course = get_course_json(course)
  course_link = course['link']
  for assign in course['assignments']:
    if not assignment or assign['name'] == assignment:
      alink = assign['link']
      questions = scrapeQuestions(driver,course_link,alink)
      store_questions(course['name'],assign['name'],questions)

'''
given a course, and assignment_id and a question, update the count of 
the question. The count is a dictionary of graders-> how many they graded.
If no question is given, get the count for all questions in the assignment
This is used for updating since all counts will be recalculated
'''
def update_counts(driver,course,assignment_id,question_id=None):
  assign = get_assignment_json(assignment_id)
  coursejson = get_course_json(course)
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
