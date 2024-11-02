from aws_cdk import (
    App,  
    Stack,
    Duration,
    CfnOutput,
    aws_s3 as s3,
    aws_dynamodb as dynamodb,
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_events as events,
    aws_events_targets as targets,
    aws_s3_notifications as s3_notifications,
)
from constructs import Construct  

class BackupSystemStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create an S3 bucket for the source
        bucket_src = s3.Bucket(self, "BucketSRC")

        # Create an S3 bucket for the destination
        bucket_dst = s3.Bucket(self, "BucketDST")

        # Create a DynamoDB table
        table = dynamodb.Table(
            self, "TableT",
            partition_key=dynamodb.Attribute(name="OriginalObjectName", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="CopyTimestamp", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST
        )

        # IAM role for Lambda functions
        lambda_role = iam.Role(self, "LambdaExecutionRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"),
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaDynamoDBExecutionRole"),
            ]
        )

        # Create the Replicator Lambda function
        replicator_function = _lambda.Function(
            self, "Replicator",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="replicator.handler",
            code=_lambda.Code.from_asset("lambda"),
            environment={
                "BUCKET_SRC": "BucketSrc",  
                "BUCKET_DST": "BucketDst",  
                "TABLE_NAME": "TableT", 
            },
            role=lambda_role
        )

        # Grant the Lambda function permissions
        bucket_src.grant_read(replicator_function)
        bucket_dst.grant_write(replicator_function)
        table.grant_read_write_data(replicator_function)

        # Add S3 notification for the source bucket to trigger the Replicator
        bucket_src.add_event_notification(s3.EventType.OBJECT_CREATED, s3_notifications.LambdaDestination(replicator_function))
        bucket_src.add_event_notification(s3.EventType.OBJECT_REMOVED, s3_notifications.LambdaDestination(replicator_function))

        # Create the Cleaner Lambda function
        cleaner_function = _lambda.Function(
            self, "Cleaner",
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler="cleaner.handler",
            code=_lambda.Code.from_asset("lambda"),
            environment={
                "TABLE_NAME": table.table_name,  # Use the actual table name
            },
            role=lambda_role
        )

        # Create a CloudWatch Events rule to trigger the Cleaner every minute
        rule = events.Rule(
            self, "Rule",
            schedule=events.Schedule.rate(Duration.minutes(1))  # Use a reasonable duration
        )
        rule.add_target(targets.LambdaFunction(cleaner_function))

        # Output the bucket names and table name
        CfnOutput(self, "BucketSrcOutput", value=bucket_src.bucket_name)
        CfnOutput(self, "BucketDstOutput", value=bucket_dst.bucket_name)
        CfnOutput(self, "TableNameOutput", value=table.table_name)

app = App()  # Ensure App is instantiated correctly
BackupSystemStack(app, "BackupSystem", env={
    'account': '888577057759', 
    'region': 'us-west-1'
})
app.synth()
