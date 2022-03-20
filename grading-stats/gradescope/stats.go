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
  "regexp"

  "golang.org/x/crypto/ssh/terminal"
  "github.com/PuerkitoBio/goquery"
)

type Graders struct {
  string
}

func (app *App) getGraders(
