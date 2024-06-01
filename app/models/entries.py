from pydantic import BaseModel


class EntryCreate(BaseModel):
    name: str
    description: str
    type: str
    path: str
    thumbnail_path: str
    project: bool

    # Permite que Pydantic convierta documentos MongoDB en objetos y viceversa
    class Config:
        from_attributes = True


class Entry(EntryCreate):
    id: str = None
