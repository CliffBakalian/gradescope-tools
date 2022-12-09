package main

import (
  "github.com/cliffbakalian/gradescope-tools/grading-stats/gradescope"
  "flag"
)


func main() {
  interactive := flag.Bool("interactive", false, "run in interactive mode")
  course_id := flag.String("course", "", "The course ID")
  assignment_id := flag.String("assignment","","The assignment ID")
  email := flag.String("email","","login email")
  password := flag.String("password","","please never use but helpful for scripting purposes")
  pf := flag.Bool("print", false, "pretty print output to stdout")
  //partial := flag.Bool("partial", false, "update only those that are not graded")
  update := flag.Bool("update", false, "update the databse")
  init := flag.Bool("Init", false, "Update everything and remake grader file")

  flag.Parse()

  gradescope.Gradescope(*interactive, *course_id, *assignment_id, *email, *password, *pf, *update,*init)
}
