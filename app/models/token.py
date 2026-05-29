from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class SpotifyToken(Base):
    __tablename__ = "spotify_tokens"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)

    # Tokens armazenados criptografados (Fernet) — nunca em plaintext
    access_token_enc: Mapped[str] = mapped_column(String, nullable=False)
    refresh_token_enc: Mapped[str] = mapped_column(String, nullable=False)

    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    scope: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
