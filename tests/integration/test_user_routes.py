import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.user import User


# --- FIXTURES DE DADOS (Payloads e Modelos padrão) ---

@pytest.fixture
def user_payload():
    """Retorna um dicionário padrão para envio em requisições POST/PUT."""
    return {
        "spotify_id": "spotify_integration_123",
        "email": "integration@example.com",
        "display_name": "Integration User"
    }


@pytest.fixture
def db_user(session: Session) -> User:
    """Insere e retorna um usuário padrão diretamente no banco de dados."""
    user = User(
        spotify_id="db_user_789",
        email="db_user@example.com",
        display_name="Database User"
    )
    session.add(user)
    session.commit()
    return user


# --- TESTES DO CORPO DE CRIAÇÃO (POST) ---

def test_create_user_route_success(client: TestClient, user_payload: dict):
    response = client.post("/users/", json=user_payload)
    
    assert response.status_code == 201
    data = response.json()
    assert data["spotify_id"] == user_payload["spotify_id"]
    assert "id" in data


def test_create_user_route_duplicate_spotify_id(client: TestClient, db_user: User, user_payload: dict):
    # Força o payload a usar o mesmo spotify_id do usuário já existente
    user_payload["spotify_id"] = db_user.spotify_id
    
    response = client.post("/users/", json=user_payload)
    
    assert response.status_code == 400
    assert response.json()["detail"] == "Usuário com este Spotify ID já está cadastrado."


# --- TESTES DE LEITURA (GET) ---

def test_read_users_route_empty(client: TestClient):
    response = client.get("/users/")
    assert response.status_code == 200
    assert response.json() == []


def test_read_users_route_with_data(client: TestClient, db_user: User):
    response = client.get("/users/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["spotify_id"] == db_user.spotify_id


def test_read_user_by_id_success(client: TestClient, db_user: User):
    print(f"O id é: {db_user.id}", db_user.id)
    response = client.get(f"/users/{db_user.id}")
    assert response.status_code == 200
    assert response.json()["spotify_id"] == db_user.spotify_id


def test_read_user_by_id_not_found(client: TestClient):
    fake_uuid = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/users/{fake_uuid}")
    assert response.status_code == 404


# --- TESTES DE ATUALIZAÇÃO (PUT) ---

def test_update_user_route_success(client: TestClient, db_user: User):
    update_payload = {"email": "new_email@test.com", "display_name": "New Name"}
    
    response = client.put(f"/users/{db_user.id}", json=update_payload)
    assert response.status_code == 200
    
    data = response.json()
    assert data["email"] == update_payload["email"]
    assert data["display_name"] == update_payload["display_name"]
    assert data["spotify_id"] == db_user.spotify_id  # Mantém o ID original


# --- TESTES DE REMOÇÃO (DELETE) ---

def test_delete_user_route_success(client: TestClient, session: Session, db_user: User):
    response = client.delete(f"/users/{db_user.id}")
    assert response.status_code == 204
    assert response.content == b"" 

    # Validação direta na sessão do banco
    db_check = session.scalars(select(User).where(User.id == db_user.id)).first()
    assert db_check is None