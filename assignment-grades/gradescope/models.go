package gradescope

type Time struct {
  hour int16
  minute int8
  seconds int8
}

type Date struct {
  year uint16
  month int8
  day int8
}

type Submission struct {
  lname string
  fname string
  uid string
  points float32
  maxPoints float32
  date Date
  time Time
  late Time
}

type Student struct{
  UID string `json:"UID"`
  Tokens int `json:"tokens"`
  Assignments []string `json:"assignments"`
  AssignTokens []int `json:"assignTokens`
}

type AltScore struct{
  //subdate Date //when they submitted, used to account for extentions
  score int //score
  tokens int //how many tokens for that score
}

// score can be an int since we don't give partial points on projects
//store alternative scores with tokens
type Assignment struct {
  name string //name of assignment
  points int //out of how many points (typically 100)
  score int //score on record
  percent float32 //percent of overall grade. does need to be float
  late Time //how late they submitted
  duedate Date //day it was due
  link string //link to project
  assigntype string //project type, could add others later
  alternative []AltScore //list of possible scores they could have
}

type User struct {
  lname string
  fname string
  uid string
  email string
  section string
  assignments []Assignment
}
