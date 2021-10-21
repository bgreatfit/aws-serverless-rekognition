import json
import http.client as httplib
from pynamodb.exceptions import DoesNotExist
from blob.asset_model import AssetModel
from log_cfg import logger


def get(event, context):

    logger.debug('event: {}'.format(event))
    try:
        blob_id = event['pathParameters']['blob_id']
        blob = AssetModel.get(hash_key=blob_id)
    except DoesNotExist:

        return {
            'statusCode': httplib.NOT_FOUND,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "message": f"BLOB {blob_id} not found",
            })
        }
    return {
        "statusCode": httplib.ACCEPTED,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({
            "callback_url": blob.callback_url,
            "labels": blob.labels,
            "created_at": blob.createdAt,
            "message": blob.message
        }, indent=4, sort_keys=True, default=str)
    }