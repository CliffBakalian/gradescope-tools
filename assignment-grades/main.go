package main

import (
  "github.com/cliffbakalian/gradescope-tools/assignment-grades/gradescope"
  "flag"
)


func main() {
  interactive := flag.Bool("interactive", false, "run in interactive mode")
  course_id := flag.String("course", "", "The course ID")
  assignment_id := flag.String("assignment","","The assignment ID")
  email := flag.String("email","cliffbakalian@gmail.com","login email")
  password := flag.String("password","","please never use but helpful for scripting purposes")
  merge := flag.Bool("merge",false,"If you want to merge to assignments. Really no need for this")
//  codeproject := flag.Bool("hw", false, "If you don't need to look at project data")

  flag.Parse()

  gradescope.Gradescope(*interactive, *course_id, *assignment_id, *email, *password, *merge)
}
