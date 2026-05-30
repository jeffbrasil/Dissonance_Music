from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.session import get_db
from app.models.track import Track
from app.models.playlist import Playlist
from app.schemas.track_schema import TrackCreate, TrackResponse, TrackUpdate

router = APIRouter()


@router.post("/", response_model=TrackResponse, status_code=status.HTTP_201_CREATED)
def create_track(track_in: TrackCreate, db: Session = Depends(get_db)):
    """
    Adiciona uma nova música a uma playlist existente.
    """
    # Validação de integridade referencial
    playlist_stmt = select(Playlist).where(Playlist.id == track_in.playlist_id)
    playlist_exists = db.scalars(playlist_stmt).first()
    if not playlist_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Não é possível adicionar a música. Playlist não encontrada.",
        )

    db_track = Track(**track_in.model_dump())
    db.add(db_track)
    db.commit()
    db.refresh(db_track)
    return db_track


@router.get("/", response_model=list[TrackResponse])
def read_tracks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retorna a lista global de músicas cadastradas (Paginada).
    """
    stmt = select(Track).offset(skip).limit(limit)
    tracks = db.scalars(stmt).all()
    return tracks


@router.get("/{track_id}", response_model=TrackResponse)
def read_track_by_id(track_id: UUID, db: Session = Depends(get_db)):
    """
    Busca os detalhes de uma música específica pelo ID (UUID).
    """
    stmt = select(Track).where(Track.id == track_id)
    db_track = db.scalars(stmt).first()
    if not db_track:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Música não encontrada.",
        )
    return db_track


@router.get("/playlist/{playlist_id}", response_model=list[TrackResponse])
def read_tracks_by_playlist(playlist_id: UUID, db: Session = Depends(get_db)):
    """
    Retorna todas as músicas que pertencem a uma playlist específica.
    """
    stmt = select(Track).where(Track.playlist_id == playlist_id)
    tracks = db.scalars(stmt).all()
    return tracks


@router.put("/{track_id}", response_model=TrackResponse)
def update_track(track_id: UUID, track_in: TrackUpdate, db: Session = Depends(get_db)):
    """
    Atualiza os metadados de uma música cadastrada.
    """
    stmt = select(Track).where(Track.id == track_id)
    db_track = db.scalars(stmt).first()
    if not db_track:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Música não encontrada.",
        )

    update_data = track_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_track, key, value)

    db.commit()
    db.refresh(db_track)
    return db_track


@router.delete("/{track_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_track(track_id: UUID, db: Session = Depends(get_db)):
    """
    Remove o registro de uma música do banco de dados.
    """
    stmt = select(Track).where(Track.id == track_id)
    db_track = db.scalars(stmt).first()
    if not db_track:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Música não encontrada.",
        )

    db.delete(db_track)
    db.commit()
    return None