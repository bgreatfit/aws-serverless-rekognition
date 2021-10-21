import http.client as httplib
import os
import boto3

from pynamodb.exceptions import DoesNotExist, DeleteError, UpdateError
from blob.asset_model import AssetModel


def event(event, context):
    event_name = event['Records'][0]['eventName']
    key = event['Records'][0]['s3']['object']['key']
    blob_id = key.replace('{}/'.format(os.environ['S3_KEY_BASE']), '')

    try:
        if 'ObjectCreated:Put' == event_name:

            try:
                blob = AssetModel.get(hash_key=blob_id)
                label_on_s3_upload(event, blob)
                return {
                    'statusCode': httplib.BAD_REQUEST,
                    'body': {
                        'error_message': 'Unable to update ASSET'}
                }
            except UpdateError:
                return {
                    'statusCode': httplib.BAD_REQUEST,
                    'body': {
                        'error_message': 'Unable to update ASSET'}
                }

        elif 'ObjectRemoved:Delete' == event_name:

            try:
                blob = AssetModel.get(hash_key=blob_id)
                blob.delete()
            except DeleteError:
                return {
                    'statusCode': httplib.BAD_REQUEST,
                    'body': {
                        'error_message': 'Unable to delete ASSET {}'.format(blob)
                    }
                }

    except DoesNotExist:
        return {
            'statusCode': httplib.NOT_FOUND,
            'body': {
                'error_message': 'ASSET {} not found'.format(blob_id)
            }
        }

    return {'statusCode': httplib.ACCEPTED}


def label_on_s3_upload(event_obj, blob):
    bucket = os.environ['S3_BUCKET']
    region_name = os.environ['REGION']

    files_uploaded = event_obj['Records']
    image_labels = []
    file_name = ''
    for file in files_uploaded:
        file_name = file["s3"]["object"]["key"]
        rekognition_client = boto3.client('rekognition', region_name=region_name)
        response = rekognition_client.detect_labels(Image={'S3Object': {'Bucket': bucket, 'Name': file_name}},
                                                    MaxLabels=5)
        for label in response['Labels']:
            image_labels.append(label["Name"].lower())

    # Add to DynamoDB

    blob.labels = image_labels
    blob.file_name = file_name
    blob.save()
