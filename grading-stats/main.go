package main

import (
  "github.com/cliffbakalian/gradescope-tools/grading-stats/gradescope"
  "flag"
)


func main() {
  interactive := flag.Bool("interactive", false, "run in interactive mode")
  course_id := flag.String("course", "", "The course ID")
  assignment_id := flag.String("assignment","","The assignment ID")
  email := flag.String("email","cliffbakalian@gmail.com","login email")
  password := flag.String("password","","please never use but helpful for scripting purposes")
  all := flag.Bool("all", false, "scrape everything. May take a while")
  cache := flag.Bool("cache", false, "don't scrape, but read from cache")

  flag.Parse()

  gradescope.Gradescope(*interactive, *course_id, *assignment_id, *email, *password, *all ,*cache)
}
