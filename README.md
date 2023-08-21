# LambdaEventTriggering
Every 24 hours, my Lambda function keeps me informed about my GitHub repositories. It queries DynamoDB for the last count, compares with current GitHub count, and updates DynamoDB if they differ. An SNS email alerts me of changes, ensuring timely updates on my repository activity.
