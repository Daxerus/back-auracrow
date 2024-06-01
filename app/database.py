from pymongo import MongoClient
from pymongo.database import Database
from dotenv import load_dotenv
import os

load_dotenv()


def get_mongo_database() -> Database:
    """Instanciar el cliente de MongoDB"""
    return MongoClient(os.getenv("MONGODB_URL")).get_database()
