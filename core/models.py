from typing import Annotated
from datetime import date
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
    wallet_name: Mapped[Annotated[str, mapped_column(nullable=True)]]
    last_update: Mapped[Annotated[int, mapped_column(nullable=True)]]
    rank: Mapped[Annotated[int, mapped_column(nullable=True)]]
    count_txn: Mapped[Annotated[int, mapped_column(nullable=True)]]
    volume: Mapped[Annotated[float, mapped_column(nullable=True)]]
    distinct_months: Mapped[Annotated[int, mapped_column(nullable=True)]]
    src_chains_count: Mapped[Annotated[int, mapped_column(nullable=True)]]
    contracts: Mapped[Annotated[int, mapped_column(nullable=True)]]
    dst_chains_count: Mapped[Annotated[int, mapped_column(nullable=True)]]
    dst_chains_list: Mapped[Annotated[str, mapped_column(nullable=True)]]
    src_chains_list: Mapped[Annotated[str, mapped_column(nullable=True)]]
    last_activity: Mapped[Annotated[date, mapped_column(nullable=True)]]
    is_mainnet: Mapped[Annotated[bool, mapped_column(nullable=True)]]
