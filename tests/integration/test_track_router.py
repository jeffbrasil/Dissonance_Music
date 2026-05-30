import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session
from uuid import uuid4

from app.models.user import User
from app.models.playlist import Playlist
from app.models.track import Track


# --- FIXTURES DE SUPORTE (Árvore de Dependências) ---

@pytest.fixture
def db_user(session: Session) -> User:
    """Insere o usuário dono da playlist."""
    user = User(
        spotify_id="user_track_test",
        email="track_test@example.com",
        display_name="Track Tester"
    )
    session.add(user)
    session.commit()
    return user


@pytest.fixture
def db_playlist(session: Session, db_user: User) -> Playlist:
    """Insere a playlist que conterá as músicas."""
    playlist = Playlist(
        user_id=db_user.id,
        alpha=0.5,
        spotify_playlist_id="playlist_for_tracks",
        status="pending"
    )
    session.add(playlist)
    session.commit()
    return playlist


@pytest.fixture
def track_payload(db_playlist: Playlist) -> dict:
    """Retorna um payload padrão de criação de música."""
    return {
        "playlist_id": str(db_playlist.id),
        "spotify_track_id": "spotify_track_abc123",
        "title": "Song Title Test",
        "artist": "Test Artist",
        "album": "Test Album",
        "duration_ms": 180000,
        "danceability": 0.8,
        "energy": 0.7,
        "acousticness": 0.1,
        "valence": 0.6,
        "bpm": 120.0
    }


@pytest.fixture
def db_track(session: Session, db_playlist: Playlist) -> Track:
    """Insere uma música padrão diretamente no banco de dados para testes de leitura/alteração."""
    track = Track(
        playlist_id=db_playlist.id,
        spotify_track_id="spotify_track_existente",
        title = "Existing Song",
        artist = "Existing Artist",
        album = "Existing Album",
        duration_ms = 200000,
        danceability = 0.5,
        energy = 0.5,
        acousticness = 0.5,
        valence = 0.5,
        bpm = 100.0
    )
    session.add(track)
    session.commit()
    return track


# --- TESTES DE CRIAÇÃO (POST) ---

def test_create_track_success(client: TestClient, track_payload: dict):
    response = client.post("/tracks/", json=track_payload)
    
    assert response.status_code == 201
    data = response.json()
    assert data["playlist_id"] == track_payload["playlist_id"]
    assert data["spotify_track_id"] == track_payload["spotify_track_id"]
    assert "id" in data


def test_create_track_playlist_not_found(client: TestClient, track_payload: dict):
    # Altera para uma playlist inexistente para forçar o erro de integridade
    track_payload["playlist_id"] = str(uuid4())
    
    response = client.post("/tracks/", json=track_payload)
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Não é possível adicionar a música. Playlist não encontrada."


def test_create_track_invalid_limits(client: TestClient, track_payload: dict):
    """Garante que as regras do Pydantic bloqueiam limites incorretos de Audio Features."""
    track_payload["energy"] = 1.2  # Max é 1.0
     # Min é 0
    
    response = client.post("/tracks/", json=track_payload)
    assert response.status_code == 422


# --- TESTES DE LEITURA (GET) ---

def test_read_tracks_global_list(client: TestClient, db_track: Track):
    response = client.get("/tracks/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["spotify_track_id"] == db_track.spotify_track_id


def test_read_track_by_id_success(client: TestClient, db_track: Track):
    response = client.get(f"/tracks/{db_track.id}")
    assert response.status_code == 200
    assert response.json()["title"] == db_track.title


def test_read_track_by_id_not_found(client: TestClient):
    response = client.get(f"/tracks/{uuid4()}")
    assert response.status_code == 404


def test_read_tracks_by_playlist_success(client: TestClient, db_playlist: Playlist, db_track: Track):
    response = client.get(f"/tracks/playlist/{db_playlist.id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["playlist_id"] == str(db_playlist.id)


# --- TESTES DE ATUALIZAÇÃO (PUT) ---

def test_update_track_partial_success(client: TestClient, db_track: Track):
    update_payload = {
        "title": "New Updated Title",
    
    }
    
    response = client.put(f"/tracks/{db_track.id}", json=update_payload)
    assert response.status_code == 200
    
    data = response.json()
    assert data["title"] == "New Updated Title"

    # Garante que os campos omitidos preservaram o valor original
    assert data["artist"] == db_track.artist


# --- TESTES DE REMOÇÃO (DELETE) ---

def test_delete_track_success(client: TestClient, session: Session, db_track: Track):
    response = client.delete(f"/tracks/{db_track.id}")
    assert response.status_code == 204
    assert response.content == b""
    
    # Valida direto na sessão a ausência do registro
    stmt = select(Track).where(Track.id == db_track.id)
    db_check = session.scalars(stmt).first()
    assert db_check is None

def test_create_track_negative_duration(client: TestClient, track_payload: dict):
    """Garante que o Pydantic bloqueia durações de música negativas."""
    track_payload["duration_ms"] = -500
    
    response = client.post("/tracks/", json=track_payload)
    assert response.status_code == 422


def test_create_track_string_instead_of_float(client: TestClient, track_payload: dict):
    """Verifica se o FastAPI rejeita tipos de dados incorretos em campos de áudio."""
    track_payload["bpm"] = "ritmo_rapido"
    
    response = client.post("/tracks/", json=track_payload)
    assert response.status_code == 422

def test_delete_playlist_cascade_tracks(client: TestClient, session: Session, db_playlist: Playlist, db_track: Track):
    """Ao remover uma playlist, todas as músicas vinculadas a ela devem sumir do banco."""
    # 1. Deleta a playlist dona da música criada na fixture 'db_track'
    response = client.delete(f"/playlists/{db_playlist.id}")
    assert response.status_code == 204
    
    # 2. Verifica diretamente no banco se a música foi limpa automaticamente pelo CASCADE
    stmt = select(Track).where(Track.id == db_track.id)
    track_check = session.scalars(stmt).first()
    
    assert track_check is None

def test_read_tracks_invalid_pagination_parameters(client: TestClient):
    """Bloqueia o uso de parâmetros inválidos na paginação de músicas."""
    response = client.get("/tracks/?limit=invalido&skip=-5")
    assert response.status_code == 422

def test_update_track_required_field_with_none(client: TestClient, db_track: Track):
    """Impede que campos obrigatórios (como título) sejam atualizados para None."""
    update_payload = {
        "title": None
    }
    
    with pytest.raises(Exception) as exc_info:
        response = client.put(f"/tracks/{db_track.id}", json=update_payload)
        # Se chegar aqui sem exceção, verifica o status code
        assert response.status_code == 422
    
    # Verifica se a exceção está relacionada à validação do Pydantic
    assert "validation error" in str(exc_info.value).lower() or "none" in str(exc_info.value).lower()
    
def test_update_track_not_found(client: TestClient):
    """Garante erro 404 ao tentar atualizar uma música com UUID inexistente."""
    update_payload = {"title": "New Title"}
    response = client.put(f"/tracks/{uuid4()}", json=update_payload)
    
    assert response.status_code == 404