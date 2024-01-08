import sys
from utils import get_course_json,get_driver,store_stats_as_csv
from update import *

'''
python shell update course --only-needed
python shell update course --all

python shell --first-time

python shell print course assignment
'''
def main():
  if len(sys.argv) < 2:
    print("missing command line arguments")
    exit(1)
  command = sys.argv[1]
  if command in ['update','--first-time']:
    logging.basicConfig(filename='debug.log', level=logging.INFO)
    driver = get_driver() 

    if command == 'update':
      if len(sys.argv) < 3:
        print("missing command line arguments")
        exit(1)
      course = sys.argv[2]
      update_all = False

      if len(sys.argv) >= 4:
        flag = sys.argv[3] == '--all'

      print('updating course: ' + course)
      update_assignments(driver,course)

      coursejson = get_course_json(course)      
      course_link = coursejson['link']
      course_name = coursejson['name']
      assignments = coursejson['assignments']
      
      # check if published or not to do minimal work
      for assignment in assignments:
        pub = assignment['published']
        if not pub or update_all:
          assign_name = assignment['name'] 
          assign_link = assignment['link'] 
          questions = assignment['questions']
          # check if done grading to do minimal work
          for question in questions:
            pd = question['percentdone']
            if pd != 100 or update_all:
              question_link = question['link']
              question_name = question['name']
              update_counts(driver,course_name,assign_link,question_link)

          # updating the percent done
          update_questions(driver,course_name,assign_name)
    else:
      do_it_all(driver)

  elif command == 'print':
    if len(sys.argv) < 4:
      print("missing command line arguments")
      exit(1)
    course = sys.argv[2]
    assignment_input = sys.argv[3]

    # check if given assignment id or name
    try:
      assignment = int(assignment_input)
      store_stats_as_csv(course,str(assignment))
    except Exception:
      assignment = assignment_input 
      coursejson = get_course_json(course)
      assignments = coursejson['assignments']
      for assign in assignments:
        if assign['name'] == assignment:
          store_stats_as_csv(course,assign['link'])
          break
    
if __name__ == "__main__":
  main()
