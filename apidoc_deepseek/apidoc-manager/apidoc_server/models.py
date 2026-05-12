"""Database models for APIDoc Server."""

from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Specification(Base):
    __tablename__ = "specifications"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text)
    version: Mapped[str] = mapped_column(String(50))
    tags: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    versions: Mapped[list["SpecVersion"]] = relationship("SpecVersion", back_populates="specification", cascade="all, delete-orphan")


class SpecVersion(Base):
    __tablename__ = "spec_versions"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    spec_id: Mapped[int] = mapped_column(ForeignKey("specifications.id", ondelete="CASCADE"))
    version: Mapped[str] = mapped_column(String(50))
    content: Mapped[dict] = mapped_column(JSON)
    format: Mapped[str] = mapped_column(String(10), default="json")
    changelog: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_by: Mapped[Optional[str]] = mapped_column(String(255))
    specification: Mapped["Specification"] = relationship("Specification", back_populates="versions")
