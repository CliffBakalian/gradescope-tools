from utils import *
from update import *
'''
start by setting up a logger to make sure everything runs smoothly
then we setup the driver and login to gradescope. Then get all data
'''
logging.basicConfig(filename='debug.log', level=logging.INFO)
driver = get_driver() 

def first_time():
  do_it_all(driver)


#courses = scrapeCourses(driver)
#store_courses(courses)

courses = [("fall24",'822297')]
store_courses(courses)
course_name = courses[0][0]
course_id = courses[0][1]

#for course in courses:
#  graders = scrapeGraders(driver,course[1])
#  store_graders(course[0],graders)

assignments = scrapeAssignments(driver,course_id)

# will store assignment to course_name.json and 
# will make an assignment_id.json to store grading stats
# run once to setup information or to wipe all assignments data 
store_assignments(course_name,assignments)

update_assignments(driver,course_name)

for assignment_name,assignment_id,published in assignments:
  iassignments = ["5218298", "5218472", "5218475","5218499"]
  if assignment_id in iassignments: 
    questions = scrapeQuestions(driver,course_id,assignment_id)

    store_questions(course_name,assignment_name,questions)
    '''
    for question_name,question_id,_ in questions:
      counts,points = scrapeCount(driver,course_id,question_id)
      store_counts(assignment_id,question_name,counts)
      store_points(assignment_id,question_name,points)
    '''
driver.quit()

def examples():
# get a [(course_name, course_id)]
# driver -> (string,string) tuple list
# only need to run once per semester
  courses = scrapeCourses(driver)

  # will write the course_name.json file for each course
  # again, onlt need to run once per semester
  store_courses(courses)

  # get a [grader]
  # driver,course_id -> string list
  # onlt need to run once a semester 
  graders = scrapeGraders(driver,course_id)

  # will write the graders to course_name.json file
  # again, onlt need to run once per semester
  store_graders(course_name,graders)


  # get a [(assignment_name, assignment_id, published?)]
  # driver,course_id-> (string, string,boolean) tuple list
  assignments = scrapeAssignments(driver,course_id)

  # will store assignment to course_name.json and 
  # will make an assignment_id.json to store grading stats
  # run once to setup information or to wipe all assignments data 
  store_assignments(course_name,assignments)

  # will get all assignment names from gradescope and update 
  # course_name.json and assignment_id.json (making this file if needed)
  # run everytime a new assignment is made
  update_assignments(driver,course_name)
  
  # get a [(qustion_name,question_id,percent_graded)]
  # driver,course_id,assignment_id -> (string,string,string) tuple list
  # reallt only need to run once assignment is made 
  # unless assignment outline is modified
  questions = scrapeQuestions(driver,course_id,assignment_id)

  # stores the question date in course_name.json and information in 
  # assignment_id.json
  # run once to setup information or to wipe all question data for all questions
  store_questions(coure_name,assignment_name,qustions)

  # will get all questions names from gradescope and update 
  # assignment_id.json 
  update_questions(driver,course_name,assignment_name)

  # will store the question data in assignment_id.json
  store_questions(course_name,assignment_name,questions)

  # get a ({grader:count},{grader:points given}) tuple 
  # driver,course_id,question_id -> {string:int} dict
  counts,points = scrapeCount(driver,course_id,question_id)

  # will get how many questions people graded on gradescope and store this
  # information in assignment_id.json
  # run this every so ofter to see updates on who graded what
  update_counts(driver,course_name,assignment_id,qusetion_id)

  # if you wanted to write to file the above 
  # (but update_counts already does this)
  store_counts(assignment_id,question_name,counts)


  # takes the assignment_id.json file and makes a csv file with
  # graders as columsn, and questions as rows. 
  # graders are found in course_name.json so make sure names match up
  store_stats_as_csv(course_name,assignment_id)

