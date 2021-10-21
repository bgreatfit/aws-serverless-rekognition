import http.client as httplib
import os
import requests
from pynamodb.exceptions import DoesNotExist
from blob.asset_model import AssetModel


def event(event, context):
    event_name = event['Records'][0]['eventName']
    key = event['Records'][0]['s3']['object']['key']
    blob_id = key.replace('{}/'.format(os.environ['S3_KEY_BASE']), '')

    try:
        if 'ObjectCreated:Put' == event_name:

            blob = AssetModel.get(hash_key=blob_id)
            result = blob.label_on_s3_upload(event)
            if result:
                blob.labels = result['image_labels']
                blob.file_name = result['file_name']
                blob.save()
                if blob.callback_url != '':
                    requests.post('http://httpbin.org/post', json={"key": "value"})
            else:
                requests.post('http://httpbin.org/post', json={"key": "value"})

    except DoesNotExist:
        return {
            'statusCode': httplib.NOT_FOUND,
            'body': {
                'error_message': 'ASSET {} not found'.format(blob_id)
            }
        }

