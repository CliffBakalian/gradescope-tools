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

func Gradescope(interactive bool,course string, assignment string, email string, password string, all bool) {
  jar, _ := cookiejar.New(nil)
  app := App{
    Client: &http.Client{Jar: jar},
  }

  if email == ""{
    email = getEmail()
  }
  if password == ""{
    password = getPassword()
  }
  app.login(email,password)

  semester,err := readCourses()
  if err != nil{
    semester = Semester{Courses:[]Course{}}
  }
  if interactive {
    course = getCourseID()
    assignment = getAssignID()
  }else if all{
    semester = buildSemester(app)
    writeCourses(semester)
  }else{
    if course == ""{
      course = getCourseID()
    }
    if assignment == ""{
      course = getAssignID()
    }
  }
  graders := GetGraders(course, app)
  stats,val:= GetStats(semester,course,assignment)
  if val != -1{ //the assignment or course was not found
    updateAssignment(app,semester,course,assignment)
    semester,_ := readCourses()
    stats,_ = GetStats(semester,course,assignment)
  }

  rendered_stats := print_stats(graders,stats)
  fmt.Println(rendered_stats)
}
