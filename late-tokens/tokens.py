from datetime import datetime,timedelta
import csv

MAX_TOKENS = 1
DAYLIGHTS_SAVINGS = datetime(2024,3,10)
TZHO = -5 #TimeZoneHourOffset
TZMO = 0  #TimeZoneMinuteOffet
TOKEN_TIME = 24 #is atoken 24 hours or 12? or other?

gradescope_mod = True

project1 = (("4029318",datetime(2024,2,13,23,59)))
project2 = (("4094462",datetime(2024,2,27,23,59)))
project3 = (("4166768",datetime(2024,3,15,23,59)))
project4 = (("4237875",datetime(2024,4,9,23,59)))
project5 = (("4352300",datetime(2024,4,25,23,59)))
project6 = (("4396345",datetime(2024,5,1,23,59)))
project7 = (("4406858",datetime(2024,5,9,23,59)))
projects = [project1,project2,project3,project4,project5,project6,project7]
weights = {0:.03,
           1:.05,
           2:.08,
           3:.08,
           4:.08,
           5:.03,
           6:.05}

pnames={"4029318":"project-1",
        "4094462":"project-2",
        "4166768":"project-3",
        "4237875":"project-4",
        "4352300":"project-5",
        "4396345":"project-6",
        "4406858":"project-7",}

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
  flag = False
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
      if course == "709210":
        cutoff = datetime(2023,10,15,23,59)
        if submission_time < cutoff:
          if flag:
            continue
          else:
            flag = True
      if submission_time >= DAYLIGHTS_SAVINGS:
        offset_hour -= 1 
      submission_time = submission_time + timedelta(hours=TZHO - offset_hour,minutes=TZMO-offset_minutes)
      
      if user in extensions:
        initdue_date = due_date
        due_date = extensions[user]

      lateness_secs = (submission_time - due_date).total_seconds() # second difference between duedate and submission time
      late_hours,late_over = divmod(lateness_secs,3600)            # getting the  hours 
      late_minues = divmod(late_over,60)[0]                        # getting the miunes, dropping secondds
      # this is if we dont take late score into gradescope
      '''
      if late_hours < 0:
        token_scores[0] = max(token_scores[0],score)               # if submitted early
      elif late_hours < MAX_TOKENS * 24:                          # if within token time
        token_scores[late_hours//24+1] = max(token_scores[late_hours//24+1],score/.9)      # find maximum score per token
        token_scores[0] = max(token_scores[0],score*(1-.1*(divmod(late_hours,24)[0]+1)))
      '''
      if late_hours < 0: # if submitted on time
        if user in extensions and course not in ["4237875","4352300","4396345","4406858"]:
          if (submission_time - initdue_date).total_seconds() > 180:
            initscore = score
            score = score/.9  
            print("I submitted " + str(pnames[course]) + "on time with inital: " + str(initscore) + "\tmodified:" + str(score))
        token_scores[0] = max(token_scores[0],score)  # take the max of score and new on time score 
      elif late_hours < MAX_TOKENS * TOKEN_TIME:      # if submitted when you can with a token
                                                      # 2 ie. 2 tokens per project, each token 24 hours
        print("submitted time: " + str(time))
        print("Due Date: " + str(time))
        print("Late hours: " + str(late_hours))
        print("Late Minutes: " + str(late_minues))
        score_with_token = score

        if gradescope_mod and course not in ["4237875","4352300","4396345","4406858"]:
          score_with_token = score/(1-.1*(divmod(late_hours,24)[0]+1))
        # token score at that token time is max of what used to be and new one 
        token_scores[late_hours//TOKEN_TIME+1] = max(token_scores[late_hours//TOKEN_TIME+1],score_with_token) 

        late_score = score
        if not gradescope_mod or course in ["4237875","4352300","4396345","4406858"]:
          late_score = score*(1-.1*(divmod(late_hours,24)[0]+1))

        # score with 0 tokens is now what was there and score with late penalty
        token_scores[0] = max(token_scores[0],late_score)
        print("I submitted " + str(pnames[course]) + " late with score " + str(score_with_token) + " and late score of " + str(late_score))

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
    roster = open('roster.csv')
    for line in roster:
      students.append(line.strip()) 
    return list(set(students))

TOTAL_TOKENS = 3
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
  students = ['Edna Adissu'] #get_students() #projects[-2][0])
  for x in students:
    row = [x]
    all_scores = []
    for y in projects:
      project = y[0]
      duedate = y[1]
      extensions = load_extensions(project)
      student = x 
      scores = get_scores_per_tokens(project,student,duedate,extensions)
      print(scores)
      for z in scores:
        all_scores.append(scores[z])
    projects_chosen,final_score = choose(all_scores)
    writer.writerow(row+all_scores+projects_chosen+[final_score])
      
make_csv()
