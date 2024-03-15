import json
import os
from datetime import datetime

import boto3
import requests

API_URL = f"https://youtube.googleapis.com/youtube/v3/commentThreads"
BUCKET_NAME = os.environ["BUCKET_NAME"]
AWS_REGION = os.environ["AWS_REGION"]
API_KEY_SECRET_NAME = os.environ["YOUTUBE_API_KEY_SECRET_NAME"]


def get_video_id(event):
    try:
        video_id = event["video_id"]
        return video_id
    except KeyError:
        raise KeyError(f"The key 'video_id' is missing from the event.")


def get_api_key(secret_name):
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager")
    response = client.get_secret_value(SecretId=secret_name)
    return response["SecretString"]


def get_page(video_id, page_token=None):

    api_key = get_api_key(
        API_KEY_SECRET_NAME,
    )

    params = {
        "part": "snippet,replies",
        "key": api_key,
        "order": "time",
        "maxResults": 100,
        "videoId": video_id,
        "pageToken": page_token,
    }

    headers = {"Accept": "application/json"}

    response = requests.get(
        API_URL,
        params=params,
        headers=headers,
    )

    if response.status_code != 200:
        raise ValueError(response.json())

    return response.json()


def format_comment(comment):
    comment = {"id": comment["id"], **comment["snippet"]}

    if "authorChannelId" in comment:
        comment["authorChannelId"] = comment["authorChannelId"]["value"]
    else:
        comment["authorChannelId"] = None

    comment["parentId"] = comment.get("parentId", None)
    return comment


def upload_comments(comments, video_id, s3):
    time = datetime.now().strftime("%Y%m%d-%H%M%S.%f")
    key = f"landing/{video_id}-{time}.json"
    # key = "landing/Ps5kScYvQQk-20240309-154310.784770.json"

    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=key,
        Body=json.dumps(comments),
        ContentType="application/json",
        ContentEncoding="utf8",
    )

    return key


def lambda_handler(event, context):
    video_id = get_video_id(event)

    s3 = boto3.client("s3")

    retrieved_comments = 0
    next_page_token = None

    comments = []

    while next_page_token is not False:
        data = get_page(
            video_id=video_id,
            page_token=next_page_token,
        )

        for item in data["items"]:
            comment = item["snippet"]["topLevelComment"]
            comment = format_comment(comment)
            comments.append(comment)

            if "replies" in item:
                for comment in item["replies"]["comments"]:
                    comment = format_comment(comment)
                    comments.append(comment)

        next_page_token = data.get("nextPageToken", False)

    retrieved_comments = len(comments)
    key = upload_comments(comments, video_id, s3)

    return {
        "video_id": video_id,
        "output": {
            "bucket_name": BUCKET_NAME,
            "bucket_key": key,
            "s3_uri": f"s3://{BUCKET_NAME}/{key}",
            "object_url": f"https://{BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{key}",
            "console_url": f"https://s3.console.aws.amazon.com/s3/object/{BUCKET_NAME}?region={AWS_REGION}&bucketType=general&prefix={key}",
        },
        "retrieved_comments": retrieved_comments,
    }
