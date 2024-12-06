from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_sqs as sqs,
    aws_s3 as s3,
    aws_cloudwatch as cloudwatch,
    aws_cloudwatch_actions as cw_actions,
    CfnOutput
)
from constructs import Construct

class CleanerLambdaStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Define the Cleaner Lambda function
        cleaner_lambda = _lambda.Function(
            self,
            "CleanerLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="cleaner_lambda.lambda_handler",
            code=_lambda.Code.from_asset("lambda/cleaner_lambda"),  # Adjust the path as needed
        )

        bucket = s3.Bucket.from_bucket_name(self, "MyBucket", "weihao-cdk-bucket")


        # Grant permissions to the Cleaner Lambda to access the S3 bucket
        bucket.grant_delete(cleaner_lambda)

        # Create an alarm action to trigger the Lambda function
        alarm = cloudwatch.Alarm.from_alarm_arn(
            self, "MyAlarm", 
            alarm_arn="arn:aws:cloudwatch:us-east-1:941377123459:alarm:LoggingLambdaStack-ObjectSizeThresholdAlarm7C7E90CA-YfnC3sITMRmP"
        )

        # Correct way to add a Lambda function as an alarm action
        alarm.add_alarm_action(
            cw_actions.LambdaAction(cleaner_lambda)  # Pass the Lambda function object, not its ARN
        )

        # Add permission for CloudWatch to invoke the Lambda
        cleaner_lambda.add_permission(
            "AllowCloudWatchInvoke",
            principal=iam.ServicePrincipal("cloudwatch.amazonaws.com"),
            source_arn=alarm.alarm_arn
        )

        # Output for easy reference
        CfnOutput(self, "CleanerLambdaFunctionName", value=cleaner_lambda.function_name)

