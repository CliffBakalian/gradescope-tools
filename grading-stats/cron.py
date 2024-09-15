from utils import *
from update import *
from datetime import datetime 
import shutil

'''
start by setting up a logger to make sure everything runs smoothly
then we setup the driver and login to gradescope. Then get all data
'''

logging.basicConfig(filename='debug.log', level=logging.INFO)
driver = get_driver() 

courses = [("fall24",'822297')]
course_name = courses[0][0]
assignments = ["4954497", "4954543", "4954560", "4954567"]

for assignment_id in assignments:
  now = datetime.now().replace(microsecond=0).isoformat()
  shutil.copy(assignment_id+".json", "history/"+assignment_id+"."+now+".json")
  update_counts(driver,course_name,assignment_id)
