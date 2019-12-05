# Service: Tools
/tools API.


## Testing
### Unit Testing
Python version 3.6 is used with the lambda, so a matching local python environment is also used:
```
pyenv local 3.6.8
```

To execute `pytest` against our `tests` folder to run our initial unit tests:
```
pytest
```

### Local API Testing
Local testing of the API, ensures that API and lambda function are correctly configured.
1. Start API
    ```
    sam local start-api
    ```
1. Use local endpoint in browser or with Postman: `http://localhost:3000/solve`

## Deployment
### Create an s3 bucket for SAM builds
```
aws cloudformation create-stack --stack-name sam-builds-tools-test --template-body file://sam-builds-bucket.yaml
```

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

### Deploy to staging environment
```
aws cloudformation create-stack \
    --template-body file://packaged.yaml \
    --stack-name Service-Tools-staging \
    --capabilities CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND \
    --parameters ParameterKey=Environment,ParameterValue=staging
```

aws cloudformation create-stack --region us-east-1 --stack-name Web-SSL-Test \
--template-body file://web-sslcert.yaml \
--parameters ParameterKey=Environment,ParameterValue=test

## Logging
Get logs for last 10 minutes:
```
sam logs -n Function --stack-name Service-Tools-Staging
```
