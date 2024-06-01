from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pymongo.database import Database
from passlib.context import CryptContext

from models.users import UserInDB, UserCreate
from models.tokens import TokenData
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from dotenv import load_dotenv
from models.users import User
from services.users import UsersService
from database import get_mongo_database


import os

load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    """Compara la contraseña introducida con la hasheada almacenada"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(self, password):
    """Encripta la contraseña"""
    return pwd_context.hash(password)


def authenticate_user(username: str, password: str):
    """Comprueba si la contraseña introducida
    concuerda con la de ese usuario"""
    db = get_mongo_database()
    user = UsersService(db).get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Crea un token de acceso temporal"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, os.getenv("SECRET_KEY"), algorithm=os.getenv("ALGORITHM")
    )
    return encoded_jwt


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Database = Depends(get_mongo_database),
):
    """Devuelve los datos del usuario logeado actualmente"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar los credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            os.getenv("SECRET_KEY"),
            algorithms=os.getenv("ALGORITHM"),
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    users_service = UsersService(db)
    user_data = users_service.get_user(username=token_data.username)
    if user_data is None:
        raise credentials_exception
    return user_data


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def create_user(
    user: UserCreate, db: Database = Depends(get_mongo_database)
) -> UserInDB:
    """Crea un usuario nuevo"""
    user_data = user.dict()
    hashed_password = get_password_hash(user_data["password"])
    user_data["hashed_password"] = hashed_password
    del user_data["password"]
    db.users_collection.insert_one(user_data)
    user_in_db = db.find_one({"username": user_data["username"]})
    return UserInDB(**user_in_db)
