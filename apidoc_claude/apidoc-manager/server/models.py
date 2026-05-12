"""SQLAlchemy ORM models."""
from __future__ import annotations
import hashlib, json
from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase): pass

def _utcnow() -> datetime: return datetime.now(timezone.utc)

class Spec(Base):
    __tablename__ = "specs"
    id:             Mapped[int]      = mapped_column(Integer, primary_key=True, autoincrement=True)
    name:           Mapped[str]      = mapped_column(String(255), nullable=False, index=True)
    description:    Mapped[str]      = mapped_column(Text, nullable=False, default="")
    latest_version: Mapped[str]      = mapped_column(String(50), nullable=False, default="")
    created_at:     Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utcnow)
    updated_at:     Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False,
                                                     default=_utcnow, onupdate=_utcnow)
    versions: Mapped[list["SpecVersion"]] = relationship(
        "SpecVersion", back_populates="spec", cascade="all, delete-orphan",
        order_by="SpecVersion.created_at.desc()")

    @property
    def versions_count(self) -> int: return len(self.versions)

class SpecVersion(Base):
    __tablename__ = "spec_versions"
    id:           Mapped[int]      = mapped_column(Integer, primary_key=True, autoincrement=True)
    spec_id:      Mapped[int]      = mapped_column(Integer, ForeignKey("specs.id", ondelete="CASCADE"),
                                                   nullable=False, index=True)
    version:      Mapped[str]      = mapped_column(String(50), nullable=False)
    content:      Mapped[str]      = mapped_column(Text, nullable=False)
    content_hash: Mapped[str]      = mapped_column(String(64), nullable=False, index=True)
    changelog:    Mapped[str]      = mapped_column(Text, nullable=False, default="")
    created_at:   Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utcnow)
    spec: Mapped["Spec"] = relationship("Spec", back_populates="versions")

    @staticmethod
    def compute_hash(content_dict: dict) -> str:
        raw = json.dumps(content_dict, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(raw.encode()).hexdigest()

    def get_content(self) -> dict: return json.loads(self.content)
