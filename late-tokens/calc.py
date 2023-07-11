import csv
import re

from datetime import datetime, timedelta
from math import ceil

from scraper import last_sub_cache, get_all_submissions, 
from utils import get_driver()


EDT = datetime(2023,3,12)


TOKENS_ALLOWED = 3
MAX_TOKEN_PER_ASSIGNMENT = -1


def getHeaders(f):
  ret = {}
  with open(f) as grades:
    reader = csv.reader(grades)
    headers = next(reader)
  for idx,header in enumerate(headers):
    ret[header] = idx 
  return ret

# get the number of tokens for the latest submission.
def latestTokens(lateness):
  late_re = re.compile("(\d+):(\d+):(\d+)")
  matched = re.search(late_re,lateness)
  if not matched:
    print("Could not find lateness")
    return None 
  hours = int(matched.group(1))
  minutes = int(matched.group(2))
  if hours == 0 and minutes < 6:
    return 0
  if minutes > 0:
    hours = hours + 1
  return ceil(hours/12)

# get the number of tokens from submission times
def submissionTokens(raw_time,assign_info):
  due_date = assign_info['due']
  late_date = assign_info['late']
  time_re = re.compile("(\d{4})-(\d{2})-(\d{2})( |T)(\d+):(\d{2}):(\d{2})")
  matched = re.search(time_re,raw_time)
  if not matched:
    return None

  # time in yyyy-mm-ddThh:mm:ss-HH:MM'
  # where -/+HH:MM if offset from z time
  year = int(matched.group(1))
  month= int(matched.group(2))
  day  = int(matched.group(3))
  hour = int(matched.group(5))
  mins = int(matched.group(6))

  #idk why this is -7/-8 and not -4, the timezone I am in
  #also gradescope has inconsistent time foramtting
  #time in yyyy-mm-ddThh:mm:ss -HHMM'
  if raw_time[-6] == '-' or raw_time[-6] == '+':
    offset = int(raw_time[-6:-3])+4 # est = +4
  else:
    offset = int(raw_time[-5:-2])+4 # est = +4
  time = datetime(year,month,day,hour,mins,59)

  #freaking edt vs est making things terrible as per usual
  if time < EDT:
    offset += 1

  time = time - timedelta(hours=offset)
  '''
  poss_ext = get_extension(name,projects)
  if poss_ext:
    due_date = poss_ext
  '''
  hours_diff = ((time-due_date).total_seconds())/3600

  if hours_diff < 0.05: #before due date with 3 minute grace period
    return 0
  return 1 + int(int(hours_diff)/12)

'''
given [(time,score)]
given {'due':DateTime,'late':DateTime}
return {num_tokens:score}
'''
def getMaxPerToken(history,assign_info):
  ret = {}
  for time,score in history:
    score = int(float(score))
    tokens = submissionTokens(time,assign_info)
    if tokens not in ret or ret[tokens] < score:
        ret[tokens] = score

  #max of on time vs late with penalty
  no_tokens = []
  for tokens,score in ret.items():
    no_tokens.append(score* (1-(ceil(tokens/2)*.1))) #PER DAY PENALTY = .1
  ret[0] = max(no_tokens)
  return ret

'''
The point of this program. 
given a row from the gradescope grades csv
given headers for that csv file
given list of assignments that need token cacls
return updated scores for each of these assignments
'''
def get_token_info(row,headers,assignments):
  total_tokens = 0
  scores = {}
  # get number of tokens used total. can prune here
  for assignment in assignments:
    score = row[headers[assignment]]
    # this is just how gradescope formats the header
    lateness = row[headers[assignment+" - Lateness (H:M:S)"]]
    tokens_used = latestTokens(str(lateness))
    if MAX_TOKEN_PER_ASSIGNMENT > -1 and tokens_used <= MAX_TOKEN_PER_ASSIGNMENT:
      # submitted for gfa.
      # will need to check so just add to total tokens to flag
      scores[assignment] = 0 
      total_tokens += TOKENS_ALLOWED
    else:
      scores[assignment] = score
    total_tokens += tokens_used
  if total_tokens <= TOKENS_ALLOWED: #prune if did not use extra tokens
   return scores 

  #start looking at past histories
  histories = {}
  for assignment in assignments:
    aid = assign_ids[assignment]
    sub_cache = list_to_hash(last_sub_cache(aid))
    name = row[headers['First Name']] + " " + row[headers['Last Name']] 
    if name in sub_cache:
      user = sub_cache[name]
      full_history = get_all_submissions(driver,COURSE_ID,aid,name,user)
      ret = getMaxPerToken(full_history,ASSIGN_INFO[assignment])
      histories[assignment] = ret
  grades = min_max_grades(histories,ASSIGN_INFO)
  return grades

