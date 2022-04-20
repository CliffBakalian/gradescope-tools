package gradescope

import (
  "fmt"
  "strings"
  "bufio"
  "os"
)

var courseID string

/*
  0 - courses
  1 - select
  2 - get (vanilla)
  3 - grade (vanilla)
  4 - exit
*/

func parse_input(input []string)(int, string){
  switch input[0]{
    case "courses": return 0,""
    case "select": 
                  if len(input) > 1{
                    return 1,input[1]
                  }
                  return -1,"Incorrecy number of args"
    case "get": return parseGet(input[1:])
    case "grade": return parseGrade(input[1:])
    case "exit": return 4,""
    case "quit": return 4,""
    default: return -1,"Unknown command\n"
   }
}

func parseGet(input []string)(int,string){
  switch input[0]{
    case "assignments": 
      if len(input) > 1 {
        return 2,input[1]
      }else if courseID != ""{
        return 2,courseID
      }else{
        return -1, "CourseID not selected or provided"
      }
    default: return -1,"Cannot get that for you"
  }
}

func parseGrade(input []string)(int,string){
  if len(input) > 1 {
    courseID = input[1]
  }
  if courseID != ""{
    return 3,input[0]
  }
  return -1, "CourseID not selected or provided"
}

func repl_eval(code int, message string, app App) bool{
  switch code{
    case 0: courses := app.getCourses()
            for k,v := range courses{
              fmt.Printf("%s:%s\n",v,k)
            }
            return false
    case 1: courseID = message
            return false
    case 2: assigns := app.getAssignments(message)
            for k,v := range assigns{
              fmt.Printf("%s:%s\n",v,k)
            }
            return false
    case 3: grade(courseID,message,app) 
            return false
    case 4: return true;
    default: fmt.Println(message) 
            return false
  }
  return true
}

func startRepl(app App){
  scanner := bufio.NewScanner(os.Stdin)
  fmt.Print("\n")
  var input string
  for {
    if courseID != ""{
      fmt.Print("("+courseID+") ")
    }
    fmt.Print("> ")
    if scanner.Scan(){
      input = scanner.Text()
    }
    code,message := parse_input(strings.Fields(input))
    stop := repl_eval(code,message,app)
    if stop{
      break;
    }
  }
}

