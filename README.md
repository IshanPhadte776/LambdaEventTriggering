# LambdaEventTriggering
Every 24 hours, my Lambda function keeps me informed about my GitHub repositories. It queries DynamoDB for the last count, compares with current GitHub count, and updates DynamoDB if they differ. An SNS email alerts me of changes, ensuring timely updates on my repository activity.


![GitHub Logo](https://github.com/IshanPhadte776/LambdaEventTriggering/blob/main/Lambda-Event-Triggering.png)

1. Cloudwatch triggers the lambda function every 24 hours
2. Lambda makes a Github API Request
3. Github Responses with Repo Data from the current day
4. Lambda makes a call to the DynamoDB table for Repo Data
5. DynamoDB Responses with Repo Data from the day prior
6. Lambda will write the current data to the DynamoDB table
7. SNS triggers an email to the subscribed user

