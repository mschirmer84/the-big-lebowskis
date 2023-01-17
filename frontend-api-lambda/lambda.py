import boto3
import json
import os


default_headers = {
    'Access-Control-Allow-Headers': '*',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
}

def handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['table'])
    result = table.get_item(
        Key={
            'faceid': 'face',
        }
    )

    if result is not None and len(result) > 0:
        return {
            'statusCode': 200,
            'headers': default_headers,
            'body': json.dumps(result)
        }

    return {
        'statusCode': 500,
        'headers': default_headers,
        'body': json.dumps('Request Failed!')
    }