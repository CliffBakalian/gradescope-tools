package gradescope

import (
  "log"
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
