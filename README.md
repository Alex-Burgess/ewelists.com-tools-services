# ewelists.com-tools-backend
Backend Serverless functions and APIs for tools relating to the [Ewelists](https://github.com/Alex-Burgess/ewelists.com) application.

The frontend has not been started yet.

## Contents

- [General](#general)
  - [Create a new SAM project](#create-a-new-sam-project)
  - [Builds Bucket](#builds-bucket)
  - [Unit Testing](#unit-testing)
  - [Local Lambda Function Tests](#local-lambda-function-tests)
  - [Local API Testing](#local-api-testing)
  - [Logging](#logging)
- [API Details](#api-details)
- [NotFound Check](#notfound-check)

## General

### Setup Environment
The local python environment is kept in sync with the python environment we use in pipeline codebuild project, which is currently 3.7.6.
```
pyenv install 3.7.6
pyenv local 3.7.6
pip install moto pytest requests_mock boto3
pip install -r Lists/requirements.txt
```

### Create a new SAM project

To create a new SAM serverless api and function project structure:
```
sam init --runtime python3.7 --name lists
```

### Builds Bucket

When packaging a service for deployment to the test environment, an S3 bucket is required to store the builds.  To create this:
```
aws s3 mb s3://sam-builds-tools-test
```

### Unit Testing
Python version 3.6 is used with the lambda, so a matching local python environment is also used:
```
pyenv local 3.6.8
```

Example test executions:
```
All: pytest
File: pytest tests/test_create.py
Class: pytest tests/test_create.py::TestPutItemInTable
Unit Test: pytest tests/test_create.py::TestCreateMain::test_create_main
```

### Local Lambda Function Tests
Lambda functions can be invoked locally as follows:
```
sam local invoke CreateListFunction --event events/create_list.json --env-vars env_vars/test_env.json
```

### Local API Testing
APIs can also be testing locally.  For example, running the command below in the Lists directory, will make a local endpoint available at `http://localhost:3000/lists`.
```
sam local start-api
```

### Logging
Get logs for last 10 minutes:
```
sam logs -n CreateListFunction --stack-name Service-lists-test
```

Tail logs, e.g. whilst executing function test:
```
sam logs -n CreateListFunction --stack-name Service-lists-test --tail
```

## API Details

### Deploy to test environment
```
sam build

sam package \
    --output-template-file packaged.yaml \
    --s3-bucket sam-builds-tools-test

sam deploy \
    --template-file packaged.yaml \
    --stack-name Service-Tools-test \
    --capabilities CAPABILITY_NAMED_IAM
```

## NotFound Check
The notfound_check function, is part of the Tools SAM package.  It is triggered to run by a CloudWatch Event Rule, on a periodic basis.

It requires the following ssm parameters to be created.
```
aws ssm put-parameter --name /Ewelists/AlertEmail --type String --value "contact@ewelists.com"
aws ssm put-parameter --name /Ewelists/AlertNumber --type String --value "+4479004*****"
```
