from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_sqs as sqs,
    Duration,
    aws_logs as logs,
    aws_lambda_event_sources as lambda_sources,
    aws_cloudwatch as cloudwatch,
    CfnOutput
)
from constructs import Construct

class LoggingLambdaStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Define the Lambda function
        logging_lambda = _lambda.Function(
            self,
            "LoggingLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="logging_lambda.lambda_handler",
            code=_lambda.Code.from_asset("lambda/logging_lambda"), 
            timeout=Duration.seconds(30),
            memory_size=128
        )

        # Create the log group and log stream if they don't exist
        log_group = logs.LogGroup(
            self,
            "LogGroup",
            log_group_name="/aws/lambda/s3_operation_logs",
            retention=logs.RetentionDays.ONE_WEEK 
        )

        logs.LogStream(
            self,
            "LogStream",
            log_group=log_group,
            log_stream_name="s3_operations"
        )

        # Add permissions to the Lambda to write to CloudWatch Logs
        logging_lambda.add_to_role_policy(iam.PolicyStatement(
            actions=["logs:CreateLogStream", "logs:PutLogEvents"],
            resources=[log_group.log_group_arn]  # Using just the log group ARN
        ))

        # Explicit permission to start queries on CloudWatch Logs
        logging_lambda.add_to_role_policy(iam.PolicyStatement(
            actions=["logs:StartQuery", "logs:GetQueryResults", "logs:StopQuery"],
            resources=[log_group.log_group_arn]
        ))

         # Create a Metric Filter
        metric_filter = logs.MetricFilter(
            self,
            "ObjectSizeChangeMetricFilter",
            log_group=log_group,
            metric_namespace="Assignment4App",
            metric_name="TotalObjectSize",
            filter_pattern=logs.FilterPattern.exists("$.size_delta"),
            metric_value="$.size_delta" 
        )

        # Create a CloudWatch Alarm
        alarm = cloudwatch.Alarm(
            self,
            "ObjectSizeThresholdAlarm",
            metric=metric_filter.metric(statistic="sum", period=Duration.minutes(1)),
            threshold=20,
            evaluation_periods=1,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD
        )

        # Import the SQS queue using its ARN
        queue = sqs.Queue.from_queue_arn(
            self,
            "LoggingQueue",
            queue_arn="arn:aws:sqs:us-east-1:941377123459:CloudComputingAssignment3Stack-LoggingQueue2008486F-AW1iGaSKytMA"
        )

        # Grant the Lambda function permissions to read from the SQS queue
        queue.grant_consume_messages(logging_lambda)

        # Add the SQS queue as an event source for the Lambda function
        sqs_event_source = lambda_sources.SqsEventSource(queue, batch_size=10)
        logging_lambda.add_event_source(sqs_event_source)

        # Outputs for easy reference
        CfnOutput(self, "LambdaFunctionName", value=logging_lambda.function_name)
        CfnOutput(self, "LogGroupName", value=log_group.log_group_name)
        CfnOutput(self, "LogStreamName", value="s3_operations") 
        CfnOutput(self, "CloudWatchAlarmName", value=alarm.alarm_name)
