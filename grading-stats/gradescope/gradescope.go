package gradescope

import (
  "fmt"
  "net/http"
  "net/http/cookiejar"

  "golang.org/x/crypto/ssh/terminal"
)

type App struct {
  Client *http.Client
}
type AuthenticityToken struct {
  Token string
}

var semester Semester

//prompt password
func getPassword() string{
  fmt.Print("Enter password: ")
  password, _:= terminal.ReadPassword(0)
  return string(password)
}

//prompt email
func getEmail() string{
  fmt.Print("Gradescope email: ")
  var email string
  fmt.Scanln(&email)
  return email
}

func getCourseID() string{
  var course string
  fmt.Print("Course ID: ")
  fmt.Scanln(&course)
  return course
}

func getAssignID() string{
  var assignment string
  fmt.Print("Assignment ID: ")
  fmt.Scanln(&assignment)
  return assignment
}

//Use this to get graders
func GetGraders(courseID string,app App)[]string{
  //try reading from file
  graders, err := readTAs(courseID)
  if err != nil || len(graders) == 0{
    //scrap from gradescope ans store to file
    return updateTAs(courseID, app) 
  }
  return graders
}

func checkCreds(email string,password string)(string,string){
  if email==""{
    email = getEmail()
  }
  if password == ""{
    password = getPassword()
  }
  return email,password
}

// func updateCourse(courseID course){
// 
// }
// 
// func updateCourse(courseID string, assignID string){
// 
// }

// need 6 options
// cache is false
// update everything - all
// update single course 
// update single assignment

// cache is true
// write everything
// write single course 
// write single assignment

func Gradescope(interactive bool,course string, assignment string, email string, password string, all bool, cache bool) {
  jar, _ := cookiejar.New(nil)
  app := App{
    Client: &http.Client{Jar: jar},
  }

  email,password = checkCreds(email,password)
  app.login(email,password)


  if interactive { //redo this, so don't do anything
    fmt.Println("Not inplemented yet")
  }else{
    var stats map[string]map[string]int
    var val int

    if !cache {              // update the stuff
      if course == "" {           // update it all 
        fmt.Println("Update it all")
        semester = buildSemester(app)
        tas := buildTAFile(app,semester)
        writeTAs(tas)
        writeCourses(semester)
      }else{
        semester,err := readCourses() //get existing data from cache
        if err != nil{
          semester = Semester{Courses:[]Course{}}
        }

        if assignment == ""{  // update entire course
          fmt.Println("Update course")
          for _,course := range semester.Courses{
            for _,assign := range course.Assignments{
              _,val = updateAssignStats(semester,course.Link,assign.Link,buildQuestions(app,course.Link,assign.Link))
              if val != -1{ //the assignment or course was not found
                fmt.Println("Error updating")  
              }
            }
          }
        }else{                      // update single assignment
          fmt.Println("Update assignment")
          // this will also write the file too
          _,val = updateAssignStats(semester,course,assignment,buildQuestions(app,course,assignment))
          if val != -1{ //the assignment or course was not found
            fmt.Println("Error updating")  
          }
        }
      }
    }else{ // write the stuff
      semester,err := readCourses() //get information from cache
      if err != nil{
        semester = Semester{Courses:[]Course{}}
      }

      if course == "" {           // write it all
        fmt.Println("Write it all")  
        for _,course := range semester.Courses{
          graders := GetGraders(course.Link, app)
          for _,assign := range course.Assignments{
            stats,_ = GetStats(semester,course.Link,assign.Link)
            csv_stats(assign.Link,graders,stats)
          }
        }

      }else if assignment == ""{  // write entire course
        fmt.Println("Write course")  
        graders := GetGraders(course, app)
        for _,c:= range semester.Courses{
          if c.Link == course{
            for _,assign := range c.Assignments{
              stats,_ = GetStats(semester,course,assign.Link)
              csv_stats(assign.Link,graders,stats)
            }
          }
        }
      }else{                      // write single assignment
        fmt.Println("Write assignment")  
        graders := GetGraders(course, app)
        stats,_ = GetStats(semester,course,assignment)
        csv_stats(assignment,graders,stats)
      }
    }
  }

  //rendered_stats := print_stats(graders,stats)
  //print_stats(graders,stats)
  //for _,c:= range semester.Courses{
  //  graders := GetGraders(course, app)
  //  for _,a := range c.Assignments {
  //    csv_stats(a.Link,graders,stats)
  //  }
  //}
  //csv_stats(assignment,graders,stats)
  //write_stats(course,assignment,semester)
  //fmt.Println(rendered_stats)
}
