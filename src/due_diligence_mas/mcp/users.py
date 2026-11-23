from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class UserRole(Enum):
    TECH = "tech"
    COMMERCIAL = "commercial"


class User(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str = Field(description="Name of the user")
    role: UserRole = Field(description="Role of the user that identifies his knowledge")


def get_mock_users() -> list[User]:
    # fixed ids: tasks reference them, so they must be stable across calls
    return [
        User(id=UUID("cd9a5f5e-e0c3-45d0-98a0-026b1e3cf619"), name="Daniel", role=UserRole.TECH),
        User(id=UUID("7b0e3c1a-5d42-4f6e-9a18-3c2f8d6b4e57"), name="Luis", role=UserRole.COMMERCIAL),
    ]
