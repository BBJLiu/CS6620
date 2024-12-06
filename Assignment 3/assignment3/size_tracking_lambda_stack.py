from aws_cdk import (
    Stack,
    Duration,
    aws_s3_notifications as s3_notifications,
    aws_lambda as _lambda,
    aws_dynamodb as dynamodb,
    aws_s3 as s3,
    aws_sqs as sqs,
    aws_iam as iam,
    aws_lambda_event_sources as lambda_sources,
    CfnOutput
)
from constructs import Construct

class SizeTrackingLambdaStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Import the existing DynamoDB table using its name
        dynamodb_table = dynamodb.Table.from_table_name(
            self,
            "ImportedS3ObjectSizeHistory",
            table_name="cdk-S3-object-size-history"
        )

        # Import the existing SQS queue using its name
        size_tracking_queue = sqs.Queue.from_queue_arn(
            self,
            "ImportedSizeTrackingQueue",
            queue_arn="arn:aws:sqs:us-east-1:941377123459:CloudComputingAssignment3Stack-SizeTrackingQueue7EE021D2-021aYRklUUDL"  # Replace with actual ARN
        )

        # Define the Lambda function
        size_tracking_lambda = _lambda.Function(
            self,
            "SizeTrackingLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="size_tracking_lambda.lambda_handler",
            code=_lambda.Code.from_asset("lambda/size_tracking_lambda"),  # Path to the Lambda code
            environment={
                "DYNAMODB_TABLE_NAME": dynamodb_table.table_name,
            },
            timeout=Duration.seconds(25)
        )

        # Grant the Lambda function permissions to access the DynamoDB table

        size_tracking_lambda.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonDynamoDBFullAccess")
        )

        # Grant the Lambda function permissions to access the s3
        size_tracking_lambda.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess")
        )

        # Grant the Lambda function permissions to read from the SQS queue
        size_tracking_lambda.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSQSFullAccess")
        )

        # Add the SQS queue as an event source for the Lambda function
        sqs_event_source = lambda_sources.SqsEventSource(size_tracking_queue, batch_size=10)
        size_tracking_lambda.add_event_source(sqs_event_source)

        # Print outputs for easy reference
        CfnOutput(self, "LambdaFunctionName", value=size_tracking_lambda.function_name)
        CfnOutput(self, "DynamoDBTableName", value=dynamodb_table.table_name)
        CfnOutput(self, "SQSQueueUrl", value=size_tracking_queue.queue_url)