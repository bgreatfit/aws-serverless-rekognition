import uuid
import json
import logging
from src.dataLayer.asset_model import AssetModel
from log_cfg import logger


def create(event, context):
    logger.debug('event: {}'.format(event))
    try:

        data = json.loads(event['body']) if event['body'] else None
        if data is not None and 'callback_url' not in data:
            logging.error('Validation Failed')
            return {'statusCode': 400,
                    'body': json.dumps({'error_message': 'please specify a callback parameter with value'})}

        callback_url = data['callback_url'] if data is not None else ''

        logger.debug('event: {}'.format(event))
        asset = AssetModel()
        asset.blob_id = uuid.uuid1().__str__()
        asset.callback_url = callback_url
        asset.save()
        upload_url = asset.get_upload_url(60000)  # No timeout specified here, use member param default

        return {
            "statusCode": 201,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "upload_url": upload_url,
                "id": asset.blob_id
            })
        }
    except Exception as e:
        return {
            "statusCode": 400,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({"error_message": "Invalid parameter"})
        }

