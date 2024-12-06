from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as _lambda,
    aws_s3 as s3,
    aws_iam as iam,
    aws_dynamodb as dynamodb,
    aws_apigateway as apigateway
)
from constructs import Construct


class DriverLambdaStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Import the existing S3 bucket
        s3_bucket = s3.Bucket.from_bucket_name(
            self,
            "ImportedS3Bucket",
            bucket_name="weihao-cdk-bucket"
        )

        # Define Requests Layer for external HTTP requests
        requests_layer = _lambda.LayerVersion(
            self,
            "RequestsLayer",
            code=_lambda.Code.from_asset("requests_layer.zip"),  # Ensure this path points to the correct zip file
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_9],
            description="A layer with requests library dependencies"
        )

        # Define the Driver Lambda function
        driver_lambda = _lambda.Function(
            self,
            "DriverLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="driver_lambda.lambda_handler",
            code=_lambda.Code.from_asset("lambda/driver_lambda"),  # Folder containing Lambda code
            layers=[requests_layer],  # Attach the requests layer
            environment={
                "S3_BUCKET_NAME": s3_bucket.bucket_name,
                "PLOTTING_API_URL": "https://siu9t5pt2d.execute-api.us-east-1.amazonaws.com/prod"
            },
            timeout=Duration.minutes(1)
        )

        # Define and attach full access policies for S3 and DynamoDB
        full_s3_policy = iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess")
        full_dynamodb_policy = iam.ManagedPolicy.from_aws_managed_policy_name("AmazonDynamoDBFullAccess")

        driver_lambda.role.add_managed_policy(full_s3_policy)
        driver_lambda.role.add_managed_policy(full_dynamodb_policy)

        # Output the API endpoint URL for reference if needed
        print("Driver Lambda configured with requests layer and environment variables.")
