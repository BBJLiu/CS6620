#!/usr/bin/env python3
import aws_cdk as cdk
from assignment3.part1 import ResourcesStack
from assignemnt3.part2 import DriverLambdaStack
from assignment3.part3 import PlottingLambdaStack
from assignment3.part4 import SizeTrackingLambdaStack

app = cdk.App()

# Define each Lambda in its own stack
DriverLambdaStack(app, "DriverLambdaStack")
PlottingLambdaStack(app, "PlottingLambdaStack")
SizeTrackingLambdaStack(app, "SizeTrackingLambdaStack")

# ResourcesStack(app, "ResourcesStack")

app.synth()