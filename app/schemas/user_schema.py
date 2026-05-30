from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from datetime import datetime


class UserBase(BaseModel):
    """Schema base com os campos comuns para compartilhamento."""
    spotify_id: str = Field(..., description="ID único do usuário retornado pelo Spotify")
    email: EmailStr | None = Field(default=None, description="E-mail do usuário")
    display_name: str | None = Field(default=None, description="Nome de exibição do usuário")


class UserCreate(UserBase):
    """Schema para validação dos dados recebidos na criação de um usuário (Request)."""
    # Como todos os campos obrigatórios já estão na base, este bloco pode ficar vazio por enquanto.
    pass


class UserUpdate(BaseModel):
    """Schema para atualização parcial dos dados do usuário (Request)."""
    # Nenhum campo é obrigatório no PUT/PATCH, permitindo atualização parcial
    email: EmailStr | None = None
    display_name: str | None = None


class UserResponse(UserBase):
    """Schema para formatação dos dados retornados pela API (Response)."""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        # Permite que o Pydantic leia os dados diretamente do modelo SQLAlchemy/Dataclass
        from_attributes = True