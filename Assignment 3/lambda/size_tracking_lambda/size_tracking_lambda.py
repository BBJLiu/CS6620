import json
import boto3
import time

def lambda_handler(event, context):
    s3 = boto3.client('s3')
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('cdk-S3-object-size-history')

    for record in event['Records']:
        message_body = json.loads(record['body'])
        sns_message = json.loads(message_body['Message'])

        # Debug: Print the sns_message to see its structure
        print("SNS Message:", json.dumps(sns_message))

        if 'Records' in sns_message:
            for s3_event in sns_message['Records']:
                bucket_name = s3_event['s3']['bucket']['name']
                object_key = s3_event['s3']['object']['key']
                
                print(f"Processing {object_key} in {bucket_name}")
                
                # Calculate total size and object count of the bucket
                try:
                    response = s3.list_objects_v2(Bucket=bucket_name)
                    total_size = sum(obj['Size'] for obj in response.get('Contents', []))
                    object_count = response['KeyCount']

                    # Write the computed data to DynamoDB
                    table.put_item(
                        Item={
                            'bucket_name': bucket_name,
                            'timestamp': str(int(time.time())),
                            'total_size': total_size,
                            'object_count': object_count
                        }
                    )
                except Exception as e:
                    print(f"Error processing bucket {bucket_name}: {str(e)}")
        else:
            print("No 'Records' key in SNS Message:", json.dumps(sns_message))

