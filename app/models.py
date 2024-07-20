# app/models.py
from pydantic import BaseModel, HttpUrl, field_validator
from typing import Optional, Union

class UserUpdate(BaseModel):
    user_name: Optional[Union[str, None]] = None
    face_img_uri: Optional[Union[HttpUrl, str, None]] = None
    github_url: Optional[Union[HttpUrl, str, None]] = None
    x_url: Optional[Union[HttpUrl, str, None]] = None

    @field_validator("user_name", "face_img_uri", "github_url", "x_url")
    def empty_string_to_none(cls, v):
        return v if v != "" else None
