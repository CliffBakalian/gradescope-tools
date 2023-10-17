# Gradescope Grading Stats

***Disclaimer: Gradescope has no API so this is a scraper. Sometimes Gradescope changes it's formatting. Just make an issue and I'll update it***

***Now in Selenium since gradescope changed thier page to be dynamic***

## installation 

you can install this by running `go install github.com/cliffbakalian/gradescope-tools/grading-stats`  
Note: make sure your $GOPATH is set. I beieve by default it is not. Assuming go is installed in `~/go`
you should be able to run:
```
export GOPATH="$HOME/go"
PATH="$GOPATH/bin:$PATH"
```
to add the install binary to your path

## Running the program
There are two things you can do, either get the grading data, or write the grading data to file

Gradescope urls look like https://www.gradescope.com/courses/XXXXX/assignments/YYYYYYY/ where XXXXXX is the course id and YYYYYYY is the assignment id.

So an example command would be:
```
grading-stats -course XXXXXX -assignment YYYYYYY -email cliffbakalian@gmail.com -password password123
```

If you do not provide an email (gradescope login) and password then the program will prompt you for it.
Sending in the password as a command line argument is not safe so please don't do it. It does make scripting nice though :)

## Updating the 'Databse'

I put 'database' in quotes because it's just a json file : `.assignments.json` to be specific
To update or create the 'database' of grading information, you can update
  + all the courses you have
  + a singleular course
  + just a single assignment

By using the `-update` flag, the program will update the entire 'databse'. Since at the time of writng this, gradescope does not seem to have an API, we must scrape so please be nice to gradescope servers and do this occasionally.  

To update all active courses leave the course flag empty:
```
grading-stats -update 
```

To update all assignments in a single course leave the assignment flag empty:
```
grading-stats -update -course XXXXXX 
```

To update a single assignment, give both a course and assignment value:
```
grading-stats -update -course XXXXXX -assignment YYYYYYY
```

## Writing to File
To write the database to a file, you can do the same as updating:
  + write all stats for all active courses you have
  + write all stats for a singleular course
  + write stats for a single assignment
The output will be `YYYYYYY.csv` with the column header being the grader's names and the row header being the question name. YYYYYYY is again the assignment ID

By default, the program will write a file for each assignment in every course in the entire 'databse'. 

To write all a file for each assignment for each class leave the course flag empty:
```
grading-stats
```

To update all assignments in a single course leave the assignment flag empty:
```
grading-stats -course XXXXXX
```

To update a single assignment, give both a course and assignment value:
```
grading-stats -course XXXXXX -assignment YYYYYYY
```

### Printing to stdout

If you don't want to render the csv yourself, you can pass in the '-print' flag and it will print out a rendered table to stdout.

For example to pretty print a table for a single assignment
```
grading-stats -course XXXXXX -assignment YYYYYYY -print
```

TODO
  + update only those that are not 100% graded
  + interactive mode