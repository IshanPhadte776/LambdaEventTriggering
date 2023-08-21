#!/bin/bash
#Runs Script in Debug Mode
set -x

# Store the AWS account ID in a variable
aws_account_id=$(aws sts get-caller-identity --query 'Account' --output text)

# Print the AWS account ID from the variable
echo "AWS Account ID: $aws_account_id"

# Set AWS region and bucket name
aws_region="us-west-2"
lambda_func_name="github-repo-security-lambda"
role_name="github-repo-security"
email_address="ishanphadte@gmail.com"

# Create IAM Role for the project
#Premissions for lambda, dynamodb, sns and cloud
role_response=$(aws iam create-role --role-name github-repo-security --assume-role-policy-document '{
  "Version": "2012-10-17",
  "Statement": [{
    "Action": "sts:AssumeRole",
    "Effect": "Allow",
    "Principal": {
      "Service": [
         "lambda.amazonaws.com",
         "sns.amazonaws.com",
          "dynamodb.amazonaws.com",
          "logs.amazonaws.com"
      ]
    }
  }]
}')
#jq is a json parser
# Extract the role ARN from the JSON response and store it in a variable
role_arn=$(echo "$role_response" | jq -r '.Role.Arn')

# Print the role ARN
echo "Role ARN: $role_arn"

# Attach Permissions to the Role
aws iam attach-role-policy --role-name $role_name --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess
aws iam attach-role-policy --role-name $role_name --policy-arn arn:aws:iam::aws:policy/AWSLambda_FullAccess
aws iam attach-role-policy --role-name $role_name --policy-arn arn:aws:iam::aws:policy/AWSLambdaBasicExecutionRole
aws iam attach-role-policy --role-name $role_name --policy-arn arn:aws:iam::aws:policy/AmazonSNSFullAccess

# Create a Lambda function
#uploads the zip file and aws will do the extractions
aws lambda create-function \
  --region "$aws_region" \
  --function-name $lambda_func_name \
  --runtime "python3.8" \
  --handler "github-repo-security-lambda.lambda_handler" \
  --memory-size 128 \
  --timeout 30 \
  --role "arn:aws:iam::$aws_account_id:role/$role_name" \
  --zip-file "fileb://./github-repo-security.zip"


aws dynamodb create-table \
  --table-name GitHubRepoSecurityTable \
  --attribute-definitions AttributeName=user_id,AttributeType=S AttributeName=RepoCount,AttributeType=N \
  --key-schema AttributeName=user_id,KeyType=HASH \
  --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5


# Create an SNS topic and save the topic ARN to a variable
topic_arn=$(aws sns create-topic --name github-repo-security-sns --output json | jq -r '.TopicArn')

# Print the TopicArn
echo "SNS Topic ARN: $topic_arn"


aws events put-rule \
  --name "RunGithubRepoSecurity" \
  --schedule-expression "rate(24 hours)" \
  --state "ENABLED"

lambda_arn="arn:aws:lambda:$aws_region:$aws_account_id:function:$lambda_func_name"
aws events put-targets \
  --rule "RunGithubRepoSecurity" \
  --targets "Id"="1","Arn"="$lambda_arn"



# Add SNS publish permission to the Lambda Function
#aws sns subscribe \
  #--topic-arn "$topic_arn" \
  #--protocol email \
  #--notification-endpoint "$email_address"

# Publish SNS
aws sns publish \
  #--topic-arn "$topic_arn" \
  #--subject "A new Repo in Github" \
  #--message "Hello, A New Repo was uploaded in Github"


