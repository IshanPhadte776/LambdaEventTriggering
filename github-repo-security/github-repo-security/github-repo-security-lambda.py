import urllib.request
import json
import boto3
import os


dynamodb = boto3.client('dynamodb')


def lambda_handler(event, context):
    #access_token = ''
    access_token = os.environ.get('ACCESS_TOKEN')

    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    api_url = "https://api.github.com/users/IshanPhadte776/repos"
    
    req = urllib.request.Request(api_url, headers=headers)
    response = urllib.request.urlopen(req)
    
    data = json.loads(response.read().decode())
    
    
    # Extract "name" and "last-updated" elements from each element
    api_repo_list = []
    
    for element in data:
        repo_name = element.get('name', 'NoRepoName')
        pushed_at = element.get('pushed_at', 'NoLastUpdated')
    
        repo_info = {'RepoName': repo_name, 'pushed_at': pushed_at}
        api_repo_list.append(repo_info)
    
    # # Retrieve the previous repo count from DynamoDB
    # user_id = 'IshanPhadte776'  # Replace with your GitHub username
    # dynamodb_response  = dynamodb.get_item(TableName='GitHubRepoSecurityTable', Key={'user_id': {'S': user_id}})
    # prev_repo_count = int(dynamodb_response .get('Item', {}).get('RepoCount', {'N': '0'}).get('N', '0'))
    
    # # Update the DynamoDB table with the current repo count
    # dynamodb.put_item(TableName='GitHubRepoSecurityTable', Item={'user_id': {'S': user_id}, 'RepoCount': {'N': str(num_repos)}})
    

    dynamoDB_repo_list = []
    
    dynamodb_response   = dynamodb.scan(TableName='AllGithubRepos')
    for item in dynamodb_response  .get('Items', []):
        repo_name = item.get('RepoName', {}).get('S', 'NoRepoName')
        pushed_at = item.get('LastUpdated', {}).get('S', 'NoLastUpdated')
    
        repo_info = {'RepoName': repo_name, 'pushed_at': pushed_at}
        dynamoDB_repo_list.append(repo_info)
    
    #print(dynamoDB_repo_list)
    
        # Create dictionaries with repo names as keys for easy comparison
    api_repo_dict = {repo['RepoName']: repo for repo in api_repo_list}
    dynamoDB_repo_dict = {repo['RepoName']: repo for repo in dynamoDB_repo_list}
    
    # Lists to store differences
    new_repos = []
    old_repos = []
    updated_repos = []
    
        # Check repositories present in api_repo_list but not in dynamoDB_repo_list
    for repo_name, repo_api in api_repo_dict.items():
        if repo_name not in dynamoDB_repo_dict:
            new_repos.append({'RepoName': repo_name, 'API_Info': repo_api})
    
    # Check repositories present in dynamoDB_repo_list but not in api_repo_list
    for repo_name, repo_dynamoDB in dynamoDB_repo_dict.items():
        if repo_name not in api_repo_dict:
            old_repos.append({'RepoName': repo_name, 'DynamoDB_Info': repo_dynamoDB})
    
    # Compare attributes for common repositories
    for repo_name, repo_api in api_repo_dict.items():
        if repo_name in dynamoDB_repo_dict:
            repo_dynamoDB = dynamoDB_repo_dict[repo_name]
            if repo_api != repo_dynamoDB:
                updated_repos.append({'RepoName': repo_name, 'API_Info': repo_api, 'DynamoDB_Info': repo_dynamoDB})

    # print("\nNew Repos:")
    # print(new_repos)
    
    # print("\nOld Repos:")
    # print(old_repos)
    
    # print("\nRepos with Updates:")
    # print(updated_repos)
    
    
    for element in new_repos:
        RepoName = element['RepoName']
        LastUpdated  = element['API_Info']['pushed_at']
        
        # Create a new item to add to the DynamoDB table
        item = {
            'RepoName': {'S': RepoName},
            'LastUpdated': {'S': LastUpdated}  # Use the appropriate key for LastUpdated
        }
        
        # Add the new item to the DynamoDB table
        dynamodb.put_item(
            TableName="AllGithubRepos",
            Item=item
        )
        
    for element in old_repos:
        repo_name = element['RepoName']
        last_updated = element['DynamoDB_Info']['pushed_at']  # Use the appropriate key for LastUpdated
    
        # Delete the item from the DynamoDB table using the composite primary key
        dynamodb.delete_item(
            TableName="AllGithubRepos",
            Key={
                'RepoName': {'S': repo_name},
                'LastUpdated': {'S': last_updated}
            }
        )

    for element in updated_repos:
        repo_name = element['RepoName']
        new_pushed_at = element['API_Info']['pushed_at']  # Use the appropriate key for the pushed_at attribute
    
        # Delete the old item using delete_item
        dynamodb.delete_item(
            TableName="AllGithubRepos",
            Key={
                'RepoName': {'S': repo_name},
                'LastUpdated': {'S': element['DynamoDB_Info']['pushed_at']}
            }
        )
        
        # Add the updated item as a new item using put_item
        item = {
            'RepoName': {'S': repo_name},
            'LastUpdated': {'S': new_pushed_at}
        }
    
        dynamodb.put_item(
            TableName="AllGithubRepos",
            Item=item
        )




            
    message = (
        f"Hello Ishan,\n\n"
        f"{'' if (new_repos or old_repos or updated_repos) else 'In the last 24 hours, No GitHub Activity Occurred on your GitHub Account.'}\n"
        f"{'' if not new_repos else 'In the last 24 hours, The following Repos were created:'}\n"
        f"{', '.join([repo['RepoName'] for repo in new_repos])}\n"
        f"{'' if not old_repos else 'In the last 24 hours, The following Repos were deleted:'}\n"
        f"{', '.join([repo['RepoName'] for repo in old_repos])}\n"
        f"{'' if not updated_repos else 'In the last 24 hours, The following Repos were updated:'}\n"
        f"{', '.join([repo['RepoName'] for repo in updated_repos])}\n"
        f"Regards,\n"
        f"\n"
        f"Your Personal AWS Security"
    )
    


    sns_client = boto3.client('sns')
    topic_arn = 'arn:aws:sns:us-west-2:822314191852:github-repo-security-sns'
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
        
        