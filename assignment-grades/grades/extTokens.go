package grades

import(
  "encoding/json"
  "fmt"
  "os"
  "io/ioutil"
  "log"
)

var (
  //maps UID to index in []Person
  studentID = make(map[string]int)
  //how long before tokens are used. Default 2 minutes
  timeLeniency = int8(2)
  students People
)

type People struct{
  People []Person `json:"people"`
}

type Person struct{
  UID string `json:"UID"`
  Tokens int `json:"tokens"`
  Assignments []string `json:"assignments"`
}

func ReadExtensions() People{
  jsonFile, err := os.Open("tokens.json")
  if err != nil {
      log.Fatalln("Cannot open tokens.json. ",err)
  }
  defer jsonFile.Close()

  bytearr, _ := ioutil.ReadAll(jsonFile)

  var people People
  err = json.Unmarshal(bytearr, &people)
  if err != nil{
    log.Fatalln("Error parsing json. ",err)
  }

  //need some way to easily access a person by UID in the Person array
  for index,value := range(people.People){
    studentID[value.UID] = index
  }

  students = people
  return people
}

//will write the People struct to json
func writeExtensions(people People){

  out, err := os.Create("tokens.json")
  if err != nil {
    log.Fatalln("Could not create file. ",err)
  }
  defer out.Close()

  b, err := json.Marshal(people)
  if err != nil {
    log.Fatalln("Failed to marshal json. ",err)
  }
  _, err = out.Write(b) 
  if err != nil {
    log.Fatalln("Failed to write file. ",err)
  }
}

//update the number of tokens people have
func UpdateExtensions(gradearr []Grade, assignID string){
  for _, value := range gradearr{
    //no need to do anything if tokens don't need to be updated
    if value.Late.Hour == 0 && value.Late.Minute <= timeLeniency {
      continue
    }
    currUID := value.UID
    //get index of current person
    studentIdx := studentID[currUID]
    var currStudent Person

    var isNew bool
    //if person already in list
    if (students.People[studentIdx].UID == currUID){
      currStudent = students.People[studentIdx]
      isNew = false
      fmt.Printf("%s %s already used tokens\n",value.Fname, value.Lname)
    }else {
      currStudent = Person{
        UID: value.UID,
        Tokens: 0,
        Assignments: []string{},
      }
      isNew = true
      fmt.Printf("%s %s used thier first token\n",value.Fname, value.Lname)
    }

    //update information
    tokenNumber := value.Late.Hour / 12
    currStudent.Tokens = currStudent.Tokens + int(tokenNumber)
    currStudent.Assignments = append(currStudent.Assignments,assignID)

    //update or add person to list
    if isNew {
      students.People = append(students.People,currStudent)
    }else{
      students.People[studentIdx] = currStudent
    }
  }
  writeExtensions(students)
}
