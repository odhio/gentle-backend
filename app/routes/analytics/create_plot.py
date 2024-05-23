from crud.message import get_messages_by_room_uuid_user_joined
from pydantic import BaseModel
from lib.analytics import user_time_series, emotion_time_series, emotion_summary, random_color
from domains.models import Emotion
from sqlalchemy.ext.asyncio import AsyncSession


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
    data: list[int]
    borderColor: str | list[str]
    backgroundColor: str | list[str]


class CircleType(BaseModel):
    label: str
    data: list[int]
    borderColor: str | list[str]
    backgroundColor: str | list[str]


class ChartJSData(BaseModel):
    labels: list[str]
    datasets: list[LineType] | list[CircleType]


class CreatePlotRequest(BaseModel):
    room_uuid: str


#
class CreatePlotResponse(BaseModel):
    user_time_series: ChartJSData
    emotion_time_series: ChartJSData
    emotion_summary: ChartJSData


def set_color(emotion):
    return getattr(Color(), emotion.upper(), "#A3B300")


async def handler(db: AsyncSession, room_uuid: str) -> CreatePlotResponse:
    messages = await get_messages_by_room_uuid_user_joined(db, room_uuid)

    user_ts = user_time_series(messages)

    user_ts_color = random_color(len(user_ts.columns.to_list()))  # ユーザ数に応じて色を生成

    emotion_ts = emotion_time_series(messages)
    emotion_sum = emotion_summary(messages)

    return CreatePlotResponse(
        user_time_series=(
            ChartJSData(
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
        ),
        emotion_time_series=(
            ChartJSData(
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
        ),
        emotion_summary=(
            ChartJSData(
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
        ),
    )
