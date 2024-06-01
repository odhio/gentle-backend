import pandas as pd
import datetime
from domains.models import Message
import seaborn as sns
import random
from lib.janome import ranking_words

# TODO:
# 2. Create a time series plot for each data

# 1-> rms > mean > despersion > trend > seasonality


# 文脈考慮する場合の変更案 paper:https://www.jstage.jst.go.jp/article/tjsai/23/6/23_6_384/_article/-char/ja
def set_resample_term(start: pd.Timestamp, end: pd.Timestamp) -> str:
    duration = (end - start).total_seconds() / 60
    if duration < 10:
        return None
    resample_rate = f"{int(duration/10)}T"

    return resample_rate


# ごちゃついてるので後で整理したい
def create_dateframe(messages: list[Message]) -> pd.DataFrame:
    df = pd.DataFrame(
        [
            {
                "user_uuid": message.user_uuid,
                "message": message.message,
                "created_at": message.created_at,
                "emotion": message.emotion,
                "pewssure": message.pressure,
                "name": message.user.name,
            }
            for message in messages
        ]
    )
    df["created_at"] = df["created_at"].dt.tz_convert("Asia/Tokyo")
    df.set_index("created_at", inplace=True)
    return df


def user_time_series(messages: list[Message]) -> pd.DataFrame:
    df = create_dateframe(messages)
    df.sort_values(by="created_at")
    print(df)

    resample_rate = set_resample_term(df["created_at"].iloc[0], df["created_at"].iloc[-1])
    resampled_df = df.groupby("name").resample(resample_rate).size().unstack(fill_value=0)
    time_series_pivot = resampled_df.T

    return time_series_pivot


def emotion_time_series(messages: list[Message]) -> pd.DataFrame:
    df = create_dateframe(messages)
    df.sort_values(by="created_at")
    print(df)

    resample_rate = set_resample_term(df["created_at"].iloc[0], df["created_at"].iloc[-1])
    df["emotion"] = df["emotion"].apply(lambda x: x.value)
    resampled_df = df.groupby("emotion").resample(resample_rate).size().unstack(fill_value=0)

    time_series_pivot = resampled_df.T

    return time_series_pivot


def topic_time_series(messages: list[Message]) -> pd.DataFrame:
    df = create_dateframe(messages)
    df.sort_values(by="created_at")

    resample_rate = set_resample_term(df["created_at"].iloc[0], df["created_at"].iloc[-1])

    resampled_df = df.resample(resample_rate).agg({"message": lambda x: list(x)})
    for row in resampled_df.iterrows():
        if len(row["message"]) > 0:
            resampled_df["message"] = ranking_words(row["message"])

    time_series_pivot = resampled_df.T

    return time_series_pivot


def emotion_summary(messages: list[Message]) -> pd.DataFrame:
    df = pd.DataFrame(
        [
            {
                "message_uuid": message.uuid,
                "room_uuid": message.room_uuid,
                "user_uuid": message.user_uuid,
                "message": message.message,
                "emotion": message.emotion,
                "created_at": message.created_at,
                "name": message.user.name,
            }
            for message in messages
        ]
    )
    df["emotion"] = df["emotion"].apply(lambda x: x.value)
    df["created_at"] = df["created_at"].dt.tz_convert("Asia/Tokyo")
    emotion_df = df.groupby(["emotion", "name"]).size().reset_index(name="emote_count")

    emotion_pivot = emotion_df.pivot(index="name", columns="emotion", values="emote_count").fillna(0)
    return emotion_pivot


def rms_time_series(messages: list[Message]) -> pd.DataFrame:
    df = create_dateframe(messages)
    df.sort_values(by="created_at")

    resample_rate = set_resample_term(df["created_at"].iloc[0], df["created_at"].iloc[-1])
    resampled_df = df.groupby("name").resample(resample_rate).agg({"pressure": "mean"})

    m = resampled_df["pressure"].mean()
    resampled_df = resampled_df.merge(m.rename("pressure_mean"), on="name")
    resampled_df["pressure_deviation"] = resampled_df["pressure"] - resampled_df["pressure_mean"]

    return resampled_df


def random_color(int) -> list[str]:
    palette = sns.color_palette("hls", int).as_hex()
    random.shuffle(palette)
    return palette
