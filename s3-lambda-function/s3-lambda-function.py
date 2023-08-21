import urllib.request
import json
import boto3

dynamodb = boto3.client('dynamodb')


def lambda_handler(event, context):
    access_token = ''
    
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    api_url = "https://api.github.com/users/IshanPhadte776"
    
    req = urllib.request.Request(api_url, headers=headers)
    response = urllib.request.urlopen(req)
    
    data = json.loads(response.read().decode())
    #num_repos = len(data)
    num_repos = data.get('public_repos', 0)  # Get the value of public_repos field

    print(num_repos)
    
    # Retrieve the previous repo count from DynamoDB
    user_id = 'IshanPhadte776'  # Replace with your GitHub username
    dynamodb_response  = dynamodb.get_item(TableName='RepoCountTable', Key={'user_id': {'S': user_id}})
    prev_repo_count = int(dynamodb_response .get('Item', {}).get('RepoCount', {'N': '0'}).get('N', '0'))
    
    # Update the DynamoDB table with the current repo count
    dynamodb.put_item(TableName='RepoCountTable', Item={'user_id': {'S': user_id}, 'RepoCount': {'N': str(num_repos)}})
    
    
    print(prev_repo_count)
    
    if num_repos > prev_repo_count:
        print(f'Number of repositories increased to: {num_repos}')
        
        diff = num_repos - prev_repo_count
        message = (
            f"Hello Ishan,\n\n"
            f"In the last 24 hours, the number of GitHub Repositories increased by {diff}.\n"
            f"Regards,\n"
            f"\n"
            f"Your Personal AWS Security"
        )
        
        sns_client = boto3.client('sns')
        topic_arn = 'arn:aws:sns:us-west-2:822314191852:s3-lambda-sns'
        sns_client.publish(
            TopicArn=topic_arn,
            Subject='Number of Repos Increased in the last 24 Hours',
            Message= message
        )
        
    elif num_repos < prev_repo_count:
        print(f'Number of repositories decreased to: {num_repos}')
        diff = prev_repo_count - num_repos
        
        message = (
            f"Hello Ishan,\n\n"
            f"In the last 24 hours, the number of GitHub Repositories decreased by {diff}.\n"
            f"Regards,\n"
            f"\n"
            f"Your Personal AWS Security"
        )
        
        sns_client = boto3.client('sns')
        topic_arn = 'arn:aws:sns:us-west-2:822314191852:s3-lambda-sns'
        sns_client.publish(
            TopicArn=topic_arn,
            Subject='Number of Repos Decreased in the last 24 Hours',
            Message= message
        )
        
    
    else:
        print ("No Change to Number of Repos in the last 24 Hours")


        message = (
            f"Hello Ishan,\n\n"
            f"In the last 24 hours, the number of GitHub Repositories hasn't changed.\n"
            f"Regards,\n"
            f"\n"
            f"Your Personal AWS Security"
        )


        sns_client = boto3.client('sns')
        topic_arn = 'arn:aws:sns:us-west-2:822314191852:s3-lambda-sns'
        sns_client.publish(
            TopicArn=topic_arn,
            Subject='Number of Repos has not changed',
            Message= message
        )
    
    
    response_data = response.read().decode()
    return {
        'statusCode': 200,
        'body': response_data
    }
        
        
    