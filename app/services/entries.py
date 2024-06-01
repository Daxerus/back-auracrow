from typing import List, Optional
from bson import ObjectId
from pymongo.collection import Collection
from pymongo.database import Database
from models.entries import Entry, EntryCreate


# CRUD
class EntryService:
    def __init__(self, db: Database):
        """Llamada auto al crear una instancia de la clase

        Inicializa la conexión a la base de datos,
        almacena la referencia a la colección de entradas
        """
        self.entries_collection: Collection = db.entries

    #
    def get_entries(self) -> List[Entry]:
        """Obtener todas las entradas"""
        entries = self.entries_collection.find({})
        return [Entry(**entry, id=str(entry.get("_id"))) for entry in entries]

    def get_entries_by_type(self, entry_type: str) -> List[Entry]:
        """Obtener todas las entradas de una sección"""
        entries = self.entries_collection.find({"type": entry_type})
        return [Entry(**entry, id=str(entry.get("_id"))) for entry in entries]

    def get_entry(self, entry_id: str) -> Optional[Entry]:
        """Obtener una entrada específica"""
        try:
            entry_id_object = ObjectId(entry_id)
            entry = self.entries_collection.find_one({"_id": entry_id_object})
            return Entry(**entry, id=str(entry.get("_id"))) if entry else None
        except Exception:
            return None

    def create_entry(self, entry: EntryCreate) -> Entry:
        """Crear una nueva entrada"""
        entry_dict = entry.dict()
        inserted = self.entries_collection.insert_one(entry_dict)
        return Entry(**entry_dict, id=str(inserted.inserted_id))

    def update_entry(
        self, entry_id: str, entry: EntryCreate
    ) -> Optional[EntryCreate]:
        """Actualizar una entrada existente"""
        try:
            entry_dict = entry.dict()
            entry_id_object = ObjectId(entry_id)
            updated = self.entries_collection.replace_one(
                {"_id": entry_id_object}, entry_dict
            )
            return (
                Entry(**entry_dict, id=entry_id)
                if updated.modified_count > 0
                else None
            )
        except Exception:
            return None

    def delete_entry(self, entry_id: str) -> bool:
        """Eliminar una entrada existente"""
        try:
            entry_id_object = ObjectId(entry_id)
            deleted = self.entries_collection.delete_one(
                {"_id": entry_id_object}
            )
            return True if deleted.deleted_count > 0 else False
        except Exception:
            return False
