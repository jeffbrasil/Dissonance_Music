from sqlalchemy import Float, Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from uuid import UUID

from app.db.base_class import Base


class Track(Base):
    __tablename__ = "tracks"

    playlist_id: Mapped[UUID] = mapped_column(
        ForeignKey("playlists.id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )

    spotify_track_id: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    artist: Mapped[str] = mapped_column(String, nullable=False)
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    album: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    
    # Audio features (fonte: AcousticBrainz ou Librosa)
    danceability: Mapped[float] = mapped_column(Float, nullable=False, default=None)
    energy: Mapped[float] = mapped_column(Float, nullable=False, default=None)
    acousticness: Mapped[float] = mapped_column(Float, nullable=False, default=None)
    valence: Mapped[float] = mapped_column(Float, nullable=False, default=None)
    bpm: Mapped[float] = mapped_column(Float, nullable=False, default=None)

    # Score pré-calculado para evitar recalcular a cada busca
    dissonance_score: Mapped[float | None] = mapped_column(Float, nullable=True, default=None)