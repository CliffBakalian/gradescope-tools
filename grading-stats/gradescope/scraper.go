package gradescope

import (
  "regexp"
  "log"
  "strconv"
  "github.com/PuerkitoBio/goquery"
)

//return a ID list -> name for courses
func (app *App) scrapeCourses() map[string]string{
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

// return course name from ID
func (app *App) scrapeCourseName(courseID string) string{
  names := app.scrapeCourses()
  return names[courseID]
}

// return assignment name from ID
func (app *App) scrapeAssignmentName(courseID string,assignmentID string)(string,int){
  names,subs := app.scrapeAssignments(courseID)
  return names[assignmentID],subs[assignmentID]
}

// get the ta's name from the course
func (app *App) scrapeTAs(courseID string)[]string{
  rosterURL:= baseURL+"/courses/"+courseID+"/memberships"
  client := app.Client
  graders := []string{}
  response, err := client.Get(rosterURL)
  if err != nil {
    log.Fatalln("Error getting roster. ",err)
  }

  defer response.Body.Close()

  document, err := goquery.NewDocumentFromReader(response.Body)
  if err != nil {
    log.Fatalln("Error getting roster body. ", err)
  }

  // look at each row in roster and if TA, add them to list
  document.Find(".rosterRow").Each(func(i int, s*goquery.Selection) {
    //need to split this up because of data at different levels
    s.Find(".js-rosterRoleSelect option").Each(func(i int, o*goquery.Selection){
      _,exists := o.Attr("selected")
      if exists && o.Text() == "TA"{
        //For some reason finding 'sorting_1' wont work so i have to remove
        // the 'Edt' from the text because they are both part of td
        user := s.Find("td").First().Text()
        graders = append(graders,user[:(len(user)-5)])
      }
    })
  })
  return graders
}

//go to assignments page and get all names and links
//also get how many submissions per assignment
func (app *App) scrapeAssignments(courseID string) (map[string]string, map[string]int){
  assignURL:= baseURL+"/courses/"+courseID+"/assignments"
  client := app.Client
  assignments := make(map[string]string)
  sub_count := make(map[string]int)
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
  document.Find(".js-assignmentTableAssignmentRow").Each(func(i int, s*goquery.Selection){
    //get the name of the assignment
    var assign_name []string
    s.Find(".table--primaryLink a").Each(func(j int, p*goquery.Selection) {
      link, _:= p.Attr("href")

      assign_name = assignment_link_re.FindStringSubmatch(link)
      assignments[assign_name[1]] = p.Text()
    })

    s.Find(".table--cell-emph").Each(func (i int, p*goquery.Selection){
      if i == 1{
        sub_count[assign_name[1]],err = strconv.Atoi(p.Text())
      }
    })
  })
  return assignments,sub_count
}

//get the name of the questions and the link to the question 
func (app *App) scrapeQuestions(courseID string, assignmentID string)map[string]string{
  assignURL := baseURL+"/courses/"+courseID+"/assignments/"+ assignmentID+"/grade"
  client := app.Client
  questions := make(map[string]string)
  response, err := client.Get(assignURL)
  if err != nil {
    log.Fatalln("Error getting questions. ",err)
  }

  defer response.Body.Close()

  document, err := goquery.NewDocumentFromReader(response.Body)
  if err != nil {
    log.Fatalln("Error getting questions body. ", err)
  }

  question_link_re := regexp.MustCompile(`questions\/(\d+)\/(grade|submissions)`)
  document.Find("a.link-noUnderline").Each(func(i int, s*goquery.Selection) {
    //get the link for the questions to obtain who graded who 
    link, _:= s.Attr("href")
    q_id := question_link_re.FindStringSubmatch(link)
    //s.Text is the name of the class
    questions[s.Text()] = q_id[1]
  })
  //techincally the previous find picks up both grading and submissions links
  //We only need to look at submissions here. 
  delete(questions," Submissions")
  return questions
}

//go the submissions page of an assignment and see who graded what
func (app *App) scrapeGraders(courseID string, questionsID string)map[string]int{
  subURL := baseURL+"/courses/"+courseID+"/questions/"+ questionsID+"/submissions"
  client := app.Client
  stats := make(map[string]int)
  response, err := client.Get(subURL)
  if err != nil {
    log.Fatalln("Error getting questions. ",err)
  }

  defer response.Body.Close()

  document, err := goquery.NewDocumentFromReader(response.Body)
  if err != nil {
    log.Fatalln("Error getting questions body. ", err)
  }

  document.Find("table tbody tr").Each(func(i int, s*goquery.Selection) {
    s.Find("td").Each(func(j int, t*goquery.Selection){
      //get who graded the submission
      if j == 2{
        grader := t.Text()
        if grader != ""{
          if val, ok := stats[grader]; ok {
            stats[grader] = val + 1
          }else{
            stats[grader] = 1
          }
        }
      }
    })
  })
  return stats
}
