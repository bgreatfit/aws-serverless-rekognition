from datetime import datetime
from enum import Enum
import boto3
import os
from pynamodb.attributes import UnicodeAttribute, UTCDateTimeAttribute, ListAttribute
from pynamodb.models import Model
from log_cfg import logger
from botocore.client import Config
BUCKET = os.environ['S3_BUCKET']
KEY_BASE = os.environ['S3_KEY_BASE']


class State(Enum):
    """
    Manage asset states in dynamo with a string field
    """
    CREATED = 1


class AssetModel(Model):
    class Meta:
        table_name = os.environ['DYNAMODB_TABLE']
        if 'ENV' in os.environ:
            host = 'http://localhost:8000'
        else:
            region = os.environ['REGION']
            host = os.environ['DYNAMODB_HOST']

    blob_id = UnicodeAttribute(hash_key=True)
    state = UnicodeAttribute(null=False, default=State.CREATED.name)
    message = UnicodeAttribute(null=True)
    callback_url = UnicodeAttribute(null=True)
    labels = ListAttribute(null=True)
    file_name = UnicodeAttribute(null=True)
    createdAt = UTCDateTimeAttribute(null=False, default=datetime.now().astimezone())
    updatedAt = UTCDateTimeAttribute(null=False, default=datetime.now().astimezone())

    def __str__(self):
        return 'blob_id:{}, state:{}'.format(self.blob_id, self.state)

    def get_key(self):
        return u'{}/{}'.format(KEY_BASE, self.blob_id)

    def save(self, conditional_operator=None, **expected_values):
        try:
            self.updatedAt = datetime.now().astimezone()
            logger.debug('saving: {}'.format(self))
            super(AssetModel, self).save()
        except Exception as e:
            logger.error('save {} failed: {}'.format(self.asset_id, e), exc_info=True)
            raise e

    def __iter__(self):
        for name, attr in self._get_attributes().items():
            yield name, attr.serialize(getattr(self, name))

    def get_upload_url(self, ttl=60):
        """
        :param ttl: url duration in seconds
        :return: a temporary presigned PUT url
        """
        s3 = boto3.client('s3', config=Config(signature_version='s3v4'), region_name='us-west-2')

        put_url = s3.generate_presigned_url(
            ClientMethod='put_object',
            Params={
                'Bucket': BUCKET,
                'Key': self.get_key(),
            },
            ExpiresIn=ttl,
        )

        logger.debug('upload URL: {}'.format(put_url))
        return put_url

    def label_on_s3_upload(self, event_obj):
        """
                :param event_obj: aws Event Object
                :return: image labels
        """
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

        return {"image_labels": image_labels, "file_name": file_name}

