from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime


class TrackBase(BaseModel):
    playlist_id: UUID = Field(..., description="ID da playlist à qual a música pertence")
    spotify_track_id: str = Field(..., description="ID único da música no Spotify")
    title: str = Field(..., description="Título da faixa")
    artist: str = Field(..., description="Nome do artista ou banda")
    album: str | None = Field(default=None, description="Nome do álbum")
    duration_ms: int = Field(..., ge=0, description="Duração da música em milissegundos")
    
    # Atributos de áudio (Audio Features)
    danceability: float = Field(..., ge=0.0, le=1.0)
    energy: float = Field(..., ge=0.0, le=1.0)
    acousticness: float = Field(..., ge=0.0, le=1.0)
    valence: float = Field(..., ge=0.0, le=1.0)
    bpm: float = Field(..., ge=0.0, description="Ritmo em batidas por minuto (BPM)")


class TrackCreate(TrackBase):
    """Schema para criação de uma música (Request)."""
    pass


class TrackUpdate(BaseModel):
    """Schema para atualização parcial de uma música (Request)."""
    title: str | None = None
    artist: str | None = None
    album: str | None = None
    duration_ms: int | None = Field(default=None, ge=0)
    popularity: int | None = Field(default=None, ge=0, le=100)
    danceability: float | None = Field(default=None, ge=0.0, le=1.0)
    energy: float | None = Field(default=None, ge=0.0, le=1.0)
    acousticness: float | None = Field(default=None, ge=0.0, le=1.0)
    valence: float | None = Field(default=None, ge=0.0, le=1.0)
    tempo: float | None = Field(default=None, ge=0.0)


class TrackResponse(TrackBase):
    """Schema para retorno de dados formatados (Response)."""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True