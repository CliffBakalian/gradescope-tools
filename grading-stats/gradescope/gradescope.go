package gradescope

import (
  "fmt"
  "net/http"
  "net/http/cookiejar"
  "log"
  "io/ioutil"
  "net/url"
  "regexp"

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
func getLoginCreds() (string,string){
  fmt.Print("Gradescope email: ")
  var email string
  fmt.Scanln(&email)
  fmt.Print("Enter password: ")
  password, _:= terminal.ReadPassword(0)
  return email, string(password)
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

  _, err = ioutil.ReadAll(response.Body)
  if err != nil {
    log.Fatalln("Error Login Body. ", err)
  }
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

//Should use input flags rather than this
func getCourseInfo() (string,string){
  var course, assignment string
  fmt.Print("Course ID: ")
  fmt.Scanln(&course)
  fmt.Print("Assignment ID: ")
  fmt.Scanln(&assignment)
  return course,assignment
}

func Gradescope(interactive bool,course string, assignment string, email string, password string) {
  jar, _ := cookiejar.New(nil)

  app := App{
    Client: &http.Client{Jar: jar},
  }

  if interactive {
    course,assignment = getCourseInfo()
    email,password = getLoginCreds()
  }

  app.login(email,password)

  graders := app.GetGraders(course)
  fmt.Println(graders)
  //stats := getStats(graders)
  //fmt.Println(stats)
}
