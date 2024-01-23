from typing import Annotated

from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
)


class Base(DeclarativeBase):
    pass


class Wallet(Base):
    __tablename__ = "stats"

    address: Mapped[Annotated[str, mapped_column(primary_key=True)]]
    proxy: Mapped[Annotated[int, mapped_column()]]
    rankUpdatedAt: Mapped[Annotated[int, mapped_column(nullable=True)]]
    rank: Mapped[Annotated[int, mapped_column(nullable=True)]]
    txsCount: Mapped[Annotated[int, mapped_column(nullable=True)]]
    volume: Mapped[Annotated[float, mapped_column(nullable=True)]]
    distinctMonths: Mapped[Annotated[int, mapped_column(nullable=True)]]
    networks: Mapped[Annotated[int, mapped_column(nullable=True)]]
    contracts: Mapped[Annotated[int, mapped_column(nullable=True)]]
    destChains: Mapped[Annotated[int, mapped_column(nullable=True)]]
