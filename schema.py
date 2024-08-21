from pydantic import BaseModel, field_validator
from typing import Optional
from forbidden_words import FORBIDDEN_WORDS


class BasePost(BaseModel):
    title: str
    description: str
    author: str

    @field_validator('description')
    @classmethod
    def check_description(cls, value):
        set_of_words = set(value.split())
        if FORBIDDEN_WORDS & set_of_words:
            raise ValueError("Your description contain forbidden words! Please, don't use dirty words!")
        else:
            return value


class PostCreate(BasePost):
    pass


class PostUpdate(BasePost):
    title: Optional[str] = None
    description: Optional[str] = None
    author: Optional[str] = None
