from datetime import datetime,timedelta
import csv

MAX_TOKENS = 6
DAYLIGHTS_SAVINGS = datetime(2023,11,5) #CHANGE PER SEMESTER
TZHO = -4 #TimeZoneHourOffset
TZMO = 0  #TimeZoneMinuteOffet

project1 = (("3242355",datetime(2023,9,10,23,59)))
project2 = (("3295642",datetime(2023,9,19,23,59)))
project3 = (("3359767",datetime(2023,10,6,23,59)))
project4 = (("3466121",datetime(2023,10,15,23,59)))
project5 = (("3531724",datetime(2023,10,30,23,59)))
project6 = (("3616438",datetime(2023,11,15,23,59)))
project7 = (("3694062",datetime(2023,11,29,23,59)))
project8 = (("3758720",datetime(2023,12,11,23,59)))
projects = [project1,project2,project3,project4,project5,project6,project7,project8]
weights = {0:.02,1:.05,2:.08,3:.02,4:.08,5:.08,6:.02,7:.05}
pnames=#load from gradescope/file 

'''
load project.exts file and make a hash of
name -> due_date
'''
def load_extensions(course):
  extension_file = open(str(course)+"/"+str(course)+".exts")
  exts = {}
  for line in extension_file:
    info = line.split(",")
    name = info[0]
    time = info[2]
    year = int(time[0:4])
    month = int(time[5:7])
    day = int(time[8:10])
    hour = int(time[11:13])
    minute = int(time[14:16])
    offset_hour = int(time[20:23])
    if time[23] == ":": #formatting is weird
      offset_minutes = int(time[24:26])
    else:
      offset_minutes = int(time[23:25])
    extension = datetime(year,month,day,hour,minute)
    if extension >= DAYLIGHTS_SAVINGS: #fuck daylights saving
      offset_hour += 1 #one is -4, and the other is -5
    extension = extension + timedelta(hours=TZHO - offset_hour,minutes=TZMO-offset_minutes)
    exts[name] = extension 
  return exts

def get_scores_per_tokens(course,user,due_date,extensions):
  try:
    student_file = open(str(course)+"/"+str(user)+"."+str(course))

    token_scores = {}
    for x in range(MAX_TOKENS+1):
      token_scores[x] = 0 
    for line in student_file:
      info = line.split(",")
      score= int(float(info[1].strip()))
      time = info[0]
      year = int(time[0:4])
      month = int(time[5:7])
      day = int(time[8:10])
      hour = int(time[11:13])
      minute = int(time[14:16])
      offset_hour = int(time[19:22])
      if time[23] == ":":
        offset_minutes = int(time[24:26])
      else:
        offset_minutes = int(time[23:25])
      submission_time = datetime(year,month,day,hour,minute)
      if submission_time >= DAYLIGHTS_SAVINGS:
        offset_hour += 1 
      submission_time = submission_time + timedelta(hours=TZHO - offset_hour,minutes=TZMO-offset_minutes)
      
      if user in extensions:
        due_date = extensions[user]

      lateness_secs = (submission_time - due_date).total_seconds() # second difference between duedate and submission time
      late_hours,late_over = divmod(lateness_secs,3600)            # getting the  hours 
      late_minues = divmod(late_over,60)[0]                        # getting the miunes, dropping secondds
      if late_hours < 0:
        token_scores[0] = max(token_scores[0],score)               # if submitted early
      elif late_hours < MAX_TOKENS * 12:                          # if within token time
        token_scores[late_hours//12+1] = max(token_scores[late_hours//12+1],score)      # find maximum score per token
        token_scores[0] = max(token_scores[0],score*(1-.1*(divmod(late_hours,24)[0]+1)))
    return token_scores 
  except:
    token_scores = {}
    for x in range(MAX_TOKENS+1):
      token_scores[x] = 0 
    return token_scores
  
def get_students(course=None):
  students = []
  if course:
    roster = open(course+"/"+course+".cache")
    for line in roster:
      students.append(line.split(",")[0]) 
    return students 
  else:
    roster = open('roster')
    for line in roster:
      students.append(line.strip()) 
    return list(set(students))

TOTAL_TOKENS = 9
def choose(scores):
  # current path, how many tokens used, current score, which project are you proccessing
  def helper(path,scores_left,tokens_used,curr_score,project_idx):
    if scores_left == [] or project_idx >= len(projects):
      return path,curr_score
    res = []
    for x in range(MAX_TOKENS+1):
      new_toks = x + tokens_used
      if new_toks  <= TOTAL_TOKENS:
        score = scores_left[x]
        new_path = path + [(score,x)]
        new_score = curr_score + (score * weights[project_idx])
        scores_remain = scores_left[MAX_TOKENS+1:]
        res.append(helper(new_path,scores_remain,new_toks,new_score,project_idx+1))
    to_return = []
    total_score = 0
    for potential in res:
      path = potential[0]
      score = potential[1]
      if score > total_score:
        total_score = score
        to_return = path
    return to_return,total_score
  return helper([],scores,0,0,0)

'''
need: list of students
need: ["proje_name",datetime(duedate)]
'''
def make_csv():
  out = open('scores.csv','w')
  writer = csv.writer(out)
  header = ["name"]
  results_header = []
  for y in projects:
    for x in range(MAX_TOKENS +1):
      header.append(pnames[y[0]]+":"+str(x)+" tokens")
    results_header.append(pnames[y[0]]+":(score,tokens_used)")

  writer.writerow(header+results_header+["total"])
  out.close()

  out = open('scores.csv','a')
  writer = csv.writer(out)
  students = get_students() #projects[-2][0])
  for x in students:
    row = [x]
    all_scores = []
    for y in projects:
      project = y[0]
      duedate = y[1]
      extensions = load_extensions(project)
      student = x 
      scores = get_scores_per_tokens(project,student,duedate,extensions)
      for z in scores:
        all_scores.append(scores[z])
    projects_chosen,final_score = choose(all_scores)
    writer.writerow(row+all_scores+projects_chosen+[final_score])
      
make_csv()
