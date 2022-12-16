import boto3
import json
import os


def handler(event, context):
    bucket = os.environ['bucket']
    client = boto3.client('rekognition')

    response = client.search_faces_by_image(CollectionId='beautiful-faces',
                                            Image={'S3Object':{'Bucket':bucket, 'Name':'image.jpg'}},
                                            FaceMatchThreshold=70,
                                            MaxFaces=1
                                            )
    faceMatches = response['FaceMatches']
    for match in faceMatches:
        print(f"FaceId: {match['Face']['ExternalImageId']} similarity {match['Similarity']}%")

