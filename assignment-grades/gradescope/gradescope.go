package gradescope

import (
  "fmt"
  "net/http"
  "net/http/cookiejar"
  "log"
  "os"
  "io"
  "net/url"
  "regexp"
  "strings"

  "golang.org/x/crypto/ssh/terminal"
  "github.com/PuerkitoBio/goquery"
)

const (
  baseURL = "https://www.gradescope.com"
)

type App struct {
  Client *http.Client
}
type AuthenticityToken struct {
  Token string
}

var gsClient App

//need authenticty token when logging in
func (app *App) getToken() AuthenticityToken {
  loginURL := baseURL + "/login"
  client := app.Client

  response, err := client.Get(loginURL)

  if err != nil {
    log.Fatalln("Error fetching login page. ", err)
  }

  defer response.Body.Close()

  document, err := goquery.NewDocumentFromReader(response.Body)
  if err != nil {
    log.Fatalln("Error reading HTTP response. ", err)
  }

  token, _ := document.Find("input[name='authenticity_token']").Attr("value")

  authenticityToken := AuthenticityToken{
    Token: token,
  }

  return authenticityToken
}


func getEmail() string{
  fmt.Print("Gradescope email: ")
  var email string
  fmt.Scanln(&email)
  return email
}

func getPassword() string{
  fmt.Print("Enter password: ")
  password, _:= terminal.ReadPassword(0)
  return string(password)
}
//prompt login creds and then login
func getLoginCreds() (string,string){
  return getEmail(), getPassword()
}

func (app *App) login(email string, password string) {
  client := app.Client
  authenticityToken := app.getToken()

  loginURL := baseURL + "/login"

  data := url.Values{
    "authenticity_token": {authenticityToken.Token},
    "session[email]":     {email},
    "session[password]":  {password},
  }

  response, err := client.PostForm(loginURL, data)

  if err != nil {
    //Note: if you fail to login, this will not be triggered
    log.Fatalln("Error logging in. ", err)
  }

  defer response.Body.Close()
  //check to make sure login creds were right
  doc, err := goquery.NewDocumentFromReader(response.Body)
  doc.Find(".alert-error span").Each(func(i int, s*goquery.Selection) {
    if s.Text() == "Invalid email/password combination." {
      log.Fatalln(s.Text())
    }
  })
}

func (app *App) getCourses() map[string]string{
  coursesURL:= baseURL
  client := app.Client
  courses := make(map[string]string)

  response, err := client.Get(coursesURL)
  if err != nil {
    log.Fatalln("Error getting assignments. ",err)
  }

  defer response.Body.Close()

  document, err := goquery.NewDocumentFromReader(response.Body)
  if err != nil {
    log.Fatalln("Error getting grades body. ", err)
  }

  //find the classes id and name, then map name to ID
  //look at only this current semester
  document.Find(".courseList--coursesForTerm").Each(func(i int, s*goquery.Selection) {
    //look at only this current semester
    if i == 0{
      course_link_re := regexp.MustCompile(`courses\/(\d+)`)
      s.Find(".courseBox").Each(func(i int, o*goquery.Selection){
        link,_ := o.Attr("href")
        o.Find(".courseBox--shortname").Each(func(i int, p*goquery.Selection){
          c_id := course_link_re.FindStringSubmatch(link)
          courses[c_id[1]] = p.Text()
        })
      })
    }
  })
  return courses
}

//go to assignments page and get all names and links
func (app *App) getAssignments(courseID string) map[string]string{
  assignURL:= baseURL+"/courses/"+courseID+"/assignments"
  client := app.Client
  assignments := make(map[string]string)

  response, err := client.Get(assignURL)
  if err != nil {
    log.Fatalln("Error getting assignments. ",err)
  }

  defer response.Body.Close()

  document, err := goquery.NewDocumentFromReader(response.Body)
  if err != nil {
    log.Fatalln("Error getting grades body. ", err)
  }

  //class in which the link to the assignments are. The text is name
  //of assignment whereas link holds the assignmnet ID
  assignment_link_re := regexp.MustCompile(`assignments\/(\d+)`)
  document.Find(".table--primaryLink a").Each(func(i int, s*goquery.Selection) {
    link, _:= s.Attr("href")

    a_id := assignment_link_re.FindStringSubmatch(link)
    assignments[a_id[1]] = s.Text()
  })
  return assignments
}

func grade(courseID string, assignID string, app App){
  app.downloadGrades(courseID,assignID)
  submissions := parseGradesFile(assignID+".csv")
  tokenList := readExtensions()
  updatedTokens := updateExtensions(submissions, tokenList, assignID)
  writeExtensions(updatedTokens)
}

//download the csvfile. The file is just the assignmnet url with 'scores.csv'
//tacked on. 
func (app *App) downloadGrades(courseID string, assignID string) {
  gradesURL := baseURL+"/courses/"+courseID+"/assignments/"+assignID+"/scores.csv"
  client := app.Client

  response, err := client.Get(gradesURL)

  if err != nil {
    log.Fatalln("Error getting grades.csv. ", err)
  }

  defer response.Body.Close()

  out, err := os.Create(assignID+".csv")
  if err != nil {
    log.Fatalln("Could not create file. ",err)
  }

  defer out.Close()

  _, err = io.Copy(out, response.Body)
  if err != nil {
    log.Fatalln("Failed to write file. ",err)
  }
}

//Should use input flags rather than this
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

func getCourseInfo() (string,string){
  return getCourseID(),getAssignID()
}

func Gradescope(interactive bool,course string, assignment string, email string, password string) {
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

  if interactive {
    startRepl(app)
  }else{

  if course == ""{
    course = getCourseID()
  }
  if assignment == ""{
    assignment = getAssignID()
  }

  //need to add more interaction, rn getAssignments is useless
  ass := app.getAssignments(course)
  fmt.Print(ass)

  fmt.Printf("Getting grades...\n")
  app.downloadGrades(course, assignment)

  fmt.Printf("Parsing grades...\n")
  submissions := parseGradesFile(assignment+".csv")

  fmt.Printf("Storing grades...\n")
  os.Rename(assignment+".csv",strings.ReplaceAll(ass[assignment], " ", "_")+".csv")

  fmt.Printf("Getting extensions...\n")
  tokenList := readExtensions()
  fmt.Printf("updating extensions...\n")
  updatedTokens := updateExtensions(submissions, tokenList, assignment)
  fmt.Printf("Writing extensions...\n")
  writeExtensions(updatedTokens)
  fmt.Printf("Writing results...\n")
  //TODO need to then write modified grades based off tokens 
  //grades.WriteGrades()

  fmt.Printf("Done :)\n")
  }
}
