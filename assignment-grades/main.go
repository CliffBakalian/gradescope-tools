package main

import (
  "fmt"
  "io/ioutil"
  "io"
  "log"
  "net/http"
  "net/http/cookiejar"
  "net/url"
  "os"
  "encoding/csv"
  "regexp"
  "strconv"

  "golang.org/x/crypto/ssh/terminal"
  "github.com/PuerkitoBio/goquery"
)

var (
  assignments = make(map[string]string)
  courseID string
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

type Grade struct {
  lname string
  fname string
  UID string
  points float32
  maxPoints float32
  date Date
  time Time
  late Time
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

//Go through the csv file and make a list of grade structs
//where each struct has name, uid, grade, and time
func parseGradesFile(filename string) []Grade {
  f, err := os.Open(filename)
  if err != nil {
    log.Fatal("Failed to open csv file")
  }

  defer f.Close()

  csvReader := csv.NewReader(f)
  csvReader.FieldsPerRecord = -1

  var grades []Grade
  //get the time then date the assignmnet was submitted
  subtime_re := regexp.MustCompile(`(\d\d):(\d\d):(\d\d)`)
  subdate_re := regexp.MustCompile(`(\d{4})-(\d{2})-(\d{2})`)

  csvReader.Read()
  for {
    record, err := csvReader.Read()
    if err == io.EOF {
      break
    }
    //if login failed, then len < 2
    if err != nil || len(record) <2{
      f.Close()
      os.Remove(filename)
      log.Fatalln("Error parsing row. Make sure credentials correct",err)
    }

    firstName := record[0]
    lastName := record[1]
    uid := record[2]
    max_points, _ := strconv.ParseFloat(record[6], 32)    
    var points float64
    var subTime, lateTime Time
    var subDate Date

    //if assignment was not submitted, the length will notbe >8
    if len(record) > 8 {
      points, _ = strconv.ParseFloat(record[5], 32)    
      subdate := subdate_re.FindStringSubmatch(record[9])
      subtime := subtime_re.FindStringSubmatch(record[9])
      latetime := subtime_re.FindStringSubmatch(record[10])
      subTime = Time{
        hour: int8(func(x int,y error)int{return x}(strconv.Atoi(subtime[1]))),
        minute: int8(func(x int,y error)int{return x}(strconv.Atoi(subtime[2]))),
        seconds: int8(func(x int,y error)int{return x}(strconv.Atoi(subtime[3]))),
      }
      lateTime = Time{
        hour: int8(func(x int,y error)int{return x}(strconv.Atoi(latetime[1]))),
        minute: int8(func(x int,y error)int{return x}(strconv.Atoi(latetime[2]))),
        seconds: int8(func(x int,y error)int{return x}(strconv.Atoi(latetime[3]))),
      }
      subDate = Date{
        year: uint16(func(x int,y error)int{return x}(strconv.Atoi(subdate[1]))),
        month: int8(func(x int,y error)int{return x}(strconv.Atoi(subdate[2]))),
        day: int8(func(x int,y error)int{return x}(strconv.Atoi(subdate[3]))),
      }
    }else {
      //the assignment was not submmited so just use 0 for these
      points = 0.0
      subTime = Time{
        hour: 0,
        minute: 0,
        seconds: 0,
      }
      lateTime = subTime
      subDate = Date{
        year: 0,
        month: 0,
        day: 0,
      }
    }

    //create the grade node in the list
    sub := Grade{
      lname: lastName,
      fname: firstName,
      UID: uid,
      points: float32(points),
      maxPoints: float32(max_points),
      date: subDate,
      time: subTime,
      late: lateTime,
    }

    grades = append(grades, sub)
  }
  return grades
}

func main() {
  jar, _ := cookiejar.New(nil)

  app := App{
    Client: &http.Client{Jar: jar},
  }
  courseID = "358323"
  assignmentID := "1896262"
  app.login()

  app.getAssignmnets()
  //need to add more interaction, rn getAssignments is useless
  app.downloadGrades(assignmentID)
  grades := parseGradesFile(assignmentID+".csv")

  for _, grade := range grades {
    fmt.Printf("%s:%.2f\n", grade.lname,grade.points)
  }
}
