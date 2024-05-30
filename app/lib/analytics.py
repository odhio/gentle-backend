import pandas as pd
from domains.models import Message
import seaborn as sns
import random


def user_time_series(messages: list[Message]) -> pd.DataFrame:
    df = pd.DataFrame(
        [
            {
                "message_uuid": message.uuid,
                "room_uuid": message.room_uuid,
                "user_uuid": message.user_uuid,  # count
                "message": message.message,  # count
                "created_at": message.created_at,  # order
                "name": message.user.name,  # count
            }
            for message in messages
        ]
    )
    df["created_at"] = df["created_at"].dt.tz_convert("Asia/Tokyo")
    print(df["created_at"])
    df.set_index("created_at", inplace=True)
    resampled_df = df.groupby("name").resample("1T").size().unstack(fill_value=0)
    time_series_pivot = resampled_df.T
    return time_series_pivot


def emotion_time_series(messages: list[Message]) -> pd.DataFrame:
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
    df.set_index("created_at", inplace=True)
    resampled_df = df.groupby("emotion").resample("1T").size().unstack(fill_value=0)
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


def random_color(int) -> list[str]:
    palette = sns.color_palette("hls", int).as_hex()
    random.shuffle(palette)
    return palette
