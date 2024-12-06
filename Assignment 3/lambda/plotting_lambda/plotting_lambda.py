import boto3
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os
from decimal import Decimal

# Initialize Boto3 clients and resources
dynamodb = boto3.resource('dynamodb')
s3_client = boto3.client('s3')

# Environment variables for the DynamoDB table and S3 bucket
DYNAMODB_TABLE_NAME = os.getenv('DYNAMODB_TABLE_NAME')
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')

def lambda_handler(event, context):
    """Lambda function to generate a plot from DynamoDB data and upload it to S3."""
    
    # Retrieve the DynamoDB table
    table = dynamodb.Table(DYNAMODB_TABLE_NAME)
    
    # Define the time window for data query (last 10 seconds)
    now = datetime.utcnow()
    ten_seconds_ago = now - timedelta(seconds=10)
    now_str = now.strftime('%Y-%m-%d %H:%M:%S')
    ten_seconds_ago_str = ten_seconds_ago.strftime('%Y-%m-%d %H:%M:%S')

    # Query the DynamoDB table for bucket size data within the time window
    response = table.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key('bucket_name').eq(S3_BUCKET_NAME) &
                               boto3.dynamodb.conditions.Key('timestamp').between(ten_seconds_ago_str, now_str)
    )
    
    # Retrieve and process query results
    items = response.get('Items', [])
    if not items:
        return {
            'statusCode': 200,
            'body': 'No data found in the last 10 seconds.'
        }

    # Extract timestamps and bucket sizes for plotting
    timestamps = [datetime.strptime(item['timestamp'], '%Y-%m-%d %H:%M:%S') for item in items]
    sizes = [float(item['bucket_size']) for item in items]
    max_size = max(sizes) if sizes else 0

    # Plot the data
    plt.figure()
    plt.plot(timestamps, sizes, label='Bucket Size Over Time', marker='o')
    plt.axhline(y=max_size, color='r', linestyle='--', label=f'Max Size: {max_size}')
    plt.xlabel('Timestamp')
    plt.ylabel('Size (bytes)')
    plt.legend()

    # Save the plot to a temporary file
    plot_file_path = '/tmp/plot.png'
    plt.savefig(plot_file_path)

    # Upload the plot file to S3
    with open(plot_file_path, 'rb') as plot_file:
        s3_client.put_object(Bucket=S3_BUCKET_NAME, Key='plot.png', Body=plot_file)

    return {
        'statusCode': 200,
        'body': 'Plot created and uploaded to S3 successfully.'
    }
