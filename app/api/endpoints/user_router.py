from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.db.session import get_db
from app.models.user import User
from app.schemas.user_schema import UserCreate, UserResponse, UserUpdate

router = APIRouter()


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Cria um novo usuário no sistema.
    Verifica se o spotify_id já está cadastrado para evitar duplicidade.
    """
    # Verificar unicidade do spotify_id
    stmt = select(User).where(User.spotify_id == user_in.spotify_id)
    existing_user = db.scalars(stmt).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário com este Spotify ID já está cadastrado.",
        )

    # O modelo mapeado como dataclass aceita os argumentos desestruturados do Pydantic
    db_user = User(**user_in.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get("/", response_model=list[UserResponse])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retorna uma lista de usuários paginada.
    """
    stmt = select(User).offset(skip).limit(limit)
    users = db.scalars(stmt).all()
    return users


@router.get("/{user_id}", response_model=UserResponse)
def read_user_by_id(user_id: UUID, db: Session = Depends(get_db)):
    """
    Busca um usuário específico pelo ID (UUID).
    """
    stmt = select(User).where(User.id == user_id)
    db_user = db.scalars(stmt).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado.",
        )
    return db_user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: UUID, user_in: UserUpdate, db: Session = Depends(get_db)):
    """
    Atualiza os dados de um usuário existente de forma parcial.
    """
    stmt = select(User).where(User.id == user_id)
    db_user = db.scalars(stmt).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado.",
        )

    # Extrai apenas os campos que foram explicitamente enviados na requisição
    update_data = user_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)
    return db_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: UUID, db: Session = Depends(get_db)):
    """
    Remove um usuário do banco de dados.
    """
    stmt = select(User).where(User.id == user_id)
    db_user = db.scalars(stmt).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado.",
        )

    db.delete(db_user)
    db.commit()
    return None