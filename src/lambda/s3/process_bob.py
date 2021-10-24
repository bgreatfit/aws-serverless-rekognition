import os
from log_cfg import logger
from src.dataLayer.asset_model import AssetModel


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
            blob.save()

        except Exception as e:
            blob.labels = []
            blob.file_name = ''
            blob.message = 'invalid image format, format may include: jpg,png'
            blob.state = "RETRY"
            blob.save()
            logger.error(f"Image: {e} ", exc_info=True)



