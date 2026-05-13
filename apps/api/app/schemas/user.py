"""User-facing DTOs."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict, EmailStr


class UserMe(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    display_name: str
    is_active: bool
    role_keys: list[str]
    permissions: list[str]
