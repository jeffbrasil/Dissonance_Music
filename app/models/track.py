from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class Track(Base):
    __tablename__ = "tracks"

    spotify_id: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    artist: Mapped[str] = mapped_column(String, nullable=False)
    album: Mapped[str | None] = mapped_column(String, nullable=True, default=None)

    # Audio features (fonte: AcousticBrainz ou Librosa)
    energy: Mapped[float | None] = mapped_column(Float, nullable=True, default=None)
    acousticness: Mapped[float | None] = mapped_column(Float, nullable=True, default=None)
    valence: Mapped[float | None] = mapped_column(Float, nullable=True, default=None)
    popularity: Mapped[float | None] = mapped_column(Float, nullable=True, default=None)
    bpm: Mapped[float | None] = mapped_column(Float, nullable=True, default=None)
    key: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)

    # Score pré-calculado para evitar recalcular a cada busca
    dissonance_score: Mapped[float | None] = mapped_column(Float, nullable=True, default=None)