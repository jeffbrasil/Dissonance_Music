from typing import Generator
from os import getenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# 1. Recupera a URL do banco de dados (usa o SQLite local como padrão)
DATABASE_URL = getenv("DATABASE_URL", "sqlite:///local.db")

# 2. Cria o Engine de conexão
# O argumento 'connect_args' é necessário apenas para o SQLite garantir compatibilidade multithreading
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

# 3. Cria a fábrica de sessões (SessionLocal)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Função geradora (Dependency Injection) para fornecer sessões do banco de dados.
    Garante que a sessão seja fechada corretamente após o término da requisição.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()