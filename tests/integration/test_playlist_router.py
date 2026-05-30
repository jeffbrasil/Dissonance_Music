import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session
from uuid import uuid4

from app.models.playlist import Playlist
from app.models.user import User




@pytest.fixture
def db_user(session: Session) -> User:
    """Insere um usuário padrão para ser dono das playlists nos testes."""
    user = User(
        spotify_id="user_playlist_owner",
        email="owner@example.com",
        display_name="Playlist Owner"
    )
    session.add(user)
    session.commit()
    return user


@pytest.fixture
def playlist_payload(db_user: User) -> dict:
    """Retorna um payload padrão de criação baseado no usuário existente."""
    return {
        "user_id": str(db_user.id),
        "alpha": 0.5,
        "spotify_playlist_id": "spotify_list_123",
        "weight_energy": 0.4,
        "weight_acousticness": 0.3,
        "weight_popularity": 0.2,
        "weight_valence": 0.1,
        "track_count": 10,
        "status": "pending"
    }


@pytest.fixture
def db_playlist(session: Session, db_user: User) -> Playlist:
    """Insere uma playlist padrão diretamente no banco de dados."""
    playlist = Playlist(
        user_id=db_user.id,
        alpha=0.75,
        spotify_playlist_id="spotify_existente_789",
        status="processing"
    )
    session.add(playlist)
    session.commit()
    return playlist




def test_create_playlist_success(client: TestClient, playlist_payload: dict):
    response = client.post("/playlists/", json=playlist_payload)
    
    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == playlist_payload["user_id"]
    assert data["alpha"] == playlist_payload["alpha"]
    assert data["status"] == "pending"
    assert "id" in data


def test_create_playlist_user_not_found(client: TestClient, playlist_payload: dict):
    # Substitui por um UUID aleatório que não existe no banco de dados
    playlist_payload["user_id"] = str(uuid4())
    
    response = client.post("/playlists/", json=playlist_payload)
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Não é possível criar a playlist. Usuário não encontrado."



def test_read_playlists_empty(client: TestClient):
    response = client.get("/playlists/")
    assert response.status_code == 200
    assert response.json() == []


def test_read_playlists_with_data(client: TestClient, db_playlist: Playlist):
    response = client.get("/playlists/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["spotify_playlist_id"] == db_playlist.spotify_playlist_id


def test_read_playlist_by_id_success(client: TestClient, db_playlist: Playlist):
    response = client.get(f"/playlists/{db_playlist.id}")
    assert response.status_code == 200
    assert response.json()["spotify_playlist_id"] == db_playlist.spotify_playlist_id


def test_read_playlist_by_id_not_found(client: TestClient):
    fake_uuid = uuid4()
    response = client.get(f"/playlists/{fake_uuid}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Playlist não encontrada."


# --- TESTES DE ATUALIZAÇÃO (PUT) ---

def test_update_playlist_success(client: TestClient, db_playlist: Playlist):
    update_payload = {
        "status": "done",
        "track_count": 25,
        "alpha": 0.12
    }
    
    response = client.put(f"/playlists/{db_playlist.id}", json=update_payload)
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "done"
    assert data["track_count"] == 25
    assert data["alpha"] == 0.12
    # Verifica se os campos não enviados mantiveram o valor original
    assert data["spotify_playlist_id"] == db_playlist.spotify_playlist_id


# --- TESTES DE REMOÇÃO (DELETE) ---

def test_delete_playlist_success(client: TestClient, session: Session, db_playlist: Playlist):
    response = client.delete(f"/playlists/{db_playlist.id}")
    assert response.status_code == 204
    assert response.content == b""
    
    # Validação direta a nível de persistência no banco de dados
    stmt = select(Playlist).where(Playlist.id == db_playlist.id)
    db_check = session.scalars(stmt).first()
    assert db_check is None

# --- TESTES DE VALIDAÇÃO DE LIMITES E NEGÓCIO (ITENS 1, 2, 4, 5) ---

def test_create_playlist_invalid_weights_upper_limit(client: TestClient, playlist_payload: dict):
    """Item 1: Verifica se o Pydantic bloqueia pesos acima do limite máximo [1.0]."""
    playlist_payload["weight_energy"] = 1.5  # Limite máximo é 1.0
    
    response = client.post("/playlists/", json=playlist_payload)
    assert response.status_code == 422  # Unprocessable Entity


def test_create_playlist_invalid_weights_lower_limit(client: TestClient, playlist_payload: dict):
    """Item 2: Verifica se o Pydantic bloqueia pesos abaixo do limite mínimo [0.0]."""
    playlist_payload["weight_acousticness"] = -0.1  # Limite mínimo é 0.0
    
    response = client.post("/playlists/", json=playlist_payload)
    assert response.status_code == 422  # Unprocessable Entity

def test_create_playlist_optional_fields_null(client: TestClient, playlist_payload: dict):
    """Item 2: Garante que a API aceita a omissão de campos nullable."""
    playlist_payload["spotify_playlist_id"] = None
    
    response = client.post("/playlists/", json=playlist_payload)
    assert response.status_code == 201
    assert response.json()["spotify_playlist_id"] is None


def test_update_playlist_invalid_status(client: TestClient, db_playlist: Playlist):
    """Item 4: Impede a atualização para um status não mapeado (Regra de Negócio)."""
    # Se você mapear o status como Literal ou Enum no Pydantic, o retorno será 422.
    # Caso trate na rota via HTTPException, pode validar o 400.
    update_payload = {"status": "status_inexistente_invalido"}
    
    response = client.put(f"/playlists/{db_playlist.id}", json=update_payload)
    
    # Se o Schema aceita qualquer string, o teste abaixo falhará até que um Enum/Literal seja inserido no Pydantic.
    # Se o Pydantic já restringir o campo status, retornará 422.
    assert response.status_code in [400, 422]


def test_read_playlists_invalid_pagination(client: TestClient):
    """Item 5: Envio de parâmetros de paginação incorretos (Tipo inválido)."""
    response = client.get("/playlists/?limit=cinco&skip=-1")
  
    assert response.status_code == 422