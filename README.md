# ml-eng-test

## REQUIREMENTS
- Docker

## RUN

1. git pull https://github.com/dwisniewski1993/ml-eng-test.git
2. cd ml-eng-test
3. docker build -t mlegtest .
4. docker run -it mlengtest

## EXECUTE
- Go to PDFs location (eg. PageInfo catalog) and run:
- curl -X POST -F "image=@A-010.00 - DOOR SCHEDULE.pdf" -F "type=tables" http://localhost:5000/task
