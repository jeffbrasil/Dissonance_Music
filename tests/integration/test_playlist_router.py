import pytest
from uuid import uuid4
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.playlist import Playlist
from app.models.track import Track


class TestCreateTrack:
    """Testes para POST /tracks/"""
    
    def test_create_track_success(self, client: TestClient, db_session: Session, sample_playlist: Playlist):
        """Deve criar uma música com sucesso quando a playlist existe"""
        track_data = {
            "playlist_id": str(sample_playlist.id),
            "spotify_track_id": "spotify:track:4uLU6hMCjMI75M1A2tKUQC",
            "title": "Bohemian Rhapsody",
            "artist": "Queen",
            "duration_ms": 354000,
            "album": "A Night at the Opera",
            "danceability": 0.35,
            "energy": 0.80,
            "acousticness": 0.20,
            "valence": 0.40,
            "bpm": 143.0,
            "dissonance_score": 0.75
        }
        
        response = client.post("/tracks/", json=track_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == track_data["title"]
        assert data["artist"] == track_data["artist"]
        assert data["spotify_track_id"] == track_data["spotify_track_id"]
        assert data["duration_ms"] == track_data["duration_ms"]
        assert data["album"] == track_data["album"]
        assert data["danceability"] == track_data["danceability"]
        assert data["energy"] == track_data["energy"]
        assert data["acousticness"] == track_data["acousticness"]
        assert data["valence"] == track_data["valence"]
        assert data["bpm"] == track_data["bpm"]
        assert data["dissonance_score"] == track_data["dissonance_score"]
        assert "id" in data
        
        # Verificar no banco
        track = db_session.get(Track, data["id"])
        assert track is not None
        assert track.title == track_data["title"]
        assert track.playlist_id == sample_playlist.id
    
    def test_create_track_without_optional_fields(self, client: TestClient, sample_playlist: Playlist):
        """Deve criar uma música mesmo sem campos opcionais (album e dissonance_score)"""
        track_data = {
            "playlist_id": str(sample_playlist.id),
            "spotify_track_id": "spotify:track:1Z6HxRZAEqEPYwhG72tl6A",
            "title": "Imagine",
            "artist": "John Lennon",
            "duration_ms": 183000,
            "danceability": 0.55,
            "energy": 0.45,
            "acousticness": 0.90,
            "valence": 0.75,
            "bpm": 75.0
            # album e dissonance_score são opcionais
        }
        
        response = client.post("/tracks/", json=track_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["album"] is None
        assert data["dissonance_score"] is None
    
    def test_create_track_playlist_not_found(self, client: TestClient):
        """Deve retornar 404 quando a playlist não existe"""
        non_existent_playlist_id = uuid4()
        track_data = {
            "playlist_id": str(non_existent_playlist_id),
            "spotify_track_id": "spotify:track:test123",
            "title": "Test Track",
            "artist": "Test Artist",
            "duration_ms": 180000,
            "danceability": 0.5,
            "energy": 0.5,
            "acousticness": 0.5,
            "valence": 0.5,
            "bpm": 120.0
        }
        
        response = client.post("/tracks/", json=track_data)
        
        assert response.status_code == 404
        assert "Playlist não encontrada" in response.json()["detail"]
    
    def test_create_track_duplicate_spotify_id(self, client: TestClient, sample_playlist: Playlist, sample_track: Track):
        """Deve retornar erro ao tentar criar música com spotify_track_id duplicado"""
        track_data = {
            "playlist_id": str(sample_playlist.id),
            "spotify_track_id": sample_track.spotify_track_id,  # ID já existente
            "title": "Different Title",
            "artist": "Different Artist",
            "duration_ms": 200000,
            "danceability": 0.5,
            "energy": 0.5,
            "acousticness": 0.5,
            "valence": 0.5,
            "bpm": 120.0
        }
        
        response = client.post("/tracks/", json=track_data)
        
        # Deve retornar 400 ou 409 (dependendo da implementação)
        assert response.status_code in [400, 409, 422]
    
    def test_create_track_missing_required_fields(self, client: TestClient, sample_playlist: Playlist):
        """Deve retornar 422 quando campos obrigatórios estão faltando"""
        track_data = {
            "playlist_id": str(sample_playlist.id),
            "title": "Incomplete Track"
            # Faltando spotify_track_id, artist, duration_ms, danceability, energy, acousticness, valence, bpm
        }
        
        response = client.post("/tracks/", json=track_data)
        assert response.status_code == 422
    
    def test_create_track_invalid_audio_features_range(self, client: TestClient, sample_playlist: Playlist):
        """Deve retornar 422 quando audio features estão fora do intervalo [0,1]"""
        track_data = {
            "playlist_id": str(sample_playlist.id),
            "spotify_track_id": "spotify:track:test123",
            "title": "Test Track",
            "artist": "Test Artist",
            "duration_ms": 180000,
            "danceability": 1.5,  # Fora do intervalo
            "energy": -0.2,        # Fora do intervalo
            "acousticness": 0.5,
            "valence": 0.5,
            "bpm": 120.0
        }
        
        response = client.post("/tracks/", json=track_data)
        assert response.status_code == 422


class TestReadTracks:
    """Testes para GET /tracks/"""
    
    def test_read_tracks_empty(self, client: TestClient):
        """Deve retornar lista vazia quando não há músicas"""
        response = client.get("/tracks/")
        
        assert response.status_code == 200
        assert response.json() == []
    
    def test_read_tracks_with_pagination(self, client: TestClient, db_session: Session, sample_playlist: Playlist, sample_tracks: list[Track]):
        """Deve retornar músicas paginadas corretamente"""
        # Verificar primeira página (skip=0, limit=2)
        response = client.get("/tracks/?skip=0&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        
        # Verificar segunda página (skip=2, limit=2)
        response = client.get("/tracks/?skip=2&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == min(2, len(sample_tracks) - 2)
    
    def test_read_tracks_default_pagination(self, client: TestClient, db_session: Session, sample_playlist: Playlist, sample_tracks: list[Track]):
        """Deve usar valores padrão de paginação (skip=0, limit=100)"""
        response = client.get("/tracks/")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == len(sample_tracks)
    
    def test_read_tracks_returns_all_fields(self, client: TestClient, sample_track: Track):
        """Deve retornar todos os campos da música corretamente"""
        response = client.get("/tracks/")
        
        assert response.status_code == 200
        data = response.json()[0]
        
        expected_fields = [
            "id", "playlist_id", "spotify_track_id", "title", "artist",
            "duration_ms", "album", "danceability", "energy", "acousticness",
            "valence", "bpm", "dissonance_score"
        ]
        
        for field in expected_fields:
            assert field in data


class TestReadTrackById:
    """Testes para GET /tracks/{track_id}"""
    
    def test_read_track_by_id_success(self, client: TestClient, sample_track: Track):
        """Deve retornar uma música específica pelo ID"""
        response = client.get(f"/tracks/{sample_track.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(sample_track.id)
        assert data["title"] == sample_track.title
        assert data["artist"] == sample_track.artist
        assert data["spotify_track_id"] == sample_track.spotify_track_id
        assert data["duration_ms"] == sample_track.duration_ms
        assert data["danceability"] == sample_track.danceability
        assert data["energy"] == sample_track.energy
    
    def test_read_track_by_id_not_found(self, client: TestClient):
        """Deve retornar 404 quando o ID não existe"""
        non_existent_id = uuid4()
        response = client.get(f"/tracks/{non_existent_id}")
        
        assert response.status_code == 404
        assert "Música não encontrada" in response.json()["detail"]
    
    def test_read_track_by_id_invalid_uuid(self, client: TestClient):
        """Deve retornar 422 quando o UUID é inválido"""
        response = client.get("/tracks/invalid-uuid-format")
        assert response.status_code == 422


class TestReadTracksByPlaylist:
    """Testes para GET /tracks/playlist/{playlist_id}"""
    
    def test_read_tracks_by_playlist_success(self, client: TestClient, db_session: Session, sample_playlist: Playlist, sample_tracks: list[Track]):
        """Deve retornar todas as músicas de uma playlist específica"""
        response = client.get(f"/tracks/playlist/{sample_playlist.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == len(sample_tracks)
        for track in data:
            assert track["playlist_id"] == str(sample_playlist.id)
    
    def test_read_tracks_by_playlist_empty(self, client: TestClient, empty_playlist: Playlist):
        """Deve retornar lista vazia quando a playlist não tem músicas"""
        response = client.get(f"/tracks/playlist/{empty_playlist.id}")
        
        assert response.status_code == 200
        assert response.json() == []
    
    def test_read_tracks_by_playlist_not_found(self, client: TestClient):
        """Deve retornar lista vazia mesmo quando a playlist não existe"""
        non_existent_id = uuid4()
        response = client.get(f"/tracks/playlist/{non_existent_id}")
        
        assert response.status_code == 200
        assert response.json() == []
    
    def test_read_tracks_by_playlist_with_cascade_delete(self, client: TestClient, db_session: Session, sample_playlist: Playlist, sample_tracks: list[Track]):
        """Verifica que as músicas são deletadas em cascata quando a playlist é deletada"""
        # Deletar a playlist
        db_session.delete(sample_playlist)
        db_session.commit()
        
        # Tentar buscar músicas da playlist deletada
        response = client.get(f"/tracks/playlist/{sample_playlist.id}")
        
        assert response.status_code == 200
        assert response.json() == []
        
        # Verificar que as músicas não existem mais no banco
        for track in sample_tracks:
            assert db_session.get(Track, track.id) is None


class TestUpdateTrack:
    """Testes para PUT /tracks/{track_id}"""
    
    def test_update_track_success(self, client: TestClient, sample_track: Track):
        """Deve atualizar os metadados de uma música com sucesso"""
        update_data = {
            "title": "Updated Track Title",
            "artist": "Updated Artist",
            "duration_ms": 300000,
            "danceability": 0.95,
            "energy": 0.15,
            "dissonance_score": 0.50
        }
        
        response = client.put(f"/tracks/{sample_track.id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(sample_track.id)
        assert data["title"] == update_data["title"]
        assert data["artist"] == update_data["artist"]
        assert data["duration_ms"] == update_data["duration_ms"]
        assert data["danceability"] == update_data["danceability"]
        assert data["energy"] == update_data["energy"]
        assert data["dissonance_score"] == update_data["dissonance_score"]
        # Campos não enviados devem permanecer os originais
        assert data["spotify_track_id"] == sample_track.spotify_track_id
        assert data["album"] == sample_track.album
    
    def test_update_track_partial_update(self, client: TestClient, sample_track: Track):
        """Deve atualizar apenas os campos enviados"""
        update_data = {"title": "Only Title Updated"}
        
        response = client.put(f"/tracks/{sample_track.id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["artist"] == sample_track.artist
        assert data["duration_ms"] == sample_track.duration_ms
        assert data["danceability"] == sample_track.danceability
    
    def test_update_track_update_spotify_id(self, client: TestClient, sample_track: Track):
        """Deve permitir atualizar o spotify_track_id"""
        new_spotify_id = "spotify:track:newtrack123"
        update_data = {"spotify_track_id": new_spotify_id}
        
        response = client.put(f"/tracks/{sample_track.id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["spotify_track_id"] == new_spotify_id
    
    def test_update_track_not_found(self, client: TestClient):
        """Deve retornar 404 quando a música não existe"""
        non_existent_id = uuid4()
        update_data = {"title": "New Title"}
        
        response = client.put(f"/tracks/{non_existent_id}", json=update_data)
        
        assert response.status_code == 404
        assert "Música não encontrada" in response.json()["detail"]
    
    def test_update_track_invalid_audio_features(self, client: TestClient, sample_track: Track):
        """Deve retornar 422 quando audio features estão fora do intervalo [0,1]"""
        update_data = {
            "danceability": 1.8,
            "acousticness": -0.5
        }
        
        response = client.put(f"/tracks/{sample_track.id}", json=update_data)
        assert response.status_code == 422
    
    def test_update_track_invalid_uuid(self, client: TestClient):
        """Deve retornar 422 quando o UUID é inválido"""
        response = client.put("/tracks/invalid-uuid", json={"title": "New Title"})
        assert response.status_code == 422


class TestDeleteTrack:
    """Testes para DELETE /tracks/{track_id}"""
    
    def test_delete_track_success(self, client: TestClient, db_session: Session, sample_track: Track):
        """Deve deletar uma música com sucesso"""
        track_id = sample_track.id
        
        response = client.delete(f"/tracks/{track_id}")
        
        assert response.status_code == 204
        assert response.content == b""
        
        # Verificar que foi deletado do banco
        track = db_session.get(Track, track_id)
        assert track is None
    
    def test_delete_track_not_found(self, client: TestClient):
        """Deve retornar 404 quando a música não existe"""
        non_existent_id = uuid4()
        response = client.delete(f"/tracks/{non_existent_id}")
        
        assert response.status_code == 404
        assert "Música não encontrada" in response.json()["detail"]
    
    def test_delete_track_invalid_uuid(self, client: TestClient):
        """Deve retornar 422 quando o UUID é inválido"""
        response = client.delete("/tracks/invalid-uuid")
        assert response.status_code == 422
    
    def test_delete_already_deleted_track(self, client: TestClient, sample_track: Track):
        """Deve retornar 404 ao tentar deletar uma música já deletada"""
        # Primeira deleção
        response = client.delete(f"/tracks/{sample_track.id}")
        assert response.status_code == 204
        
        # Segunda deleção (música não existe mais)
        response = client.delete(f"/tracks/{sample_track.id}")
        assert response.status_code == 404
    
    def test_delete_track_does_not_affect_other_tracks(self, client: TestClient, db_session: Session, sample_playlist: Playlist, sample_tracks: list[Track]):
        """Deletar uma música não deve afetar outras músicas da mesma playlist"""
        track_to_delete = sample_tracks[0]
        remaining_tracks = sample_tracks[1:]
        
        response = client.delete(f"/tracks/{track_to_delete.id}")
        assert response.status_code == 204
        
        # Verificar que as outras músicas continuam existindo
        for track in remaining_tracks:
            assert db_session.get(Track, track.id) is not None
        
        # Verificar que a playlist ainda existe
        assert db_session.get(Playlist, sample_playlist.id) is not None


# Fixtures adicionais necessárias
@pytest.fixture
def empty_playlist(db_session, sample_user):
    """Cria uma playlist vazia para testes"""
    playlist = Playlist(
        id=uuid4(),
        user_id=sample_user.id,
        alpha=0.5,
        weight_energy=0.4,
        weight_acousticness=0.3,
        weight_popularity=0.2,
        weight_valence=0.1,
        track_count=0,
        status="pending"
    )
    db_session.add(playlist)
    db_session.commit()
    db_session.refresh(playlist)
    return playlist