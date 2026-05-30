from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, MappedAsDataclass
from uuid import UUID, uuid4
from sqlalchemy import DateTime, func, MetaData


convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

class Base(MappedAsDataclass, DeclarativeBase):

    """
    Classe base declarativa para todos os models SQLAlchemy.
    Define campos comuns: id, created_at e updated_at.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        init = False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),  # atualiza automaticamente em qualquer UPDATE
        nullable=False,
        init=False,
    )
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4, init = False)
