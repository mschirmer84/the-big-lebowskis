#!/usr/bin/env python3
import os

import aws_cdk as cdk

from beautiful_faces.beautiful_faces_stack import BeautifulFacesStack


app = cdk.App()
BeautifulFacesStack(app, "BeautifulFacesStack",
    env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),
)

app.synth()
