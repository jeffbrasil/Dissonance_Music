from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, MappedAsDataclass
from uuid import UUID, uuid4
from sqlalchemy import DateTime, func

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
