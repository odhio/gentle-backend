from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    ForeignKey,
    Enum,
    Text,
    DateTime,
    func,
    JSON,
    Boolean,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship, joinedload, selectinload
from sqlalchemy.sql import func
import enum
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    uuid = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    image = Column(String, nullable=False)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        onupdate=func.now(),
    )

    messages = relationship("Message", back_populates="user")
    rooms = relationship("RoomMember", back_populates="user")

class Emotion(enum.Enum):
    HAPPY = "happy"
    SAD = "sad"
    ANGER = "anger"
    FEAR = "fear"
    DISGUST = "disgust"
    NEUTRAL = "neutral"


class Room(Base):
    __tablename__ = "rooms"

    uuid = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    emotion = Column(Enum(Emotion), default=Emotion.NEUTRAL, nullable=False)
    summary = Column(Text, default="", nullable=False)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        onupdate=func.now(),
    )
    closed_at = Column(DateTime(timezone=True), nullable=True)

    members = relationship("RoomMember", back_populates="room")
    messages = relationship("Message", back_populates="room")


class RoomMember(Base):
    __tablename__ = "room_members"

    uuid = Column(String, primary_key=True, index=True)
    room_uuid = Column(String, ForeignKey("rooms.uuid"), nullable=False)
    user_uuid = Column(String, ForeignKey("users.uuid"), nullable=False)
    summary = Column(Text, default="", nullable=False)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        onupdate=func.now(),
    )
    UniqueConstraint("room_uuid", "user_uuid")

    room = relationship("Room", back_populates="members")
    user = relationship("User", back_populates="rooms")

class Message(Base):
    __tablename__ = "messages"

    uuid = Column(String, primary_key=True, index=True)
    room_uuid = Column(String, ForeignKey("rooms.uuid"), nullable=False)
    user_uuid = Column(String, ForeignKey("users.uuid"), nullable=False)
    message = Column(Text, nullable=False)
    emotion = Column(Enum(Emotion), nullable=False)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        onupdate=func.now(),
    )

    room = relationship("Room", back_populates="messages")
    user = relationship("User", back_populates="messages")
