package gradescope

import (
  "strings"
  "strconv"
  "log"
  "fmt"
  "encoding/json"
  "io/ioutil"
)

//get the states for an assignment
func GetStats(semester Semester, courseID string, assignmentID string)(map[string]map[string]int, int){
  stats := make(map[string]map[string]int)
  for _,course := range semester.Courses{
    if course.Link == courseID{
      assignments := course.Assignments
      for _,assignment := range assignments{
        if assignment.Link == assignmentID{
          questions := assignment.Questions
          for _,question := range questions{
            graders := question.Graded
            tas := make(map[string]int)
            for _,grader := range graders{
              tas[grader.Grader] = grader.Count 
            }
            stats[question.Name] = tas
          }
          return stats,-1
        }
      }
      //assignment not found
      return stats,1
    }
  }
  //course not found
  return stats,2
}

func updateAssignStats(semester Semester,courseID string, assignmentID string,questions []Question)(map[string]map[string]int,int){
  stats := make(map[string]map[string]int)
  for _,course := range semester.Courses{
    if course.Link == courseID{
      assignments := course.Assignments
      for _,assignment := range assignments{
        if assignment.Link == assignmentID{
          assignment.Questions = questions
          for _,question := range questions{
            graders := question.Graded
            tas := make(map[string]int)
            for _,grader := range graders{
              tas[grader.Grader] = grader.Count 
            }
            stats[question.Name] = tas
          }
          writeCourses(semester)
          return stats,-1
        }
      }
      return stats,1
    }
  }
  return stats,2
}

func updateCourse(app App,semester Semester, courseID string){
  //make the new course struct
  name := app.scrapeCourseName(courseID)
  link := courseID
  course := Course{
    Name: name,
    Assignments: []Assignment{},
    Link: link,
  }

  //buid the course's assignments
  course.Assignments = buildAssignments(app,link)
  semester.Courses = append(semester.Courses,course)
  writeCourses(semester)
}

func updateAssignment(app App, semester Semester, courseID string, assignmentID string){
  //make the assignment struct
  name,submissions := app.scrapeAssignmentName(courseID,assignmentID)
  link := assignmentID
  assignment := Assignment{
    Name: name,
    Submissions: submissions,
    Link: link,
    Questions: []Question{},
  }
  //build the rest of the assignment
  assignment.Questions = buildQuestions(app,courseID,assignmentID)

  for _,course := range semester.Courses{
    if course.Link == courseID{
      course.Assignments = append(course.Assignments,assignment)
      writeCourses(semester)
      return
    }
  }

  //the course does not exist
  name = app.scrapeCourseName(courseID)
  link = courseID
  course := Course{
    Name: name,
    Assignments: []Assignment{assignment},
    Link: link,
  }
  semester.Courses = append(semester.Courses, course)
  writeCourses(semester)
}

//parse Everything
func buildSemester(app App)Semester{
  classes := []Course{}
  courses := app.scrapeCourses()
  for l,c := range courses{
    course := Course{
      Name: c,
      Assignments: []Assignment{},
      Link: l,
    }
    course.Assignments = buildAssignments(app,l)
    classes = append(classes,course)
  }
  return Semester{Courses: classes}
}

//get the assignment info
func buildAssignments(app App, courseID string)[]Assignment{
  assignments := []Assignment{}
  links,subs := app.scrapeAssignments(courseID)
  for l,a := range links{
    assignment := Assignment{
      Name: a,
      Submissions: subs[l],
      Link: l,
      Questions: []Question{},
    }
    assignment.Questions = buildQuestions(app,courseID,l)
    assignments = append(assignments,assignment)
  }
  return assignments
}

//get the question info
func buildQuestions(app App, courseID string, assignmentID string)[]Question{
  questions := []Question{}
  problems := app.scrapeQuestions(courseID,assignmentID)
  for q,l := range problems{
    question := Question{
      Name: q,
      Link: l,
      Graded: []Graders{},
    }
    question.Graded = buildGraded(app,courseID,l)
    questions = append(questions,question)
  }
  return questions
}

// get the grader info
func buildGraded(app App, courseID string, questionID string)[]Graders{
  tas := []Graders{} 
  graders := app.scrapeGraders(courseID,questionID)
  for g,c := range graders{
    grader := Graders{
      Grader: g,
      Count: c,
    }
    tas = append(tas,grader)
  }
  return tas
}

// returns how many digits in the integer. Used for pretty formatting
func countDigits(i int)int{
  count := 0
  for i != 0 {
    i /= 10
    count = count + 1
  }
  return count
}

//pretty prints the stats
func print_stats(graders []string,stats map[string]map[string]int)string{
  //get question names
  fmt.Println(graders)
  max_question_len := 0
  questions := make([]string, len(stats))
  i := 0
  for k := range stats{
      questions[i] = k
      lenk := len(k)
      if lenk> max_question_len{
        max_question_len = lenk
      }
      i++
  }

  spacing := 1
  divider := "|"
  divlen := len(divider)
  rendered := "\n"
  //start making the header
  rendered = rendered + strings.Repeat(" ",max_question_len+spacing+divlen)

  //get grader names and lengths to render nicely
  name_lengths := make([]int, len(graders))
  for index,grader := range graders{
    name_lengths[index] = len(grader)
    //make the header 
    rendered = rendered + strings.Repeat(" ",spacing) + grader + strings.Repeat(" ",spacing) + divider
  }
  rendered = rendered + "\n"
  //make each line
  //maybe overly-complicated. Idk if maps have order
  for _,q:= range questions{
    //write the quesetion
    line := q + strings.Repeat(" ",max_question_len+spacing-len(q)) + divider
    //write ech graders count for the question
    grader_seg := ""
    for i,g := range graders{
      grader_seg = grader_seg + strings.Repeat(" ",spacing)
      if count,ok := stats[q][g];ok{
        grader_seg = grader_seg + strings.Repeat(" ",name_lengths[i]-countDigits(count))+strconv.Itoa(count)+strings.Repeat(" ",spacing) + divider
      }else{
        grader_seg = grader_seg + strings.Repeat(" ",name_lengths[i])+strings.Repeat(" ",spacing) + divider
      }
    }
    line = line + grader_seg + "\n"
    rendered = rendered + line
  }
  return rendered
}

func write_stats(courseID string, assignID string,semester Semester   ){
  for _,course := range semester.Courses{
    fmt.Println(course.Link)
    if course.Link == courseID{
      assignments := course.Assignments
      for _,assignment := range assignments{
        fmt.Println(assignment.Link)
        if assignment.Link == assignID{
          res,err := json.Marshal(assignment)
          if err != nil {
            log.Fatal(err)
          }

          err = ioutil.WriteFile(assignID+".json", res, 0644)
          if err != nil {
            log.Fatal(err)
          }
        }
      }
    }
  }
}
