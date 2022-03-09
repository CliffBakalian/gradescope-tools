package grades

import (
  "io"
  "log"
  "os"
  "encoding/csv"
  "regexp"
  "strconv"
)

var (
  courseID string
)

type Time struct {
  Hour int8
  Minute int8
  Seconds int8
}

type Date struct {
  Year uint16
  Month int8
  Day int8
}

type Grade struct {
  Lname string
  Fname string
  UID string
  Points float32
  MaxPoints float32
  Date Date
  Time Time
  Late Time
}

//Go through the csv file and make a list of grade structs
//where each struct has name, uid, grade, and time
func ParseGradesFile(filename string) []Grade {
  f, err := os.Open(filename)
  if err != nil {
    log.Fatal("Failed to open csv file")
  }

  defer f.Close()

  csvReader := csv.NewReader(f)
  csvReader.FieldsPerRecord = -1

  var grades []Grade
  //get the time then date the assignmnet was submitted
  subtime_re := regexp.MustCompile(`(\d\d):(\d\d):(\d\d)`)
  subdate_re := regexp.MustCompile(`(\d{4})-(\d{2})-(\d{2})`)

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
    uid := record[2]
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
        Hour: int8(func(x int,y error)int{return x}(strconv.Atoi(subtime[1]))),
        Minute: int8(func(x int,y error)int{return x}(strconv.Atoi(subtime[2]))),
        Seconds: int8(func(x int,y error)int{return x}(strconv.Atoi(subtime[3]))),
      }
      lateTime = Time{
        Hour: int8(func(x int,y error)int{return x}(strconv.Atoi(latetime[1]))),
        Minute: int8(func(x int,y error)int{return x}(strconv.Atoi(latetime[2]))),
        Seconds: int8(func(x int,y error)int{return x}(strconv.Atoi(latetime[3]))),
      }
      subDate = Date{
        Year: uint16(func(x int,y error)int{return x}(strconv.Atoi(subdate[1]))),
        Month: int8(func(x int,y error)int{return x}(strconv.Atoi(subdate[2]))),
        Day: int8(func(x int,y error)int{return x}(strconv.Atoi(subdate[3]))),
      }
    }else {
      //the assignment was not submmited so just use 0 for these
      points = 0.0
      subTime = Time{
        Hour: 0,
        Minute: 0,
        Seconds: 0,
      }
      lateTime = subTime
      subDate = Date{
        Year: 0,
        Month: 0,
        Day: 0,
      }
    }

    //create the grade node in the list
    sub := Grade{
      Lname: lastName,
      Fname: firstName,
      UID: uid,
      Points: float32(points),
      MaxPoints: float32(max_points),
      Date: subDate,
      Time: subTime,
      Late: lateTime,
    }

    grades = append(grades, sub)
  }
  return grades
}
