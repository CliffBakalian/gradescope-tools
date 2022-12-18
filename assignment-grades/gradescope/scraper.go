package gradescope

import (
  "log"
  "github.com/PuerkitoBio/goquery"
)

func (app *App) gradesTable(url string) *goquery.Document{
  client := app.Client
  response, err := client.Get(url+"/review_grades")
  if err != nil {
    log.Fatalln("Error getting assignments. ",err)
  }

  defer response.Body.Close()

  document, err := goquery.NewDocumentFromReader(response.Body)
  if err != nil {
    log.Fatalln("Error getting grades body. ", err)
  }
  return document
}

//given link to assignment and student email, return array of dates and scores
//easier input is name, but some students have same name
func getSubLink(document *goquery.Document,email string) string{
  
  //find the student's submission
  // look in the table
  // for each row in the table
  link := "" //link to submission
  found := false
  document.Find(".js-reviewGradesTable tbody tr").EachWithBreak(func(i int, s*goquery.Selection)bool {
    s.Find("td").EachWithBreak(func(k int, p*goquery.Selection)bool{
      //if the first column of row (the name and link)
      if k == 0{
        //find the link
        p.Find(".table--primaryLink a").Each(func(j int, q*goquery.Selection) {
          link,_ = q.Attr("href")
        })
      }else{// if k == 1{ //if second column (the email)
        p.Find("a").EachWithBreak(func(j int, q*goquery.Selection)bool {
          if q.Text() == email{
            found = true
            return false
          }
          return true
        })
      }/* else{
        return false
      }*/
      return true
    })
    
    // if found, no need to continue looping through list
    if found{
      return false
    }
    return true
  })

  if link == ""{
    log.Fatalln("Could not find submission")
  }
  return link 
}

func (app *App) getTimes(url string) *goquery.Document{
  client := app.Client
  response, err := client.Get(url)
  if err != nil {
    log.Fatalln("Error getting submission. ",err)
  }

  defer response.Body.Close()

  document, err := goquery.NewDocumentFromReader(response.Body)
  if err != nil {
    log.Fatalln("Error getting submission body. ", err)
  }
  return document
}
