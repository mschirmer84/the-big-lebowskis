from aws_cdk import (
    Stack,
    CfnParameter as _cfnParameter,
    aws_cognito as _cognito,
    aws_s3 as _s3,
    aws_dynamodb as _dynamodb,
    aws_lambda as _lambda,
    aws_apigateway as _apigateway,
    aws_s3_notifications as _s3n,
    aws_s3_deployment as _s3d,
    aws_iam as _iam
)
from constructs import Construct
import os


class BeautifulFacesStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        faces_table = _dynamodb.Table(self, id='dynamoTable', table_name='beautiful_faces_metadata', partition_key=_dynamodb.Attribute(
            name='faceid', type=_dynamodb.AttributeType.STRING))
        
        faces_bucket = _s3.Bucket(self, id='s3bucket', bucket_name=f"beautifulfaces-upload-{self.account}")
        
        faces_lambda = _lambda.Function(self, id='lambdafunction', function_name="detect-faces", runtime=_lambda.Runtime.PYTHON_3_9,
                                    handler='lambda.handler',
                                    code=_lambda.Code.from_asset(os.path.join("./", "detect-faces-lambda")),
                                    environment={
                                        'table': faces_table.table_name,
                                        'bucket': faces_bucket.bucket_name,
                                        },
                                    )
        faces_bucket.add_event_notification(_s3.EventType.OBJECT_CREATED, _s3n.LambdaDestination(faces_lambda))
        faces_table.grant_read_write_data(faces_lambda)
        faces_bucket.grant_read(faces_lambda)
        faces_lambda.add_to_role_policy(_iam.PolicyStatement(
            actions=["rekognition:SearchFacesByImage"],
            resources=[f"arn:aws:rekognition::{self.account}:collection/beautiful-faces"],
            effect=_iam.Effect.ALLOW
        ))

        frontend_api_lambda = _lambda.Function(self, id='frontend_api', function_name="frontend-api", runtime=_lambda.Runtime.PYTHON_3_9,
                                    handler='lambda.handler',
                                    code=_lambda.Code.from_asset(os.path.join("./", "frontend-api-lambda")),
                                    environment={
                                        'table': faces_table.table_name,
                                        'bucket': faces_bucket.bucket_name,
                                        },
                                    )
        faces_table.grant_read_data(frontend_api_lambda)
        
        frontend_api = _apigateway.LambdaRestApi(self, id='frontend_api_lambda', rest_api_name='frontend', handler=frontend_api_lambda, proxy=True)

        spa_bucket = _s3.Bucket(self, id='spabucket', bucket_name=f"beautifulfaces-frontend-{self.account}",
                public_read_access=True, website_index_document='index.html')
        
        static_website = _s3d.BucketDeployment(self, id='static_website', destination_bucket=spa_bucket, sources=[_s3d.Source.asset('spa/dist')])
