package gradescope

import (
  "regexp"
  "log"
  "strings"
  "strconv"
  "github.com/PuerkitoBio/goquery"
)

//type Graders struct {
//  grader string
//}

func (app *App) GetGraders(courseID string)[]string{
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

func (app *App) GetQuestions(courseID string, assignmentID string)map[string]string{
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

func (app *App) getQuestionStats(courseID string, questionsID string)map[string]int{
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
        if val, ok := stats[grader]; ok {
          stats[grader] = val + 1
        }else{
          stats[grader] = 1
        }
      }
    })
  })
  //techincally the previous find picks up both grading and submissions links
  //We only need to look at submissions here. 
  return stats
}

//this is a map from question name -> map[grader: number graded]
func (app *App) getStats(courseID string, questions map[string]string)map[string]map[string]int{
  stats := make(map[string]map[string]int)
  for question,link := range questions{
    stats[question] = app.getQuestionStats(courseID, link)
  }
  return stats
}

func countDigits(i int)int{
  count := 0
  for i != 0 {
    i /= 10
    count = count + 1
  }
  return count
}

func print_stats(graders []string,stats map[string]map[string]int)string{
  //get question names
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
  rendered := ""
  //start making the header
  rendered = strings.Repeat(" ",max_question_len+spacing+divlen)

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
