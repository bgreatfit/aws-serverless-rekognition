import requests

from src.dataLayer.asset_model import AssetModel
from log_cfg import logger


def event(event, context):

    logger.debug(f"Event:{event}")
    for r in event.get('Records'):
        if r.get('eventName') == "MODIFY" and r['dynamodb']['NewImage']['state']['S'] != 'DONE':
            callback_url = r['dynamodb']['NewImage']['callback_url']['S']
            image_labels = r['dynamodb']['NewImage']['labels']['L']
            blob_id = r['dynamodb']['NewImage']['blob_id']['S']
            message = r['dynamodb']['NewImage']['message']['S']
            blob = AssetModel.get(hash_key=blob_id)
            if callback_url != '':
                try:
                    blob.state = 'DONE'
                    blob.save()
                    requests.post(f'{callback_url}', json={"message": message, "image_labels": image_labels})
                except ConnectionError as e:
                    logger.error(f"callback_url: {e} ", exc_info=True)
                    requests.post(f'{callback_url}', json={"message": f"Callback url {e}",
                                                           "image_labels": image_labels})



