from fastapi import FastAPI
from conexion import create_db_and_tables
from routers.clientes_router import router as client_router
from routers.reservas_router import router as reservas_router
from routers.paquetes_router import router as paquetes_router
from routers.guias_router import router as guias_router
from routers.transportes_router import router as transportes_router
from routers.hoteles_router import router as hoteles_router
from routers.destinos_router import router as destinos_router
from routers.pagos_router import router as pagos_router

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/")
def inicio():
    return {"message":"Agencia de viajes"}

app.include_router(client_router)
app.include_router(reservas_router)
app.include_router(paquetes_router)
app.include_router(guias_router)
app.include_router(transportes_router)
app.include_router(hoteles_router)
app.include_router(destinos_router)
app.include_router(pagos_router)