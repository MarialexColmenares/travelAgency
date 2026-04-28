from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database.conexion import get_db
from modelos.models import Destino
from esquemas.schemas import CreateDestino, UpdateDestino

router = APIRouter(prefix="/destinos", tags=["Destinos"])

# --- GET: OBTENER TODOS LOS DESTINOS ---
@router.get("/")
def mostrar_destinos(session : Session = Depends(get_db) ):

    selescion = select(Destino)
    destinos = session.exec(selescion).all()

    return destinos

# --- GET: OBTENER UN DESTINO POR ID ---
@router.get("/destino{id_destino}")
def obtener_destino_id(id_destino: int, session: Session = Depends(get_db)):
    destino = session.get(Destino, id_destino)

    if not destino:

        raise HTTPException(status_code=404, detail="Transportes not found")

    return destino

# --- GET: OBTENER UN DESTINOS FILTRADOS POR CIUDAD Y PAIS --- 
@router.get("/filter")
def filter_movies(ciudad: str, pais: str, session: Session = Depends(get_db)):

    destino = session.exec(select(Destino).where(Destino.ciudad == ciudad, Destino.pais == pais)).all()
    return destino

# --- POST: CREAR UN NUEVO DESTINO ---
@router.post("/")
def crear_destino(
    data : CreateDestino,
    session : Session = Depends(get_db) ):
    nuevo_destino = Destino(
        **data.model_dump()
    )
    session.add(nuevo_destino)
    session.commit()
    session.refresh(nuevo_destino)

    return nuevo_destino

# --- POST BULK: CREAR MUCHOS NUEVOS DESTINOS ---
@router.post("/bulk")
def crear_destinos_masivo(
    lista_data: list[CreateDestino],
    session: Session = Depends(get_db)
):
   
    nuevos_destinos = [Destino(**destino.model_dump()) for destino in lista_data]
    

    session.add_all(nuevos_destinos)
    session.commit()

    for destino in nuevos_destinos:
        session.refresh(destino)

    return nuevos_destinos



# --- PATCH: ACTUALIZACIÓN PARCIAL ---
@router.patch("/{id_destino}")
def actualizar_destino_parcial(
    id_destino: int,
    data: UpdateDestino,
    session: Session = Depends(get_db)
):
    db_destino = session.get(Destino, id_destino)

    if not db_destino:
        raise HTTPException(status_code=404, detail="Destino no encontrado")

    datos_nuevos = data.model_dump(exclude_unset=True)


    for llave, valor in datos_nuevos.items():
        setattr(db_destino, llave, valor)

    session.add(db_destino)
    session.commit()
    session.refresh(db_destino)

    return db_destino

