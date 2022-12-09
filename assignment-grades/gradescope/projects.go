package gradescope

import (
  "io"
  "log"
  "os"
  "encoding/csv"
  "regexp"
  "strconv"
  "math"
)

type Time struct {
  hour int8
  minute int8
  seconds int8
}

type Date struct {
  year uint16
  month int8
  day int8
}

//store alternative scores with tokens
type AltScore struct{
  score float32
  tokens int
}

type Assignment struct {
  name string
  points float32
  score float32
  percent float32
  late Time
  duedate Date
  link string
  assigntype string
  alternative []AltScore
}

type Student struct {
  lname string
  fname string
  uid string
  email string
  section string
  assignments = []Assignment
}

const (
  max_tokens = 5
  project_info_file = "projects.csv"
)

//Go though file that stores project data and get the link on gradescope and 
//the due date for the project
func getProjectData(filename string) (map[string]string,map[string]Date,map[string]float32){
  f, err := os.Open(filename)
  if err != nil {
    log.Fatal("Failed to open csv file")
  }

  defer f.Close()

  links := make([string]string)
  duedates := make([string]Date)
  percents := make([string]float32)
  csvReader := csv.NewReader(f)
  csvReader.FieldsPerRecord = -1

  for {
    project, err := csvReader.Read()
    //no more students to go through
    if err == io.EOF {
      break
    }
    links[project[0]] = project[1]
    y = project[2]
    m = project[1]
    d = project[0]
    duedates[project[0]] = Date{
      year:y,
      month:m,
      day:d,
    }
  }
  return links,duedates,percents   
}

//optimze student's score with tokens on projects
func optimize(assignments []Assignment, percents [string]float32) []Assignment{
  projects = []Assignments  
  scores = map[string][]AltScore
  //add assignment to projects
  for idx,assign := assignments{
    if assign.assigntype == "Project"{
      projects = append(projects,assign)
      scores[assign.name] = assign.alternative
    }
  }

  //for each project there are 3^n scores for all projects per student. This is an overcount. 
  //score with 0 tokesn, score with 1 token, score with 2 tokens
  
  //possible = [(count,p1_score,p2_score,...pn_score)]
  possible = make([][]float32)
  //add at least one project to possible
  p0alts = score[projects[0].name]
  for alt:= range p0alts{
    p0 := make([]float32)
    p0 = append(alt.tokens,alt.score)
    possible = append(possible,p0)
  }
  
  //use to store new lists
  temp := make([][]float32)

  //now start adding the other projects
  for p := range projects[1:]{
    for lst:= range possible{
      alts = score[p.name]
      for alt:= range alts{
        //add the new project to the already existing lists
        count:= lst[0]
        if alt.tokens + count <= max_tokens {
          // add the score to the list
          // add this new score list to temp
          temp = append(temp,append(lst,alt.score))
        }
      }
      //temp now has added say 3 values 0 tokens, 1 tokens and 2 tokens
    }
    //have possible now just be all the new added lists, and only the newly added lists
    possible = temp
    temp = make([][]float32)
  }

  //now get max list
  max = 0.0
  for idx,scores := range possible{
    score := sum(scores[1:]) 
    if score > max{
      max = score
    }
  }
  //now change assignment to return
  for idx,assign := range assignments{
    assign.score = max[idx]
  }
  return assignments
}

