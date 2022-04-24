package gradescope

import (
  "log"
  "net/url"

  "github.com/PuerkitoBio/goquery"
)

const (
  baseURL = "https://www.gradescope.com"
)

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

//login to gradescope
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

  doc, err := goquery.NewDocumentFromReader(response.Body)
  doc.Find(".alert-error span").Each(func(i int, s*goquery.Selection) {
    if s.Text() == "Invalid email/password combination." {
      log.Fatalln(s.Text())
    }
  })
}
