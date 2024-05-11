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
