package gradescope

import (
  "fmt"
  "net/http"
  "net/http/cookiejar"
  "log"
  "os"
  "io"
  "io/ioutil"
  "net/url"

  "golang.org/x/crypto/ssh/terminal"
  "github.com/PuerkitoBio/goquery"
)

const (
  baseURL = "https://www.gradescope.com"
)

var (
  assignments = make(map[string]string)
  courseID string
  assignmentID string
)

type App struct {
  Client *http.Client
}
type AuthenticityToken struct {
  Token string
}

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

//prompt login creds and then login
func (app *App) login() {
  client := app.Client
  authenticityToken := app.getToken()

  loginURL := baseURL + "/login"

  fmt.Print("Gradescope email: ")
  var email string
  fmt.Scanln(&email)
  fmt.Print("Enter password: ")
  password, err := terminal.ReadPassword(0)

  data := url.Values{
    "authenticity_token": {authenticityToken.Token},
    "session[email]":     {email},
    "session[password]":  {string(password)},
  }

  response, err := client.PostForm(loginURL, data)

  if err != nil {
    //Note: if you fail to login, this will not be triggered
    log.Fatalln("Error logging in. ", err)
  }

  defer response.Body.Close()

  _, err = ioutil.ReadAll(response.Body)
  if err != nil {
    log.Fatalln("Error Login Body. ", err)
  }
}

//go to assignments page and get all names and links
func (app *App) getAssignmnets() {
  assignURL:= baseURL+"/courses/"+courseID+"/assignments"
  client := app.Client

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
  document.Find(".table--primaryLink a").Each(func(i int, s*goquery.Selection) {
    name, _:= s.Attr("href")
    //TODO parse 'name' for ID. Currently its a link
    assignments[s.Text()] = name
  })
}

//download the csvfile. The file is just the assignmnet url with 'scores.csv'
//tacked on. 
func (app *App) downloadGrades(assignID string) {
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
func getCourseInfo(){
  fmt.Print("Course ID: ")
  fmt.Scanln(&courseID)
  fmt.Print("Assignment ID: ")
  fmt.Scanln(&assignmentID)
}

func Gradescope() {
  jar, _ := cookiejar.New(nil)

  app := App{
    Client: &http.Client{Jar: jar},
  }

  getCourseInfo()

  app.login()

  need to add more interaction, rn getAssignments is useless
  app.getAssignmnets()

  fmt.Printf("Getting grades...\n")
  app.downloadGrades(assignmentID)

  fmt.Printf("Parsing grades...\n")
  submissions := parseGradesFile(assignmentID+".csv")

  fmt.Printf("Getting extensions...\n")
  tokenList := readExtensions()
  fmt.Printf("updating extensions...\n")
  updatedTokens := updateExtensions(submissions, tokenList, assignmentID)
  fmt.Printf("Writing extensions...\n")
  writeExtensions(updatedTokens)
  fmt.Printf("Writing results...\n")
  //TODO need to then write modified grades based off tokens 
  //grades.WriteGrades()

  fmt.Printf("Done :)\n")
}
