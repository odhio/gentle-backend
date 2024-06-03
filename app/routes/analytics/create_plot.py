from crud.message import get_messages_by_room_uuid_user_joined
from pydantic import BaseModel
from typing import Union
from lib.analytics import (
    user_time_series,
    emotion_time_series,
    emotion_summary,
    topics_time_series,
    rms_time_series,
    topics_summary,
    random_color,
    term_combination,
)
from domains.models import Emotion
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime


class CreatePlotRequest(BaseModel):
    room_uuid: str


# Emotion表示用カラーパレット
class Color(BaseModel):
    HAPPY: str = "#EFA000"
    SAD: str = "#474799"
    ANGER: str = "#CD1F43"
    FEAR: str = "#7B3380"
    DISGUST: str = "#AA2763"
    NEUTRAL: str = "#A3B300"


# Chart.js用データ構造
class LineType(BaseModel):
    label: str
    data: Union[list[int], list[float]]
    borderColor: str | list[str]
    backgroundColor: str | list[str]


class CircleType(BaseModel):
    label: str
    data: Union[list[int], list[float]]
    borderColor: str | list[str]
    backgroundColor: str | list[str]


class ChartJSData(BaseModel):
    labels: list[str]
    datasets: list[LineType] | list[CircleType]


class TopicsTimeSeries(BaseModel):
    """
    sample:
    {
        "topics": [
            {"プロジェクト": 5,"進捗": 2,"ステップ": 2...},
            {"会議": 3, "明日": 2, "資料": 1...},
            {"会議室": 2, "予約": 1, "明日": 1...},
        ],
        "segments": [
            "2024-05-01 00:00:00",
            "2024-05-01 00:05:00",
            "2024-05-01 00:010:00",
        ]
    }
    """

    topics: list[dict[str, int]]
    segments: list[str]


class TopicsSammry(BaseModel):
    """
    sample:
    {
        "simple_count": {
            "プロジェクト": 5,
            "進捗": 2,
            "ステップ": 2, ...
        },
        "tfidf": {
            "テスト": 1.86..,
            "内容": 1.23...,
            "ステップ": 0.2..., ...
        }
    }
    """

    simple_count: dict[str, int]
    tfidf: dict[str, float]


class TermCombination(BaseModel):
    col_1: dict[int, str]
    col_2: dict[int, str]
    count: dict[int, int]


class CreatePlotResponse(BaseModel):
    user_time_series: ChartJSData
    emotion_time_series: ChartJSData
    emotion_summary: ChartJSData
    topics_time_series: TopicsTimeSeries
    rms_time_series: ChartJSData
    topics_summary: TopicsSammry
    term_combination: TermCombination


def set_color(emotion):
    return getattr(Color(), emotion.upper(), "#A3B300")


async def handler(db: AsyncSession, room_uuid: str) -> CreatePlotResponse:
    messages = await get_messages_by_room_uuid_user_joined(db, room_uuid)

    user_ts = user_time_series(messages)
    # ユーザ数に応じて色を生成(色の一貫性を保つために使い回す)
    user_ts_color = random_color(len(user_ts.columns.to_list()))
    user_ts_response = ChartJSData(
        labels=[ts.strftime("%Y-%m-%d %H:%M:%S") for ts in user_ts.index.tolist()],
        datasets=[
            LineType(
                label=col,
                data=user_ts[col].tolist(),
                borderColor=user_ts_color[i],
                backgroundColor=user_ts_color[i],
            )
            for i, col in enumerate(user_ts.columns)
        ],
    )

    emotion_ts = emotion_time_series(messages)
    emotion_ts_response = ChartJSData(
        labels=[ts.strftime("%Y-%m-%d %H:%M:%S") for ts in emotion_ts.index.tolist()],
        datasets=[
            LineType(
                label=col,
                data=emotion_ts[col].to_list(),
                borderColor=set_color(col),
                backgroundColor=set_color(col),
            )
            for i, col in enumerate(emotion_ts.columns)
        ],
    )

    emotion_sum = emotion_summary(messages)
    emotion_sum_response = ChartJSData(
        labels=emotion_sum.columns.to_list(),
        datasets=[
            CircleType(
                label=i,
                data=row.to_list(),
                borderColor=[set_color(col) for col in emotion_sum.columns],
                backgroundColor=[set_color(col) for col in emotion_sum.columns],
            )
            for i, row in emotion_sum.iterrows()
        ],
    )

    topics_ts = topics_time_series(messages)
    topics_ts_response = TopicsTimeSeries(
        topics=[dict(v.most_common(10)) for v in topics_ts["message"].to_list()],
        segments=[ts.strftime("%Y-%m-%d %H:%M:%S") for ts in user_ts.index.tolist()],
    )

    rms_ts, time_range = rms_time_series(messages)
    rms_list = []

    i = 0
    for name, group in rms_ts.groupby(level=0):
        rms_list.append(
            LineType(
                label=name,
                data=group["pressure_zsore"].to_list(),
                borderColor=user_ts_color[i],
                backgroundColor=user_ts_color[i],
            )
        )
        i += 1
    rms_rs_response = ChartJSData(
        labels=[ts.strftime("%Y-%m-%d %H:%M:%S") for ts in time_range],
        datasets=rms_list,
    )

    countup, tfidf = topics_summary(messages)

    term_comb = term_combination(messages)
    term_comb_response = TermCombination(
        col_1=term_comb["col_1"],
        col_2=term_comb["col_2"],
        count=term_comb["count"],
    )

    return CreatePlotResponse(
        user_time_series=user_ts_response,
        emotion_time_series=emotion_ts_response,
        emotion_summary=emotion_sum_response,
        topics_time_series=topics_ts_response,
        rms_time_series=rms_rs_response,
        topics_summary=TopicsSammry(simple_count=countup, tfidf=tfidf),
        term_combination=term_comb_response,
    )