//Go through grade csv file and make a list of Students
func parseGradesFile(filename string) []Student{
  //links map project name to link on gradescope.com
  //duedates map project name to starting date
  //both are gotten from other file
  links,duedates,percents = getProjectData(project_info_file)
  f, err := os.Open(filename)
  if err != nil {
    log.Fatal("Failed to open csv file")
  }

  defer f.Close()

  students := make([]Student)

  csvReader := csv.NewReader(f)
  csvReader.FieldsPerRecord = -1

  //get the time then date the assignmnet was submitted
  subtime_re := regexp.MustCompile(`(\d\d):(\d\d):(\d\d)`)
  subdate_re := regexp.MustCompile(`(\d{4})-(\d{2})-(\d{2})`)
  project_re := regexp.MustCompile(`Project \d+[a-z]?`)
  atype_re := regexp.MustCompile(`(Project|Lecture Quiz|Quiz|Exam)`)
  /*
  maxpoints_re := regexp.MustCompile(`- Max Points`)
  subtime := regexp.MustCompile(`- Submission Time`)
  lateness := regexp.MustCompile(`- Lateness (H:M:S)`)
  */

  header,err := csvReader.Read()

  //each assign has score, max points, submission time and lateness
  //there is also a total lateness column, first name, latename, SID, email
  //and section colum. Remove those and divide by 4 to get number of assigns
  num_assigns := (len(header)-6)/4

  //if login failed, then len < 2
  if err != nil || len(record) <2{
    f.Close()
    os.Remove(filename)
    log.Fatalln("Error parsing row. Make sure credentials correct",err)
  }

  //used to optimize score
  optimze := false
  for {
    student, err := csvReader.Read()
    //no more students to go through
    if err == io.EOF {
      break
    }

    firstName := student[0]
    lastName := student[1]
    userid := student[2]
    email := student[3]
    section := student[4]
    assignments := make([]Assignments)

    // starting getting info for each assignmet
    offset_idx := 5 //starting after first name, last name, sid, email, sections
    assign_num := 0
    assign_idx := (assign_num*4)+offset_idx
     
    for assign_num < num_assigns{
      //get info for assignment
      name := header[assign_idx] 
      assigntype := atype_re.FindStringSubmatch(name)
      //eg. ads check or other
      if assigntype == nil{
        assign_num += 1
        assign_idx = (assign_num*4)+offset_idx
        continue 
      }
      duedate := duedates[name]
      score := student[assign_idx]
      points := student[assign_idx +1] //name, max points, submission time, late
      subdate := subdate_re.FindStringSubmatch(student[assign_idx + 2])
      late := subtime_re.FindStringSubmatch(student[assign_idx + 3])
      alts := make([]AltScore) 

      latetime := Time{
          hour: int8(func(x int,y error)int{return x}(strconv.Atoi(late[1]))),
          minute: int8(func(x int,y error)int{return x}(strconv.Atoi(late[2]))),
          seconds: int8(func(x int,y error)int{return x}(strconv.Atoi(late[3]))),
      }
      //if project and submission was late
      if asigntype == "Project" && (latetime.hour>0 ||latetime.minute >0|| latetime.seconds>0){
        //TODO look at submission scores for assignment
        // make list of Altscores
        //mark as someone to optimize
        /*
        scraper algo:
          input: NAME, COURSE, ASSIGNMENT
          go to gradescope.com/courses/COURSE/assignments/ASSIGNMENT/review_grades
          find the NAME and go to that page
          find the submission history
          get all submissions times, date, and score
          get max score before deadline,
          get max score after deadline within 12 hours
          get max score after deadline within 24 hours
          add all scores and token counts to AltScore
          add Altscore list to alts
        */
        //NOTE
          /*
            - if score with 0 tokens is greatest, just go with that
            -  score with 0 tokens is either before the deadline or with penalty
            so only add these to alts if applicable
          */
      }
      //make assignment
      assign := Assignment{
        name: name,
        points: points,
        score: score,
        late: latetime,
        duedate: duedate,
        link: links[name],
        assigntype: assigntype,
        alternative: alts,
      }
      //add to assignment lists
      assignments = append(assign, assignments)

      //update things for the loop guard
      assign_num += 1
      assign_idx = (assign_num*4)+offset_idx
    }
    
    if optimize{
      assignments = optimze(assignments,percents) 
      optimize = false
    }
    //make student
    student := Student{
      fname: firstName,
      lanem: lastName,
      uid: userid,
      email: email,
      section: section, 
      assignments: assignments,
    }
    //add student to list
    students = append(student, students)
  }
  return students 
}
