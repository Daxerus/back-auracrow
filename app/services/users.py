from pymongo.collection import Collection
from pymongo.database import Database
from models.users import UserInDB


# CRUD
class UsersService:
    def __init__(self, db: Database):
        """Llamada auto al crear una instancia de la clase

        Inicializa la conexión a la base de datos,
        almacena la referencia a la colección de entradas
        """
        self.users_collection: Collection = db.users

    def get_user(self, username: str):
        """Busca al usuario introducido en la base de datos"""
        user_data = self.users_collection.find_one(
            {"username": username},
            {"_id": 0, "username": 1, "hashed_password": 1, "name": 1},
        )
        if user_data:
            return UserInDB(**user_data)
        return None
