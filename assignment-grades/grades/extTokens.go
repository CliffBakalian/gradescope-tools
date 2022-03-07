package grades

import(
  "encoding/json"
  "fmt"
  "os"
  "io/ioutil"
  "log"
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

  for i := 0; i < len(people.People); i++ {
    fmt.Printf("Person: %s\tTokens: %d\tAssignmnet[0]: %s\n",people.People[i].UID, people.People[i].Tokens, people.People[i].Assignments[0])
  }
  return people
}
