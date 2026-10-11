"""Tables from docs/api-contracts.md §4.5. Nothing reads or writes them yet (V2)."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel, create_engine

from api.settings import DATABASE_URL

engine = create_engine(DATABASE_URL)


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    password_hash: str           # scrypt$<salt hex>$<hash hex>
    created_at: datetime = Field(default_factory=utcnow)


class Report(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    owner_id: int | None = Field(default=None, foreign_key="user.id")
    status: str
    input: dict = Field(sa_column=Column(JSON))
    engine: dict | None = Field(default=None, sa_column=Column(JSON))
    explanation: dict | None = Field(default=None, sa_column=Column(JSON))
    stages: list = Field(default_factory=list, sa_column=Column(JSON))  # StageEvent list, for replay
    created_at: datetime = Field(default_factory=utcnow)


class Village(SQLModel, table=True):
    code: str = Field(primary_key=True)  # LGD village code
    name: str
    block_code: str
    block_name: str
    district_code: str
    district_name: str
    households: int
    population: int
    literacy_rate: float
    workers: int
    is_rural: bool
    osm_counts: dict = Field(default_factory=dict, sa_column=Column(JSON))


def create_tables(bind=engine) -> None:
    SQLModel.metadata.create_all(bind)
