#!/usr/bin/env bash

set -u

for bucket_name in $DSS_S3_BUCKET $DSS_S3_CHECKOUT_BUCKET $DSS_S3_BUCKET_TEST $DSS_S3_CHECKOUT_BUCKET_TEST ; do
    echo Clearing AWS bucket ${bucket_name}
    aws s3 rm --recursive s3://${bucket_name}
done

for bucket_name in $DSS_GS_BUCKET $DSS_GS_CHECKOUT_BUCKET $DSS_GS_BUCKET_TEST $DSS_GS_CHECKOUT_BUCKET_TEST; do
    echo Clearing GS bucket ${bucket_name}
    gsutil -m rm gs://${bucket_name}/**
done

