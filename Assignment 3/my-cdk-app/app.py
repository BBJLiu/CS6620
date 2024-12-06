#!/usr/bin/env python3
import aws_cdk as cdk
from cloud_computing_assignment3.cloud_computing_assignment3_stack import CloudComputingAssignment3Stack
from cloud_computing_assignment3.driver_lambda_stack import DriverLambdaStack
from cloud_computing_assignment3.plotting_lambda_stack import PlottingLambdaStack
from cloud_computing_assignment3.size_tracking_lambda_stack import SizeTrackingLambdaStack

app = cdk.App()

# Define each Lambda in its own stack
# DriverLambdaStack(app, "DriverLambdaStack")
# PlottingLambdaStack(app, "PlottingLambdaStack")
# SizeTrackingLambdaStack(app, "SizeTrackingLambdaStack")

# ResourcesStack(app, "CloudComputingAssignment3Stack")

####Testing

# Deploy the main infrastructure stack
infrastructure_stack = CloudComputingAssignment3Stack(app, "CloudComputingAssignment3Stack")

# Deploy the size tracking Lambda stack
lambda_stack = SizeTrackingLambdaStack(app, "SizeTrackingLambdaStack")

app.synth()
