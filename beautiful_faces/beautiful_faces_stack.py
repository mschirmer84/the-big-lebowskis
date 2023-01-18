from aws_cdk import (
    Stack,
    aws_s3 as _s3,
    aws_dynamodb as _dynamodb,
    aws_lambda as _lambda,
    aws_apigateway as _apigateway,
    aws_s3_notifications as _s3n,
    aws_s3_deployment as _s3d,
    aws_iam as _iam,
    aws_rekognition as _rekognition,
    DockerImage,
    BundlingOptions,
    AssetStaging,
    CfnOutput,
    RemovalPolicy,
)
from constructs import Construct
import os


class BeautifulFacesStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        recognition_collection = _rekognition.CfnCollection(self, id='beautiful-faces-collection', collection_id='beautiful_faces')

        faces_table = _dynamodb.Table(self, id='dynamoTable', table_name='beautiful_faces_metadata', partition_key=_dynamodb.Attribute(
            name='type', type=_dynamodb.AttributeType.STRING), removal_policy=RemovalPolicy.DESTROY)
        
        faces_bucket = _s3.Bucket(self, id='s3bucket', bucket_name=f"beautifulfaces-upload-{self.account}", removal_policy=RemovalPolicy.DESTROY, auto_delete_objects=True)
        
        faces_lambda = _lambda.Function(self, id='lambdafunction', function_name="detect-faces", runtime=_lambda.Runtime.PYTHON_3_9,
                                    handler='lambda.handler',
                                    code=_lambda.Code.from_asset(os.path.join("./", "detect-faces-lambda")),
                                    environment={
                                        'table': faces_table.table_name
                                        },
                                    )
        faces_bucket.add_event_notification(_s3.EventType.OBJECT_CREATED, _s3n.LambdaDestination(faces_lambda))
        faces_table.grant_read_write_data(faces_lambda)
        faces_bucket.grant_read(faces_lambda)
        faces_lambda.add_to_role_policy(_iam.PolicyStatement(
            actions=["rekognition:SearchFacesByImage"],
            resources=[recognition_collection.attr_arn],
            effect=_iam.Effect.ALLOW
        ))

        frontend_api_lambda = _lambda.Function(self, id='frontend_api', function_name="frontend-api", runtime=_lambda.Runtime.PYTHON_3_9,
                                    handler='lambda.handler',
                                    code=_lambda.Code.from_asset(os.path.join("./", "frontend-api-lambda")),
                                    environment={
                                        'table': faces_table.table_name
                                        },
                                    )
        faces_table.grant_read_data(frontend_api_lambda)

        spa_bucket = _s3.Bucket(self, id='spabucket', bucket_name=f"beautifulfaces-frontend-{self.account}",
                public_read_access=True, website_index_document='index.html', removal_policy=RemovalPolicy.DESTROY, auto_delete_objects=True)
        
        frontend_api = _apigateway.LambdaRestApi(self, id='frontend_api_lambda', rest_api_name='frontend',
                handler=frontend_api_lambda,
                proxy=True,
                default_cors_preflight_options=_apigateway.CorsOptions(
                    allow_origins=['*'],
                    allow_methods=['*'],
                    allow_headers=['*'],
                    allow_credentials=True,
                )
        )

        spa_asset = AssetStaging(self, id='spa_asset',
                source_path=os.path.join(os.getcwd(), "spa"),
                bundling=BundlingOptions(
                    image=DockerImage.from_registry('node:16-slim'),
                    entrypoint=['bash', '-c'],
                    command=['npm install && npm run build && cp -r dist/* /asset-output'],
                    environment={
                        'VITE_API_ENDPOINT': frontend_api.url_for_path('/')
                    },
                    user='root',
                ))
        
        static_website = _s3d.BucketDeployment(self, id='static_website',
                destination_bucket=spa_bucket,
                sources=[
                    _s3d.Source.asset(spa_asset.absolute_staged_path),
                    _s3d.Source.json_data('config.json', {'api_endpoint': frontend_api.url_for_path('/')})
                ],
                retain_on_delete=False,
                )
        
        CfnOutput(self, 'spa_website_url',
            value=spa_bucket.bucket_website_url,
            description='Single Page Application Website URL',
            export_name='spa-website-url'
        )
