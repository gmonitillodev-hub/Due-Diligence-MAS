from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Priority(Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class Task(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    assignee: UUID
    description: str
    priority: Priority
