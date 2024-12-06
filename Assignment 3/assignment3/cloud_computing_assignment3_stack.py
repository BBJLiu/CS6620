from aws_cdk import Stack, RemovalPolicy
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_dynamodb as dynamodb
from constructs import Construct
from aws_cdk import (
    aws_sns as sns,
    aws_sqs as sqs,
    aws_sns_subscriptions as subs,
    aws_s3_notifications as s3n,
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_dynamodb as ddb
)


class CloudComputingAssignment3Stack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create the S3 bucket with a unique name
        s3_bucket = s3.Bucket(
            self,
            "TestBucket",
            bucket_name="weihao-cdk-bucket",  # Updated unique name
            removal_policy=RemovalPolicy.DESTROY 
        )

        # Create an SNS topic
        sns_topic = sns.Topic(self, "MySNSTopic")

        # Create SQS queues
        size_tracking_queue = sqs.Queue(self, "SizeTrackingQueue")
        logging_queue = sqs.Queue(self, "LoggingQueue")

        # Subscribe SQS queues to the SNS topic
        sns_topic.add_subscription(subs.SqsSubscription(size_tracking_queue))
        sns_topic.add_subscription(subs.SqsSubscription(logging_queue))

        # Configure S3 bucket to send events to the SNS topic
        s3_bucket.add_event_notification(s3.EventType.OBJECT_CREATED_PUT, s3n.SnsDestination(sns_topic))
        s3_bucket.add_event_notification(s3.EventType.OBJECT_REMOVED_DELETE, s3n.SnsDestination(sns_topic))

        # Create the DynamoDB table with a unique name
        dynamodb_table = dynamodb.Table(
            self,
            "S3ObjectSizeHistory",
            table_name="cdk-S3-object-size-history", 
            partition_key=dynamodb.Attribute(name="bucket_name", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="timestamp", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY 
        )

        # Output resource names for confirmation
        print(f"S3 bucket '{s3_bucket.bucket_name}' and DynamoDB table '{dynamodb_table.table_name}' created successfully.")
