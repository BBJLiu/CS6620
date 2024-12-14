import boto3

def lambda_handler(event, context):
    s3_client = boto3.client('s3')
    bucket_name = 'weihao-cdk-bucket'  

    # Retrieve the list of objects in the bucket
    response = s3_client.list_objects_v2(Bucket=bucket_name)

    # Check if the bucket is not empty
    if 'Contents' in response:
        # Find the object with the largest size
        largest_object = max(response['Contents'], key=lambda obj: obj['Size'])

        # Delete the largest object
        s3_client.delete_object(Bucket=bucket_name, Key=largest_object['Key'])
        print(f"Deleted {largest_object['Key']} from {bucket_name}")

    else:
        print("No objects found in the bucket.")
