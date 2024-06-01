from fastapi import FastAPI
from api import entries, users
from fastapi.middleware.cors import CORSMiddleware


# Instancia de la aplicación FastAPI
app = FastAPI()

# Registra los endpoints de la API
app.include_router(entries.router)
app.include_router(users.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir solicitudes desde cualquier origen
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos HTTP
    allow_headers=["*"],  # Permitir todos los encabezados
)

# Punto de entrada para ejecutar la apicación
if __name__ == "__main__":
    import uvicorn

    # Ejecuta el servidor usando Uvicorn
    uvicorn.run(app, host="localhost", port=8000)
