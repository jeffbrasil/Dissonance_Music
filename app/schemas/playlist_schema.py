from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime


class PlaylistBase(BaseModel):
    """Campos base compartilhados entre os schemas de Playlist."""
    user_id: UUID = Field(..., description="ID do usuário dono da playlist")
    alpha: float = Field(..., description="Parâmetro matemático de atenuação (alpha)")
    spotify_playlist_id: str | None = Field(default=None, description="ID gerado pelo Spotify")
    weight_energy: float = Field(default=0.4, ge=0.0, le=1.0, description="Peso da energia")
    weight_acousticness: float = Field(default=0.3, ge=0.0, le=1.0, description="Peso da acústica")
    weight_popularity: float = Field(default=0.2, ge=0.0, le=1.0, description="Peso da popularidade")
    weight_valence: float = Field(default=0.1, ge=0.0, le=1.0, description="Peso da valência")
    track_count: int = Field(default=0, ge=0, description="Quantidade de faixas")
    status: str = Field(default="pending", description="Status do processamento da playlist")


class PlaylistCreate(PlaylistBase):
    """Schema para os dados recebidos na criação de uma playlist (Request)."""
    pass


class PlaylistUpdate(BaseModel):
    """Schema para atualização de dados da playlist (Request)."""
    # Todos os campos são opcionais para permitir atualização parcial (PATCH/PUT)
    spotify_playlist_id: str | None = None
    alpha: float | None = None
    weight_energy: float | None = Field(default=None, ge=0.0, le=1.0)
    weight_acousticness: float | None = Field(default=None, ge=0.0, le=1.0)
    weight_popularity: float | None = Field(default=None, ge=0.0, le=1.0)
    weight_valence: float | None = Field(default=None, ge=0.0, le=1.0)
    track_count: int | None = Field(default=None, ge=0)
    status: str | None = None


class PlaylistResponse(PlaylistBase):
    """Schema para retorno de dados formatados pela API (Response)."""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True