'''
get the column of student info for elms.
should just be SID since everything else needs to be a lookup
from the elms template. People have different names and emails 
from gradescope and elms
'''
def get_student_info(row,headers):
  return [row[headers['SID']]]

'''
for things that don't need tokens, pretty easy, 
just copy the score over.
'''
def get_non_token_info(row,headers,assignments):
  ret = []
  for assignment in assignments:
    ret.append(row[headers[assignment]])
  return ret

def list_to_hash(lst):
  ret = {}
  for (name,link) in lst:
    ret[name] = link
  return ret

'''
given {assignment:{token_number:score}}}
given {assignmnet:{late:datetime, due:datetime,weight:float}}
maximize score and token use
return {assignment:score}
'''

TOKENS_ALLOWED = 3
MAX_TOKEN_PER_ASSIGNMENT = -1
def min_max_grades(histories,assign_info):
  ret = {}
  assigns_to_check = []
  for name,scores in histories.items():
    if max(scores.keys()) == 0: #if they used only 0 tokens
      ret[name] = max(scores.values())
    else:
      assigns_to_check.append(name)
  _,path = bfs(assigns_to_check,assigns_to_check,histories,assign_info,TOKENS_ALLOWED,{}) 
  final_score = -1
  for assignment,tokens in path.items():
    ret[assignment] = histories[assignment][tokens]
  return ret

'''
given [assignments]
given {assignment:{token_number:score}}}
given {assignmnet:{late:datetime, due:datetime,weight:float}}
given tokens (left)
given score
given {assignment: tokens}
this is a bfs tree problem. start with 0 tokens, then x token per project
return (score,{assignment: tokens})
'''
def bfs(assignments,visited,histories,assign_info,tokens,path):
  ## calculater the path on the tree
  if tokens <= 0 or visited == []:
    score = 0
    for assignment in assignments:
      weight = assign_info[assignment]['weight']
      if assignment in path:
        score += histories[assignment][path[assignment]] * weight
      else:
        score += histories[assignment][0] * weight
    return score,path
        
  values = []
  for assignment in visited:
    weight = assign_info[assignment]['weight']
    for toks,score in histories[assignment].items():
      new_assigns = list(set(visited) - set([assignment]))
      new_toks = tokens - toks
      if new_toks >= 0:
        new_path = path.copy()
        new_path[assignment] = toks
        res = bfs(assignments,new_assigns,histories,assign_info,new_toks,new_path)
        values.append(res)
      else:
        score = 0
        for assignment in assignments:
          weight = assign_info[assignment]['weight']
          if assignment in path:
            score += histories[assignment][path[assignment]] * weight
          else:
            score += histories[assignment][0] * weight
        return score,path
  ret = {}
  final_score = -1
  for score,path in values:
    if score > final_score:
      final_score = score
      ret = path
  return final_score,ret


def start(input_file):
  headers = getHeaders(input_file)
  outfile = open("final.csv",'w')
  with open(input_file) as raw_grades:
    reader = csv.reader(raw_grades)
    _ = next(reader)

    outfile.write(",".join(["SID"] + non_token + token_assignments) + "\n")
    for row in reader:
      sinfo = (get_student_info(row,headers))
      ntok = (get_non_token_info(row,headers,non_token))
      toks = (get_token_info(row,headers,token_assignments))
      tok_list = []
      for assignment in token_assignments:
        if assignment in toks:
          tok_list.append(str(toks[assignment]))
        else:
          tok_list.append("0")
      row = ",".join(sinfo + ntok + tok_list) + "\n"
      outfile.write(row)

test_file = "330summer.csv"
driver = get_driver()
start(test_file)
