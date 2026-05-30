from uuid import UUID

from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class Playlist(Base):
    __tablename__ = "playlists"

    #atributos obrigatórios
    
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    alpha: Mapped[float] = mapped_column(Float, nullable=False)
    # Parâmetros matemáticos usados na geração (para histórico — US20)
    spotify_playlist_id: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    
    weight_energy: Mapped[float] = mapped_column(Float, nullable=False, default=0.4)
    weight_acousticness: Mapped[float] = mapped_column(Float, nullable=False, default=0.3)
    weight_popularity: Mapped[float] = mapped_column(Float, nullable=False, default=0.2)
    weight_valence: Mapped[float] = mapped_column(Float, nullable=False, default=0.1)

    track_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String, nullable=False, default="pending")
    # pending | processing | done | failed