import json
import os
from concurrent.futures import ThreadPoolExecutor
from pprint import pprint

import boto3
import spacy
from botocore.exceptions import ClientError

BUCKET_NAME = os.environ["BUCKET_NAME"]
AWS_REGION = os.environ["AWS_REGION"]


def get_comments(key, s3):
    data = s3.get_object(Bucket=BUCKET_NAME, Key=key)
    contents = data["Body"].read()
    return json.loads(contents)


def upload_comments(comments, key, s3):
    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=key,
        Body=json.dumps(comments),
        ContentType="application/json",
        ContentEncoding="utf8",
    )

    return key


def detect_sentiment(comment, comprehend):
    try:
        response = comprehend.detect_sentiment(
            Text=comment["textOriginal"],
            LanguageCode="fr",
        )
        comment["sentimentName"] = response["Sentiment"]
        comment["sentimentScorePositive"] = response["SentimentScore"]["Positive"]
        comment["sentimentScoreNegative"] = response["SentimentScore"]["Negative"]
        comment["sentimentScoreNeutral"] = response["SentimentScore"]["Neutral"]
        comment["sentimentScoreMixed"] = response["SentimentScore"]["Mixed"]
    except comprehend.exceptions.TextSizeLimitExceededException as err:
        print(f"Error {err} for comment:")
        pprint(comment)
    return comment


def add_sentiment(comments, comprehend):
    # with ThreadPoolExecutor(max_workers=20) as executor:
    #     futures = [
    #         executor.submit(detect_sentiment, comment, comprehend)
    #         for comment in comments
    #     ]

    #     comments = [future.result() for future in futures]
    comments = [detect_sentiment(comment, comprehend) for comment in comments]
    return comments


def add_lemmas(comments):
    nlp = spacy.load(
        "fr_core_news_md",
        exclude=["parser", "ner"],
    )

    def is_word(token):
        return not any(
            [
                token.is_stop,
                token.is_punct,
                token.is_space,
            ]
        )

    texts = [comment["textOriginal"].lower() for comment in comments]
    docs = nlp.pipe(texts)
    for comment, doc in zip(comments, docs):
        lemmas = [token.lemma_ for token in doc if is_word(token)]
        comment["textLemmatized"] = lemmas

    return comments


def lambda_handler(event, context):
    s3 = boto3.client("s3")
    comprehend = boto3.client("comprehend")

    key = event["bucket_key"]
    comments = get_comments(key, s3)
    comments = add_sentiment(comments, comprehend)
    comments = add_lemmas(comments)

    key = key.replace("landing", "processed")
    key = upload_comments(comments, key, s3)

    return {
        "output": {
            "bucket_name": BUCKET_NAME,
            "bucket_key": key,
            "s3_uri": f"s3://{BUCKET_NAME}/{key}",
            "object_url": f"https://{BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{key}",
            "console_url": f"https://s3.console.aws.amazon.com/s3/object/{BUCKET_NAME}?region={AWS_REGION}&bucketType=general&prefix={key}",
        },
    }
