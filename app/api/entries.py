from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from typing import List, Union
from models.entries import Entry, EntryCreate
from models.responses import Message
from models.users import UserInDB
from services.entries import EntryService
from database import get_mongo_database
from pymongo.database import Database
from services.auth import get_current_user, get_current_active_user

router = APIRouter()


@router.get(
    "/entries/",
    response_model=Union[List[Entry], str],
    responses={404: {"model": Message}},
)
async def read_entries(db: Database = Depends(get_mongo_database)):
    """Obtener todas las entradas"""
    entry_service = EntryService(db)
    entries = entry_service.get_entries()
    if not entries:
        return JSONResponse(
            status_code=404,
            content={"message": "No hay publicaciones que mostrar"},
        )
    else:
        return entries


@router.get(
    "/entries/type/{entry_type}",
    response_model=Union[List[Entry], str],
    responses={404: {"model": Message}},
)
async def read_entries_by_tag(
    entry_type: str, db: Database = Depends(get_mongo_database)
):
    """Obtener todas las entradas de una sección"""
    entry_service = EntryService(db)
    entries = entry_service.get_entries_by_type(entry_type)
    if not entries:
        return JSONResponse(
            status_code=404,
            content={"message": "No hay publicaciones que mostrar"},
        )
    else:
        return entries


@router.get(
    "/entries/{entry_id}",
    response_model=Entry,
    responses={404: {"model": Message}},
)
async def read_entry(entry_id: str, db: Database = Depends(get_mongo_database)):
    """Obtener una entrada por su ID"""
    entry_service = EntryService(db)
    entry = entry_service.get_entry(entry_id)
    if entry is None:
        return JSONResponse(
            status_code=404, content={"message": "Publicación no encontrada"}
        )
    return entry


@router.post(
    "/entries/",
    dependencies=[Depends(get_current_active_user)],
    response_model=Entry,
    responses={404: {"model": Message}},
)
async def create_entry(
    entry: EntryCreate, db: Database = Depends(get_mongo_database)
):
    """Crear una nueva entrada"""
    entry_service = EntryService(db)
    if entry is None:
        return JSONResponse(
            status_code=404,
            content={"message": "No se ha podido crear la publicación"},
        )
    return entry_service.create_entry(entry)


@router.put(
    "/entries/{entry_id}",
    dependencies=[Depends(get_current_active_user)],
    response_model=Entry,
    responses={404: {"model": Message}},
)
async def update_entry(
    entry_id: str,
    entry: EntryCreate,
    db: Database = Depends(get_mongo_database),
):
    """Actualizar una entrada existente"""
    entry_service = EntryService(db)
    updated_entry = entry_service.update_entry(entry_id, entry)
    if updated_entry is None:
        return JSONResponse(
            status_code=404, content={"message": "Publicación no encontrada"}
        )
    return updated_entry


@router.delete(
    "/entries/{entry_id}",
    dependencies=[Depends(get_current_active_user)],
    responses={404: {"model": Message}, 200: {"model": Message}},
)
async def delete_entry(
    entry_id: str,
    db: Database = Depends(get_mongo_database),
    current_user: UserInDB = Depends(get_current_user),
):
    """Eliminar una entrada"""
    entry_service = EntryService(db)
    if entry_service.delete_entry(entry_id) is False:
        return JSONResponse(
            status_code=404, content={"message": "Publicación no encontrada"}
        )
    else:
        return JSONResponse(
            status_code=200,
            content={"message": "Publicación eliminada con éxito"},
        )
