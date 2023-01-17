import boto3
import json
import os
from datetime import datetime


def handler(event, context):
    client = boto3.client('rekognition')
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['table'])
    bucket = os.environ['bucket']
    
    response = client.search_faces_by_image(CollectionId='beautiful-faces',
                                            Image={'S3Object':{'Bucket':bucket, 'Name':'image.jpg'}},
                                            FaceMatchThreshold=70,
                                            MaxFaces=1
                                            )
    faceMatches = response['FaceMatches']
    for match in faceMatches:
        print(f"FaceId: {match['Face']['ExternalImageId']} similarity {match['Similarity']}%")
        table.put_item(
            Item={
                'type':'face',
                'id': match['Face']['FaceId'],
                'accuracy': f"{match['Similarity']}%",
                'name': match['Face']['ExternalImageId'],
                'timestamp': datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}
            )
        response = table.get_item(
            Key={
                'type': 'face',
                }
            )
        print(response['Item'])
