package gradescope

import (
  "io"
  "log"
  "os"
  "encoding/csv"
  "regexp"
  "strconv"
)

var (
  submissionIDs = make(map[string]int)
)

type Time struct {
  hour int8
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

//Go through the csv file and make a list of grade structs
//where each struct has name, uid, grade, and time
func parseGradesFile(filename string) []Submission{
  f, err := os.Open(filename)
  if err != nil {
    log.Fatal("Failed to open csv file")
  }

  defer f.Close()

  csvReader := csv.NewReader(f)
  csvReader.FieldsPerRecord = -1

  var submissions []Submission
  //get the time then date the assignmnet was submitted
  subtime_re := regexp.MustCompile(`(\d\d):(\d\d):(\d\d)`)
  subdate_re := regexp.MustCompile(`(\d{4})-(\d{2})-(\d{2})`)

  //counter for mapping
  submissionidx := 0

  csvReader.Read()
  for {
    record, err := csvReader.Read()
    if err == io.EOF {
      break
    }
    //if login failed, then len < 2
    if err != nil || len(record) <2{
      f.Close()
      os.Remove(filename)
      log.Fatalln("Error parsing row. Make sure credentials correct",err)
    }

    firstName := record[0]
    lastName := record[1]
    userid := record[2]
    max_points, _ := strconv.ParseFloat(record[6], 32)    
    var points float64
    var subTime, lateTime Time
    var subDate Date

    //if assignment was not submitted, the length will notbe >8
    if len(record) > 8 {
      points, _ = strconv.ParseFloat(record[5], 32)    
      subdate := subdate_re.FindStringSubmatch(record[9])
      subtime := subtime_re.FindStringSubmatch(record[9])
      latetime := subtime_re.FindStringSubmatch(record[10])
      subTime = Time{
        hour: int8(func(x int,y error)int{return x}(strconv.Atoi(subtime[1]))),
        minute: int8(func(x int,y error)int{return x}(strconv.Atoi(subtime[2]))),
        seconds: int8(func(x int,y error)int{return x}(strconv.Atoi(subtime[3]))),
      }
      lateTime = Time{
        hour: int8(func(x int,y error)int{return x}(strconv.Atoi(latetime[1]))),
        minute: int8(func(x int,y error)int{return x}(strconv.Atoi(latetime[2]))),
        seconds: int8(func(x int,y error)int{return x}(strconv.Atoi(latetime[3]))),
      }
      subDate = Date{
        year: uint16(func(x int,y error)int{return x}(strconv.Atoi(subdate[1]))),
        month: int8(func(x int,y error)int{return x}(strconv.Atoi(subdate[2]))),
        day: int8(func(x int,y error)int{return x}(strconv.Atoi(subdate[3]))),
      }
    }else {
      //the assignment was not submmited so just use 0 for these
      points = 0.0
      subTime = Time{
        hour: 0,
        minute: 0,
        seconds: 0,
      }
      lateTime = subTime
      subDate = Date{
        year: 0,
        month: 0,
        day: 0,
      }
    }

    //create the grade node in the list
    sub := Submission{
      lname: lastName,
      fname: firstName,
      uid: userid,
      points: float32(points),
      maxPoints: float32(max_points),
      date: subDate,
      time: subTime,
      late: lateTime,
    }
    submissions= append(submissions, sub)

    submissionIDs[userid] = submissionidx
    submissionidx = submissionidx + 1
  }
  return submissions
}

func WriteGradesVerbose(submissions []Submission, subIDs map[string]int, tokens TokenList, studentIDs map[string]int,assignName string){
//  header := []string{"Student","ID","SIS User ID","SIS Login ID","Section"}
//  rows := [][]string{{}}
//  for _, submission:= range(submissions){
//    user := submission.uid
//  }
}

func WriteGrades(submissions[]Submission, tokens TokenList, assignName string){
  WriteGradesVerbose(submissions, submissionIDs, tokens, studentIDs, assignName)
}
