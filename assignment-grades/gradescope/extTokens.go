package gradescope

import(
  "encoding/json"
  "fmt"
  "os"
  "io/ioutil"
  "log"
)

var (
  //maps UID to index in []Tokenlist
  studentIDs = make(map[string]int)
  //how long before tokens are used. Default 2 minutes
  timeLeniency = int8(2)
)

type TokenList struct{
  Students []Student `json:"students"`
}

type Student struct{
  UID string `json:"UID"`
  Tokens int `json:"tokens"`
  Assignments []string `json:"assignments"`
  AssignTokens []int `json:"assignTokens`
}

func readTokenExtensions() TokenList{
  jsonFile, err := os.Open("tokens.json")
  if err != nil {
    log.Println("Cannot open tokens.json. ",err)
    log.Println("Creating file. ")
    os.Create("tokens.json")
    return TokenList{Students: []Student{}}
  }
  defer jsonFile.Close()

  bytearr, _ := ioutil.ReadAll(jsonFile)

  var tokens TokenList
  err = json.Unmarshal(bytearr, &tokens)
  if err != nil{
    log.Println("Error parsing json. ",err)
    log.Println("Ignoring Contents")
    return TokenList{Students: []Student{}}
  }

  //need some way to easily access a person by UID in the TokenList array
  for index,value := range(tokens.Students){
    studentIDs[value.UID] = index
  }
  return tokens
}

//will write the People struct to json
func writeExtensions(tokens TokenList){
  out, err := os.Create("tokens.json")
  if err != nil {
    log.Fatalln("Could not create file. ",err)
  }
  defer out.Close()

  b, err := json.Marshal(tokens)
  if err != nil {
    log.Fatalln("Failed to marshal json. ",err)
  }
  _, err = out.Write(b)
  if err != nil {
    log.Fatalln("Failed to write file. ",err)
  }
}

//update the number of tokens people have
func updateExtensions(submissions map[string]Submission, tokens TokenList, assignID string) TokenList{
  peopleLen := len(tokens.Students)
  for _, submission:= range submissions{
    //no need to do anything if tokens don't need to be updated
    if submission.late.hour == 0 && submission.late.minute <= timeLeniency {
      continue
    }
    currUID := submission.uid
    //get index of current person
    studentIdx := studentIDs[currUID]
    var currStudent Student

    var isNew bool
    //if person already in list
    if (peopleLen > 0 && tokens.Students[studentIdx].UID== currUID){
      currStudent = tokens.Students[studentIdx]
      isNew = false
    }else {
      currStudent = Student{
        UID: submission.uid,
        Tokens: 0,
        Assignments: []string{},
      }
      isNew = true
    }

    //update information
    tokenNumber := (submission.late.hour / 12)+1
    oldTokens := currStudent.Tokens
    currStudent.AssignTokens = append(currStudent.AssignTokens,int(tokenNumber))
    currStudent.Tokens = currStudent.Tokens + int(tokenNumber)
    currStudent.Assignments = append(currStudent.Assignments,assignID)
    fmt.Printf("%s %s (%s) had %d, submitted %d hours late, and has used %d tokens\n",submission.fname, submission.lname,currStudent.UID,oldTokens,submission.late.hour,int(currStudent.Tokens))

    //update or add person to list
    if isNew {
      tokens.Students= append(tokens.Students,currStudent)
      studentIDs[submission.uid] = peopleLen
      peopleLen = peopleLen + 1
    }else{
      tokens.Students[studentIdx] = currStudent
    }
  }
  return tokens;
}
