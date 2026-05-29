from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import (
    User,  # Ajuste o caminho do import conforme sua estrutura
)


def test_create_user(session):
    # Create (Criar)
    new_user = User(
        spotify_id="spotify_123",
        email="user@example.com",
        display_name="John Doe",
    )
    session.add(new_user)
    session.commit()

    # Verificar se foi persistido corretamente
    assert new_user.id is not None
    assert isinstance(new_user.id, UUID)
    assert new_user.created_at is not None
    assert new_user.updated_at is not None


def test_read_user(session: Session):
    # Preparar cenário
    user = User(
        spotify_id="spotify_456",
        email="read@example.com",
        display_name="Reader",
    )
    session.add(user)
    session.commit()

    # Read (Ler)
    stmt = select(User).where(User.spotify_id == "spotify_456")
    db_user = session.scalars(stmt).first()

    assert db_user is not None
    assert db_user.email == "read@example.com"
    assert db_user.display_name == "Reader"


def test_update_user(session: Session):
    # Preparar cenário
    user = User(
        spotify_id="spotify_789",
        email="old@example.com",
        display_name="Old Name",
    )
    session.add(user)
    session.commit()

    # Update (Atualizar)
    user.display_name = "New Name"
    user.email = "new@example.com"
    session.commit()

    # Recarregar do banco para garantir a persistência
    stmt = select(User).where(User.id == user.id)
    updated_user = session.scalars(stmt).first()

    assert updated_user.display_name == "New Name"
    assert updated_user.email == "new@example.com"


def test_delete_user(session: Session):
    # Preparar cenário
    user = User(
        spotify_id="spotify_000",
        email="delete@example.com",
        display_name="To Be Deleted",
    )
    session.add(user)
    session.commit()

    # Delete (Deletar)
    session.delete(user)
    session.commit()

    # Verificar se foi removido
    stmt = select(User).where(User.id == user.id)
    deleted_user = session.scalars(stmt).first()

    assert deleted_user is None
