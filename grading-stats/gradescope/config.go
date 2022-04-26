package gradescope

import (
  "encoding/json"
  "encoding/csv"
  "errors"
  "io/ioutil"
  "io"
  "os"
  "log"
)

const (
  assignmentFile = ".assignments.json"
  graderFile = ".graders.csv"
)

type Semester struct{
  Courses []Course `json:courses`
}

type Course struct{
  Name string `json:name`
  Assignments []Assignment `json:assignment`
  Link string `json:link`
}

//Assignments have a name, number of submissions, a link
type Assignment struct{
  Name string `json:name`
  Submissions int `json:submissions`
  Link string `json:link`
  Questions []Question `json:question`
}

//Assignments are made of questions with names and grading info
type Question struct{
  Name string `json:name`
  Link string `json:link`
  Graded []Graders `json:graded`
}

//How much each grader graded the question 
type Graders struct{
  Grader string `json:grader`
  Count int  `json:count`
}

// read from json
func readCourses() (Semester,error){
  jsonFile, err := os.Open(assignmentFile)
  if err != nil {
    log.Println("Cannot load file. ", err)
    log.Println("Creating file. ")
    os.Create(assignmentFile)
    return Semester{Courses: []Course{}},errors.New("Empty")
  }
  defer jsonFile.Close()
  
  bytearr,_ := ioutil.ReadAll(jsonFile)
  var semester Semester
  err = json.Unmarshal(bytearr, &semester)
  if err != nil{
    log.Println("Error parson json. ",err)
    log.Println("Ignoring Contents")
    return Semester{Courses: []Course{}},errors.New("Empty")
  }
  return semester,nil
}

// write to json
func writeCourses(semester Semester){
  out, err := os.Create(assignmentFile)
  if err != nil {
    log.Fatalln("Could not create file. ",err)
  }
  defer out.Close()

  b, err := json.Marshal(semester)
  if err != nil {
    log.Fatalln("Failed to marshal json. ",err)
  }
  _,err = out.Write(b)
  if err != nil {
    log.Fatalln("Failed to write file. ", err)
  }
}

// read graders from grader file
func readTAs(course string) ([]string, error){
  f, err := os.Open(graderFile)
  if err != nil{
    log.Println("Failed to open grader file")
    return nil,err
  }

  defer f.Close()

  csvReader := csv.NewReader(f)
  csvReader.FieldsPerRecord = -1
  var tas = []string{}
  for{
    record, err := csvReader.Read()
    if err == io.EOF{
      break
    }
    if err != nil {
      f.Close()
      return tas,err
    }
    if course != "" && record[1] == course{  
      tas= append(tas,record[0])
    }
  }
  return tas,nil
}

//write tas to the end. I don't want to rewrite because this file should be manually created. This is only for the case that the file got corrupted. 
func writeTAs(tas map[string]map[string]string,){
  f,err := os.OpenFile(graderFile,os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
  if err != nil {
    log.Fatal(err)
  }
  for ta,course:= range tas{
    for link,name := range course{
      if _, err := f.Write([]byte(ta+","+link+","+name+"\n")); err != nil {
          log.Fatal(err)
      }
    }
  }
  if err := f.Close(); err != nil {
      log.Fatal(err)
  }
}

func buildTAFile(app App, semester Semester)map[string]map[string]string{
    //ta:name -> link->course
    graders := make(map[string]map[string]string)
    for _,course := range semester.Courses {
      tas := app.scrapeTAs(course.Link)
      for _,ta := range tas{
        if _,ok := graders[ta]; ok{
          graders[ta][course.Link] = course.Name
        }else{
          graders[ta] = map[string]string{course.Link:course.Name}
        }
      }
    }
    return graders
}

func updateTAs(courseID string, app App)[]string{
  tas := app.scrapeTAs(courseID)
  graders := make(map[string]map[string]string)
  for _,ta := range tas{
    graders[ta][courseID] = ""
  }
  writeTAs(graders)
  return tas
}

/*
func writeAssignment(courseID string, assignment Assignment, semester Semester){ 
  for _,course := range semester.Courses{
    if course.Link == courseID{
      course.Assignments = append(course.Assignments,assignment)
      break
    }
  }
  writeCourses(semester)
}

func writeGrading(courseID string, assignmentID string, questionID string, graders []Graders, semester Semester){
  for _,course := range semester.Courses{
    if course.Link == courseID{
      assignments := course.Assignments
      for _,assignment := range assignments{
        if assignment.Link == assignmentID{
          questions := assignment.Questions
          for _,question := range questions{
            if question.Link == questionID{
              question.Graded = graders
              writeCourses(semester)
              return
            }
          }
        }
      }
    }
  }
}
*/
