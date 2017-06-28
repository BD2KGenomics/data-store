from __future__ import absolute_import, division, print_function, unicode_literals

import typing

from . import HCABlobStore
from ..blobstore import BlobStore


class GSHCABlobStore(HCABlobStore):
    def __init__(self, handle: BlobStore) -> None:
        self.handle = handle

    def verify_blob_checksum(self, bucket: str, object_name: str, metadata: typing.Dict[str, str]) -> bool:
        """
        Given a blob, verify that the checksum on the cloud store matches the checksum in the metadata dictionary.  The
        keys to the metadata dictionary will be the items in ``MANDATORY_METADATA``.  Each cloud-specific implementation
        of ``HCABlobStore`` should extract the correct field and check it against the cloud-provided checksum.
        :param bucket:
        :param object_name:
        :param metadata:
        :return: True iff the checksum is correct.
        """
        checksum = self.handle.get_cloud_checksum(bucket, object_name)
        metadata_checksum_key = typing.cast(str, HCABlobStore.MANDATORY_METADATA['CRC32C']['keyname'])
        return checksum.lower() == metadata[metadata_checksum_key].lower()