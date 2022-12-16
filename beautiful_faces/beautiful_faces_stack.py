from aws_cdk import (
    Stack,
    CfnParameter as _cfnParameter,
    aws_cognito as _cognito,
    aws_s3 as _s3,
    aws_dynamodb as _dynamodb,
    aws_lambda as _lambda,
    aws_apigateway as _apigateway,
    aws_s3_notifications as _s3n,
)
from constructs import Construct
import os


class BeautifulFacesStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        user_pool = _cognito.UserPool(self, "UserPool")
        user_pool.add_client("app-client",
            auth_flows=_cognito.AuthFlow(user_password=True),
            supported_identity_providers=[_cognito.UserPoolClientIdentityProvider.COGNITO]
        )
        
        #auth = _apigateway.CognitoUserPoolsAuthorizer(self, "faceDetector", cognito_user_pools=[user_pool])

        faces_table = _dynamodb.Table(self, id='dynamoTable', table_name='beautiful_faces_metadata', partition_key=_dynamodb.Attribute(
            name='faceid', type=_dynamodb.AttributeType.STRING))
        
        faces_bucket = _s3.Bucket(self, id='s3bucket', bucket_name=f"beautifulfaces-upload-{self.account}")
        
        faces_lambda = _lambda.Function(self, id='lambdafunction', function_name="detect-faces", runtime=_lambda.Runtime.PYTHON_3_9,
                                     handler='index.handler',
                                     code=_lambda.Code.from_asset(os.path.join("./", "detect-faces-lambda")),
                                     environment={
                                        'table': faces_table.table_name,
                                        'bucket': faces_bucket.bucket_name,
                                        },
                                     )
        faces_bucket.add_event_notification(_s3.EventType.OBJECT_CREATED, _s3n.LambdaDestination(faces_lambda))
        faces_table.grant_read_write_data(faces_lambda)
        faces_bucket.grant_read(faces_lambda)

