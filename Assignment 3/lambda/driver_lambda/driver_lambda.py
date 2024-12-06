import boto3
import os
import time
import requests

# Initialize S3 client
s3_client = boto3.client('s3')

# Environment variables for S3 bucket name and Plotting Lambda API URL
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')
PLOTTING_API_URL = os.getenv('PLOTTING_API_URL')

def create_object(bucket_name, key, content):
    s3_client.put_object(Bucket=bucket_name, Key=key, Body=content)
    print(f"Created object {key} with content: {content}")

def update_object(bucket_name, key, content):
    s3_client.put_object(Bucket=bucket_name, Key=key, Body=content)
    print(f"Updated object {key} with new content: {content}")

def delete_object(bucket_name, key):
    s3_client.delete_object(Bucket=bucket_name, Key=key)
    print(f"Deleted object {key}")

def call_plotting_lambda():
    try:
        response = requests.get(PLOTTING_API_URL)

        if response.status_code == 200:
            print(f"Plotting Lambda API Response: {response.status_code}, {response.text}")
        else:
            print(f"Failed to call Plotting Lambda API: {response.status_code}, {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"Error calling Plotting Lambda API: {e}")

def lambda_handler(event, context):
    # Perform S3 operations with delays
    create_object(S3_BUCKET_NAME, 'assignment1.txt', 'Empty Assignment 1')
    time.sleep(2)

    update_object(S3_BUCKET_NAME, 'assignment1.txt', 'Empty Assignment 2222222222')
    time.sleep(2)

    delete_object(S3_BUCKET_NAME, 'assignment1.txt')
    time.sleep(2)

    create_object(S3_BUCKET_NAME, 'assignment2.txt', '33')
    time.sleep(2)

    # Trigger the Plotting Lambda function via API
    call_plotting_lambda()

    return {
        'statusCode': 200,
        'body': 'Driver Lambda executed successfully and triggered Plotting Lambda.'
    }
