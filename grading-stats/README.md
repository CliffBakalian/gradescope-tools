# Gradescope Grading Stats

***Disclaimer: Gradescope has no API so this is a scraper. Sometimes Gradescope changes it's formatting. Just make an issue and I'll update it***

***Now in Selenium since gradescope changed thier page to be dynamic***

## installation 

You should be able to clone this repository and just run `main.py`  

## Structure of files

This program works by scraping gradescope and creating local files that stores
the scrapped data. These files are in json format. 

Some background first: 
Gradescope urls look like 
https://www.gradescope.com/courses/XXXXX/assignments/YYYYYYY/ 
where XXXXXX is the course id and YYYYYYY is the assignment id.

The files created (and some of the consequent data) will be based on these ids. 
These files look like the following:

  + `course_id.json`- Contains the following information:
      - Course Name
      - Course ID (link)
      - List of assignments - Each Assignment has the following information: 
        + Assignment Name
        + Assignment ID (link)
        + If the assignment is published or not
        + List of questions - Each Question has the following information:
          - Question Name
          - Question ID (link: https://www.gradescope.com/courses/XXXXX/questions/ZZZZZZZZ/submissions where ZZZZZZZZ is the question ID)
          - Percentage Done
      - List of grader names
  + `assignment_id.json` - Contains the following information:
      - List of Questions - Each question has the following information:
          - Question Name
          - Question ID (link)
          - List of counts - Each question has a key of a grader's name and a value of the number they graded

**Question**: Why the duplicate data of Question information/Why have a separate assignment file?  
**Answer**: Program should only update/scrape what is needed. 
`course_id.json` indicates to program what needs to be updated (based off the question percentage done). 
`assignment_id.json` is the file that will be updated and overwritten consistently.

### Sample Files

#### `course_id.json`
Here is an example of `course_id.json` (named `123456.json`):
```json
{
  "name": "Course1",
  "link": "123456",
  "assignments": [
    {
      "name": "assignment one",
      "link": "0000001",
      "published": false,
      "questions": [
        {
          "name": "Named Question 1",
          "link": "10000001",
          "percentdone": 100
        },
        {
          "name": "2:",
          "link": "10000002",
          "percentdone": 45 
        }
      ]
    },
    {
      "name": "assignment 2",
      "link": "0000002",
      "published": true,
      "questions": [
        {
          "name": "Q1",
          "link": "20000001",
          "percentdone": 100
        }
      ]
    }
  ],
  "graders": [
    "Cliff Bakalian",
    "Grader 1",
    "Grader 2"
  ]
}
```

#### `assignment_id.json`

Here is an example of `assignment_id.json` (named `0000001.json` corresponding to the above assignment one):
```json
{
  "questions":[
    {
      "name": "Named Question 1",
      "link": "10000001",
      "counts": {
        "Cliff Bakalian": 20,
        "Grader 1": 19,
        "Grader 2": 21
      }
    },
    {
      "name": "2:",
      "link": "10000002",
      "counts": {
        "Cliff Bakalian": 20,
        "Grader 1": 7
      }
    }
  ]
}
```

## Running the program
***TODO: Need to finalize the interface***
You can currently work with `shell.py`.  
The program accepts the following command line arguments:
```bash
python shell.py update <course> [--all|--only-needed]


python shell.py --first-time
```

`--first-time` should be run ***once and only once***. If something got messed up
you will need to delete all created files before you rerun.  

`--only-needed` will only update questions that are not 100 percent graded on assignments that have not been published on gradescope. The edge case is that Gradescope does sound rounding when reporting percent complete so its possible an assignment is not fully graded but Gradescope says 100% (say 997 out of 1000 are graded).  

`--all` will update all questions for all assignments even if they are published or at 100%.

### Printing to csv 
You can use the following command to print the grading stats to a csv file:
```
python shell.py update <course> <assignment>
```
This does no scraping or updating so you will have to run those commands first.
