from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.session import get_db
from app.models.playlist import Playlist
from app.models.user import User
from app.schemas.playlist_schema import PlaylistCreate, PlaylistResponse, PlaylistUpdate

router = APIRouter()


@router.post("/", response_model=PlaylistResponse, status_code=status.HTTP_201_CREATED)
def create_playlist(playlist_in: PlaylistCreate, db: Session = Depends(get_db)):
    """
    Cria uma nova playlist associada a um usuário existente.
    """
    # Validação de integridade: o usuário precisa existir no sistema
    user_stmt = select(User).where(User.id == playlist_in.user_id)
    user_exists = db.scalars(user_stmt).first()
    if not user_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Não é possível criar a playlist. Usuário não encontrado.",
        )

    db_playlist = Playlist(**playlist_in.model_dump())
    db.add(db_playlist)
    db.commit()
    db.refresh(db_playlist)
    return db_playlist


@router.get("/", response_model=list[PlaylistResponse])
def read_playlists(skip: int = 0, limit: int = 25, db: Session = Depends(get_db)):
    """
    Retorna uma lista de todas as playlists cadastradas (Paginada).
    """
    stmt = select(Playlist).offset(skip).limit(limit)
    playlists = db.scalars(stmt).all()
    return playlists


@router.get("/{playlist_id}", response_model=PlaylistResponse)
def read_playlist_by_id(playlist_id: UUID, db: Session = Depends(get_db)):
    """
    Busca os detalhes de uma playlist específica pelo ID (UUID).
    """
    stmt = select(Playlist).where(Playlist.id == playlist_id)
    db_playlist = db.scalars(stmt).first()
    if not db_playlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playlist não encontrada.",
        )
    return db_playlist


@router.put("/{playlist_id}", response_model=PlaylistResponse)
def update_playlist(playlist_id: UUID, playlist_in: PlaylistUpdate, db: Session = Depends(get_db)):
    """
    Atualiza os parâmetros ou o status de uma playlist existente.
    """
    stmt = select(Playlist).where(Playlist.id == playlist_id)
    db_playlist = db.scalars(stmt).first()
    if not db_playlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playlist não encontrada.",
        )

    # Coleta apenas as chaves explicitamente passadas no corpo do JSON
    update_data = playlist_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_playlist, key, value)

    db.commit()
    db.refresh(db_playlist)
    return db_playlist


@router.delete("/{playlist_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_playlist(playlist_id: UUID, db: Session = Depends(get_db)):
    """
    Remove o registro de uma playlist do banco de dados.
    """
    stmt = select(Playlist).where(Playlist.id == playlist_id)
    db_playlist = db.scalars(stmt).first()
    if not db_playlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playlist não encontrada.",
        )

    db.delete(db_playlist)
    db.commit()
    return None