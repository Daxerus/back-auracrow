from pydantic import BaseModel


class User(BaseModel):
    username: str
    name: str
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str


class UserCreate(User):
    password: str
