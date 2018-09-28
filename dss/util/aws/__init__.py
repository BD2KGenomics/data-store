import json

import boto3
import botocore
from . import clients, resources, cloudwatch_logging


AWS_MIN_CHUNK_SIZE = 64 * 1024 * 1024
"""Files must be larger than this before we consider multipart uploads."""
AWS_MAX_MULTIPART_COUNT = 10000
"""Maximum number of parts allowed in a multipart upload.  This is a limitation imposed by S3."""


class ARN:
    fields = "arn partition service region account_id resource".split()
    _default_region, _default_account_id, _default_iam_username = None, None, None

    def __init__(self, arn="arn:aws::::", **kwargs):
        self.__dict__.update(dict(zip(self.fields, arn.split(":", 5)), **kwargs))
        if "region" not in kwargs and not self.region:
            self.region = self.get_region()
        if "account_id" not in kwargs and not self.account_id:
            self.account_id = self.get_account_id()

    @classmethod
    def get_region(cls):
        if cls._default_region is None:
            cls._default_region = botocore.session.Session().get_config_variable("region")
        return cls._default_region

    @classmethod
    def get_account_id(cls):
        if cls._default_account_id is None:
            cls._default_account_id = clients.sts.get_caller_identity()["Account"]
        return cls._default_account_id

    def __str__(self):
        return ":".join(getattr(self, field) for field in self.fields)


def send_sns_msg(topic_arn, message, attributes=None):
    sns_topic = resources.sns.Topic(str(topic_arn))
    args = {'Message': json.dumps(message)}
    if attributes is not None:
        args['MessageAttributes'] = attributes
    sns_topic.publish(**args)


def get_s3_chunk_size(filesize: int) -> int:
    if filesize <= AWS_MAX_MULTIPART_COUNT * AWS_MIN_CHUNK_SIZE:
        return AWS_MIN_CHUNK_SIZE
    else:
        div = filesize // AWS_MAX_MULTIPART_COUNT
        if div * AWS_MAX_MULTIPART_COUNT < filesize:
            div += 1
        return ((div + 1048575) // 1048576) * 1048576


def is_s3_encrypted(bucket: str, key: str) -> bool:
    return not boto3.resource("s3").Object(bucket, key).server_side_encryption is None


def waive_s3_checksum_equality(bucket: str, key: str) -> bool:
    # AWS S3 ETag checksums are not valid indicators of file equality
    # if server side encryption is enabled.
    # TODO Before waiving checksum equality, it would be valuable
    # to have some other indicator of file equality, such as file size.
    # However, as the code is currently structured, that information
    # is not available.
    return is_s3_encrypted(bucket, key)
