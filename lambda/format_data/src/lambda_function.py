import csv
import io
import json
import os
from pprint import pprint

import boto3

BUCKET_NAME = os.environ["BUCKET_NAME"]
AWS_REGION = os.environ["AWS_REGION"]


def get_key(event):
    try:
        key = event["bucket_key"]
        return key
    except KeyError:
        raise KeyError(f"The key 'bucket_key' is missing from the event.")


def load_json(key, s3):
    data = s3.get_object(Bucket=BUCKET_NAME, Key=key)
    contents = data["Body"].read()

    return json.loads(contents)


def convert_json_to_csv(data):

    csv_buffer = io.StringIO()

    writer = csv.DictWriter(csv_buffer, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)
    csv_data = csv_buffer.getvalue()

    return csv_data


def upload_csv(data, key, s3):
    csv_data = convert_json_to_csv(data)

    key = key.replace("processed", "formatted").replace("json", "csv")
    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=key,
        Body=csv_data,
        ContentType="text/csv",
        ContentEncoding="utf8",
    )
    return key


def lambda_handler(event, context):
    key = get_key(event)

    s3 = boto3.client("s3")

    data = load_json(key, s3)
    key = upload_csv(data, key, s3)

    return {
        "output": {
            "bucket_name": BUCKET_NAME,
            "bucket_key": key,
            "s3_uri": f"s3://{BUCKET_NAME}/{key}",
            "object_url": f"https://{BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{key}",
            "console_url": f"https://s3.console.aws.amazon.com/s3/object/{BUCKET_NAME}?region={AWS_REGION}&bucketType=general&prefix={key}",
        },
    }


if __name__ == "__main__":
    from pprint import pprint

    results = lambda_handler(
        {"key": "processed/Ps5kScYvQQk-20240309-154310.784770.json"},
        None,
    )
    pprint(results)
