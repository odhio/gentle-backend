import pandas as pd
import datetime
from domains.models import Message
import seaborn as sns
import random
from lib.janome import ranking_words, create_term_document_matrix, create_tfidf_matrix, create_term_combination


def set_resample_term(start: pd.Timestamp, end: pd.Timestamp) -> str:
    duration = (end - start).total_seconds() / 60
    if duration < 10:
        return "1T"
    resample_rate = f"{int(duration/10)}T"

    return resample_rate


def set_zscore(x):
    return (x - x.mean()) / x.std()


# ごちゃついてるので後で整理したい
def create_dateframe(messages: list[Message]) -> pd.DataFrame:
    df = pd.DataFrame(
        [
            {
                "user_uuid": message.user_uuid,
                "message": message.message,
                "created_at": message.created_at,
                "emotion": message.emotion,
                "pressure": message.pressure,
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
    df = df.sort_values(by="created_at")

    resample_rate = set_resample_term(df.index[0], df.index[-1])
    resampled_df = df.groupby("name").resample(resample_rate).size().unstack(fill_value=0)
    time_series_pivot = resampled_df.T

    return time_series_pivot


def emotion_time_series(messages: list[Message]) -> pd.DataFrame:
    df = create_dateframe(messages)
    df = df.sort_values(by="created_at")

    resample_rate = set_resample_term(df.index[0], df.index[-1])
    df["emotion"] = df["emotion"].apply(lambda x: x.value)
    resampled_df = df.groupby("emotion").resample(resample_rate).size().unstack(fill_value=0)

    time_series_pivot = resampled_df.T

    return time_series_pivot


def topics_time_series(messages: list[Message]) -> pd.DataFrame:
    df = create_dateframe(messages)
    df = df.sort_values("created_at")

    resample_rate = set_resample_term(df.index[0], df.index[-1])
    resampled_df = df.resample(resample_rate).agg({"message": lambda x: ranking_words(x.tolist())})

    return resampled_df


def emotion_summary(messages: list[Message]) -> pd.DataFrame:
    df = create_dateframe(messages)

    df["emotion"] = df["emotion"].apply(lambda x: x.value)
    emotion_df = df.groupby(["emotion", "name"]).size().reset_index(name="emote_count")

    emotion_pivot = emotion_df.pivot(index="name", columns="emotion", values="emote_count").fillna(0)

    return emotion_pivot


def rms_time_series(messages: list[Message]) -> pd.DataFrame:
    """
    INPUT:
        [Message, Message, Message, ...]
    OUTPUT:
        DataFrame with columns:
            - pressure
            - pressure_deviation

        DataFrame(Multi-level):
            - Level 0: 'name'
            - Level 1: 'created_at'
    """

    df = create_dateframe(messages)
    df = df.sort_values(by="created_at")

    resample_rate = set_resample_term(df.index[0], df.index[-1])

    time_range = pd.date_range(start=df.index[0], end=df.index[-1], freq=resample_rate)

    result = []
    for name, group in df.groupby("name"):
        resampled_df = group.resample(resample_rate).agg({"pressure": "mean"}).fillna(0)

        # 音量/音圧関係は環境差がでかいので平均をとって集計区間にサンプル(発話)が存在する場合はその偏差を算出
        # 比較的音圧が大きい区間は相対的に重要度が高い/議論が集中した可能性があるのではという仮説検証
        resampled_df["name"] = name
        resampled_df["pressure_zsore"] = resampled_df["pressure"].transform(set_zscore).fillna(0)

        result.append(resampled_df)
    resampled_df = pd.concat(result)
    resampled_df.reset_index(inplace=True)
    resampled_df.rename(columns={"index": "created_at"}, inplace=True)
    resampled_df.set_index(["name", "created_at"], inplace=True)

    # 他のtsと時系列を合わせたかったのですが、うまくいかなかったので一旦reindexで使用したtime_rangeを一緒に返してます。
    # 上位の関数を立ててindex範囲を定義して各関数に渡すよう変更を考えてます(FEでの表示データ欠落にもつながるので)。
    return resampled_df, time_range


def topics_summary(messages: list[Message]) -> dict[str, int | float]:
    """
    INPUT:
        [Message, Message, Message, ...]
        -> create_term_document_matrix/ create_tfidf_matrix([Message.message, Message.message, Message.message, ...])
    OUTPUT:
        DataFrame(countup/ tfidf)
    """
    df = create_dateframe(messages)
    sentences = df["message"].tolist()
    countup = create_term_document_matrix(sentences)
    tfidf = create_tfidf_matrix(sentences)

    return countup, tfidf


def term_combination(messages: list[Message]) -> dict[str, int]:
    """
    INPUT:
        [Message, Message, Message, ...]
        -> create_term_document_matrix([Message.message, Message.message, Message.message, ...])
    OUTPUT:
        DataFrame
    """
    df = create_dateframe(messages)
    sentences = df["message"].tolist()
    term_comb = create_term_combination(sentences)

    return term_comb


def random_color(int) -> list[str]:
    palette = sns.color_palette("hls", int).as_hex()
    random.shuffle(palette)

    return palette
