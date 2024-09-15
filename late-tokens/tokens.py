from datetime import datetime,timedelta
import csv

TOTAL_TOKENS = 3 # total tokens a student has
MAX_TOKENS = 1 # maximum number of tokens per project

#Daylights savings *S*tart and *E*nd
EDT_S = datetime(2024,3,10)
EDT_E  = datetime(2024,11,3)

#people that submit 3 minutes late (12:02 am we give leeway)
GRACE_PERIOD_MINUTES = 3 

TOKEN_TIME = 24 #is a token 24 hours or 12? or other?

gradescope_mod = True

project1 = (("4029318",datetime(2024,2,13,23,59,59)))
project2 = (("4094462",datetime(2024,2,27,23,59,59)))
project3 = (("4166768",datetime(2024,3,15,23,59,59)))
project4 = (("4237875",datetime(2024,4,9,23,59,59)))
project5 = (("4352300",datetime(2024,4,25,23,59,59)))
project6 = (("4396345",datetime(2024,5,1,23,59,59)))
project7 = (("4406858",datetime(2024,5,9,23,59,59)))
projects = [project1,project2,project3,project4,project5,project6,project7]

# change due dates to GMT
projects = list(map(lambda x: 
            (x[0],x[1]+ timedelta(hours=4,minutes=GRACE_PERIOD_MINUTES)) 
              if EDT_S < x[1] < EDT_E else
                (x[0],x[1]+ timedelta(hours=5,minutes=GRACE_PERIOD_MINUTES)),
            projects))

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
  # the extension line could be for something that is not a dude date change
  for line in extension_file:
    info = line.split(",")
    if info: # if they have 
      name = info[0]
      time = info[2]
      year = int(time[0:4])
      month = int(time[5:7])
      day = int(time[8:10])
      hour = int(time[11:13])
      minute = int(time[14:16])
      offset_hour = int(time[20:23])
      offset_minutes = int(time[23:25])
      seconds = 59
      extension = datetime(year,month,day,hour,minute,seconds)

      # convert to GMT
      extension = extension + timedelta(hours=-offset_hour,
                                        minutes=offset_minutes)
      exts[name] = extension 
  return exts

def get_scores_per_tokens(assignment,user,due_date,extensions):
  flag = False

  token_scores = {}
  for x in range(MAX_TOKENS+1): #from 0,1,2,...MAX_TOKENS
    token_scores[x] = 0 
  try:
    student_file = open(str(assignment)+"/"+str(user)+"."+str(assignment))

    for line in student_file:
      info = line.split(",")
      score= int(float(info[1].strip()))
      time = info[0]
      year = int(time[0:4])
      month = int(time[5:7])
      day = int(time[8:10])
      hour = int(time[11:13])
      minute = int(time[14:16])
      seconds = 59
      offset_hour = int(time[19:22])

      #gradescope doesn't format consistently >:(!!!!!!
      if time[23] == ":":
        offset_minutes = int(time[24:26])
      else:
        offset_minutes = int(time[23:25])

      submission_time = datetime(year,month,day,hour,minute,seconds)

#'''--------------------------------------------------------------------------'''
# we messed up autograder and we should discard all scores made before this time
      if assignment == "709210": 
        cutoff = datetime(2023,10,15,23,59)
        if submission_time < cutoff:
          if flag:
            continue
          else:
            flag = True
#'''-------------------------------------------------------------------------'''

      submission_time = submission_time + timedelta(hours=-offset_hour,
                                                    minutes=offset_minutes)
      
      if user in extensions:
        initdue_date = due_date
        due_date = extensions[user]
      
      # second difference between duedate and submission time
      lateness_secs = (submission_time - due_date).total_seconds() 
      # getting the  hours 
      late_hours,late_over = divmod(lateness_secs,3600)            
      # getting the minutes, dropping seconds
      late_minutes = divmod(late_over,60)[0]                        

      # this is if we dont take late score into gradescope
      if late_hours < 0: # if submitted on time
        '''
        this semester tried to do late penalty in gradescope for projects 1-3
        gradescope due date did not include extensions so it just gave penalty 
        to everyone who submitted after the initial duedate regardless if they
        had an extension. SO here if the user has an extension and this is a
        project 1-3 score, revert the change
        '''
        if user in extensions and assignment not in ["4237875","4352300","4396345","4406858"]:
          if (submission_time > initdue_date):
            score = score/.9  
        
        # take the max of score and new on time score 
        token_scores[0] = max(token_scores[0],score)  

      # if submitted when you can with a token
      # 2 ie. 2 tokens per project, each token 24 hours
      elif late_hours < MAX_TOKENS * TOKEN_TIME:      
        '''
        Again the late penalty already calculated for project 1-3
        in this case though we need to make sure they submitted within 24 hours
        of their due date since some people could be submitting for the GFA
        '''
        if assignment not in ["4237875","4352300","4396345","4406858"]:
          score_with_token = score/.9 #(1-.1*(divmod(late_hours,TOKEN_TIME)[0]+1))
        else:
          score_with_token = score

        # token score at that token time is max of what used to be and new one 
        token_number = late_hours//TOKEN_TIME+1
        token_scores[token_number] = max(token_scores[token_number],
                                                     score_with_token) 
        
        # now calculate score with penalty
        late_score = score
        if assignment in ["4237875","4352300","4396345","4406858"]:
          late_score = score*.9 #*(1-.1*(divmod(late_hours,24)[0]+1))

        # score with 0 tokens is now what was there and score with late penalty
        token_scores[0] = max(token_scores[0],late_score)

  except Exception as ex:
    print("ERROR WITH TOKENS- Assignment: " + str(assignment) + 
          "\t user: " + str(user))
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
def make_csv(students,projects):
  out = open('scores.csv','w')
  writer = csv.writer(out)
  header = ["name","SID"]
  results_header = []
  for y in projects:
    for x in range(MAX_TOKENS +1):
      header.append(pnames[y[0]]+":"+str(x)+" tokens")
    results_header.append(pnames[y[0]]+":(score,tokens_used)")

  writer.writerow(header+results_header+["total"])
  out.close()

  out = open('scores.csv','a')
  writer = csv.writer(out)
  for x in students:
    x = x.split(",")
    row = [x[0],x[1]]
    all_scores = []
    for y in projects:
      project = y[0]
      duedate = y[1]
      extensions = load_extensions(project)
      student = x[0]
      scores = get_scores_per_tokens(project,student,duedate,extensions)
      for z in scores:
        all_scores.append(scores[z])
    projects_chosen,final_score = choose(all_scores)
    writer.writerow(row+all_scores+projects_chosen+[final_score])
      
students = get_students() #projects[-2][0])
make_csv(students,projects)
