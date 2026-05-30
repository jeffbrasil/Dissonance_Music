import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.base_class import Base
from app.db.session import get_db
from app.models.user import User  # Garante o registro do modelo

@pytest.fixture(scope="session")
def engine():
    # Usamos o StaticPool para que todas as conexões compartilhem o mesmo banco em memória
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()

@pytest.fixture
def session(engine):
    """Cria uma nova sessão para cada teste, garantindo isolamento via rollback."""
    connection = engine.connect()
    # Inicia uma transação no banco de dados
    transaction = connection.begin()
    
    # Vincula a sessão à conexão ativa
    session = Session(bind=connection)

    yield session

    # Finaliza a sessão e desfaz qualquer alteração (Rollback) para o próximo teste
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(session):
    """Injeta a sessão ativa e segura o ciclo de vida durante a requisição."""
    def _get_db_override():
        try:
            yield session
        finally:
            pass  # Não fecha a sessão aqui, deixa o controle com a fixture 'session'

    app.dependency_overrides[get_db] = _get_db_override
    
    with TestClient(app) as client:
        yield client
        
    app.dependency_overrides.clear()