from pydantic import BaseModel, Field
from typing import Optional
import uuid

class Task(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    description: str
    expected_output: str