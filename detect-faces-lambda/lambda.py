import boto3
import urllib
import os
from datetime import datetime


def handler(event, context):
    rekognition = boto3.client('rekognition')
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['table'])
    
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = urllib.parse.unquote_plus(record['s3']['object']['key'], encoding='utf-8')
        
        accepted_extensions = ['png', 'jpg', 'jpeg']
        if os.path.splitext(key)[1].lower() not in accepted_extensions:
            raise TypeError(f"Rekognition cannot process [{key}]. Extension must one of [{accepted_extensions}].")

        response = rekognition.search_faces_by_image(CollectionId='beautiful_faces',
                                                Image={'S3Object':{'Bucket':bucket, 'Name':key}},
                                                FaceMatchThreshold=70,
                                                MaxFaces=1
                                                )
        face_matches = response['FaceMatches']
        for match in face_matches:
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
