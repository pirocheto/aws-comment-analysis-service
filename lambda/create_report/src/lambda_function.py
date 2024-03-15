import json
import os
from pathlib import Path

import boto3
import matplotlib.pyplot as plt
from pdf import create_pdf

plt.rcParams["font.family"] = "Helvetica"

BUCKET_NAME = os.environ["BUCKET_NAME"]
AWS_REGION = os.environ["AWS_REGION"]


def get_key(event):
    try:
        key = event["bucket_key"]
        return key
    except KeyError:
        raise KeyError(f"The key 'bucket_key' is missing from the event.")


def get_data(key, s3):
    data = s3.get_object(Bucket=BUCKET_NAME, Key=key)
    contents = data["Body"].read()
    return json.loads(contents)


def lambda_handler(event, context):
    key = get_key(event)
    s3 = boto3.client("s3")
    data = get_data(key, s3)

    pdf = create_pdf(
        video_id=data["video_id"],
        nb_comments=data["nb_total"],
        date_first_comment=data["date"]["first_comment"],
        date_last_comment=data["date"]["last_comment"],
        sentiments=data["sentiment"],
        data_by_day=data["by_time"]["day"],
        word_frequencies=data["word_frequencies"],
    )

    key = key.replace("analyzed", "reports").replace("json", "pdf")
    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=key,
        Body=pdf.output(dest="S"),
        ContentType="application/pdf",
        ContentEncoding="utf8",
    )

    return {
        "output": {
            "bucket_name": BUCKET_NAME,
            "bucket_key": key,
            "s3_uri": f"s3://{BUCKET_NAME}/{key}",
            "object_url": f"https://{BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{key}",
            "console_url": f"https://s3.console.aws.amazon.com/s3/object/{BUCKET_NAME}?region={AWS_REGION}&bucketType=general&prefix={key}",
        },
    }
