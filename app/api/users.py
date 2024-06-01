from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from database import get_mongo_database
from datetime import timedelta
from fastapi import HTTPException, status
import os

from models.tokens import Token
from models.users import User, UserCreate
from models.responses import Message
from services.auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    get_current_active_user,
)


router = APIRouter()

db = get_mongo_database()

ACCESS_TOKEN_EXPIRE_MINUTES = float(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """Autentica usuario y devuelve un token de acceso"""
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nombre de usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return Token(access_token=access_token, token_type="Bearer")


@router.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: User = Depends(get_current_user),
):
    """Devuelve al usuario actual si está logeado"""
    return current_user


@router.post(
    "/users/", response_model=User, responses={404: {"model": Message}}
)
async def create_user(user: UserCreate):
    """Crea un usuario nuevo"""
    if user is None:
        return JSONResponse(
            status_code=404,
            content={"message": "No se ha podido crear el usuario"},
        )
    return create_user(user)


@router.get(
    "/admin/",
    dependencies=[Depends(get_current_active_user)],
    responses={401: {"model": Message}},
)
async def verify_session():
    return JSONResponse(
        status_code=200,
        content={"message": "Autorización correcta para llamada admin"},
    )
