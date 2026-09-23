import os

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from dotenv import load_dotenv

load_dotenv()


def get_s3_client():
    return boto3.client(
        "s3",
        region_name=os.getenv("AWS_REGION")
    )


def list_bucket_objects():
    bucket_name = os.getenv("AWS_S3_BUCKET")

    if not bucket_name:
        return {
            "status": "not_configured",
            "message": "AWS_S3_BUCKET is not configured.",
            "objects": []
        }

    try:
        s3 = get_s3_client()

        response = s3.list_objects_v2(
            Bucket=bucket_name
        )

        objects = []

        for item in response.get("Contents", []):
            objects.append({
                "key": item["Key"],
                "size": item["Size"],
                "last_modified": item["LastModified"].isoformat()
            })

        return {
            "status": "success",
            "bucket": bucket_name,
            "objects": objects
        }

    except (BotoCoreError, ClientError) as error:
        return {
            "status": "error",
            "message": str(error),
            "objects": []
        }