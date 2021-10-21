import http.client as httplib
import os
import requests
from log_cfg import logger
from pynamodb.exceptions import DoesNotExist
from blob.asset_model import AssetModel


def event(event, context):
    event_name = event['Records'][0]['eventName']
    key = event['Records'][0]['s3']['object']['key']
    blob_id = key.replace('{}/'.format(os.environ['S3_KEY_BASE']), '')

    if 'ObjectCreated:Put' == event_name:

        blob = AssetModel.get(hash_key=blob_id)
        try:
            result = blob.label_on_s3_upload(event)
            blob.labels = result['image_labels']
            blob.file_name = result['file_name']
            blob.message = "success"
            if blob.callback_url != '':
                try:
                    requests.post(f'{blob.callback_url}', json={"message": "success", "image_labels":
                                                                result['image_labels']})
                except ConnectionError as e:
                    logger.error(f"blob.callback_url: {e} ", exc_info=True)
                    blob.message = f"Wrong callback url {e}"
            blob.save()

        except Exception as e:
            blob.labels = []
            blob.file_name = ''
            blob.message = 'invalid image format, format may include: jpg,JPEG,png'
            blob.save()
            requests.post(f'{blob.callback_url}', json={"message": f"invalid image format, format may include:"
                                                                   f" jpg,JPEG,png {e}"})
            logger.error(f"blob.callback_url: {e} ", exc_info=True)



