from pydantic import BaseModel, HttpUrl, field_validator
from typing import Optional

class UserUpdate(BaseModel):
    user_name: Optional[str] = None
    face_img_uri: Optional[str] = None
    github_url: Optional[str] = None
    x_url: Optional[str] = None

    @field_validator("user_name", "face_img_uri", "github_url", "x_url")
    def empty_string_to_none(cls, v):
        return v if v != "" else None
