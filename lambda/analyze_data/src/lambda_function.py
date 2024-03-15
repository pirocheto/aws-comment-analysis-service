import ast
import itertools
import json
import os
from collections import Counter
from datetime import datetime

import boto3
import pandas as pd

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
    df = pd.read_csv(data["Body"])
    return transform_data(df)


def transform_data(df):
    def parse_lemmas(lemmas):
        return ast.literal_eval(lemmas)

    df["textLemmatized"] = df["textLemmatized"].apply(parse_lemmas)

    df["publishedAt"] = pd.to_datetime(df["publishedAt"])
    df["publishedAtMonth"] = df["publishedAt"].dt.month
    df["publishedAtYear"] = df["publishedAt"].dt.year
    df["publishedAtDay"] = df["publishedAt"].dt.day

    df["publishedAtYearMonth"] = df["publishedAt"].dt.strftime("%Y-%m")
    df["publishedAtYearMonthDay"] = df["publishedAt"].dt.strftime("%Y-%m-%d")
    return df


def get_stats_by_time(df, freq):
    if freq == "d":
        col = "publishedAtYearMonthDay"
    elif freq == "M":
        col = "publishedAtYearMonth"

    index = pd.period_range(
        start=df[col].min(),
        end=df[col].max(),
        freq=freq,
    )

    df_groups = (
        df.groupby([col, "sentimentName"])
        .size()
        .unstack(fill_value=0)
        .reindex(index.astype(str), fill_value=0)
    )

    df_groups["TOTAL"] = df_groups.sum(axis=1)
    return df_groups.to_dict(orient="index")


def upload_stats(stats, key, s3):
    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=key,
        Body=json.dumps(stats),
        ContentType="application/json",
        ContentEncoding="utf8",
    )

    return key


def word_frequency(words):
    words = list(itertools.chain.from_iterable(words))
    return Counter(words)


def get_frequencies(df):
    stats = {}
    for sent in ["POSITIVE", "NEGATIVE", "MIXED", "NEUTRAL"]:
        words = df[df["sentimentName"] == sent]["textLemmatized"]
        stats[sent] = word_frequency(words)

    words = df["textLemmatized"]
    stats["OVERALL"] = word_frequency(words)
    return stats


def lambda_handler(event, context):
    s3 = boto3.client("s3")
    key = get_key(event)
    df = get_data(key, s3)

    dates = df["publishedAt"].sort_values()
    date_first_comment = dates.iloc[0]
    date_last_comment = dates.iloc[-1]
    time_activity = date_last_comment - date_first_comment

    stats = {
        "video_id": df.iloc[0]["videoId"],
        "sentiment": df["sentimentName"].value_counts().to_dict(),
        "date": {
            "first_comment": str(date_first_comment),
            "last_comment": str(date_last_comment),
            "time_activity": str(time_activity),
        },
        "nb_total": df.shape[0],
        "by_time": {
            "month": get_stats_by_time(df, freq="M"),
            "day": get_stats_by_time(df, freq="d"),
        },
        "word_frequencies": get_frequencies(df),
    }

    key = key.replace("formatted", "analyzed").replace("csv", "json")
    key = upload_stats(stats, key=key, s3=s3)

    return {
        "output": {
            "bucket_name": BUCKET_NAME,
            "bucket_key": key,
            "s3_uri": f"s3://{BUCKET_NAME}/{key}",
            "object_url": f"https://{BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{key}",
            "console_url": f"https://s3.console.aws.amazon.com/s3/object/{BUCKET_NAME}?region={AWS_REGION}&bucketType=general&prefix={key}",
        },
    }
