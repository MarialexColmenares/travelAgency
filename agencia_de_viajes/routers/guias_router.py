from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database.conexion import get_db
from esquemas.schemas import GuiaCreate, GuiaUpdate
from modelos.models import Guia

router = APIRouter(prefix="/guias", tags=["Guias"])

# --- GET: OBTENER TODOS LOS GUIAS ---
@router.get("")
def mostrar_guias(
    session: Session = Depends(get_db)):

    statement = select(Guia)
    guias = session.exec(statement).all()

    return guias

# --- GET: OBTENER UN GUIA POR ID ---
@router.get("/guia{id_guia}")
def obtener_guia_id(id_guia: int, session: Session = Depends(get_db)):
    guia = session.get(Guia, id_guia)

    if not guia:

        raise HTTPException(status_code=404, detail="guia not found")

    return guia

# --- POST: CREAR UN NUEVO GUIA ---
@router.post("")
def crear_guia(
    data: GuiaCreate,
    session: Session = Depends(get_db)
):
    nuevo_guia = Guia(
        **data.model_dump()
    )

    session.add(nuevo_guia)
    session.commit()
    session.refresh(nuevo_guia)

    return nuevo_guia

# --- POST BULK: CREAR MUCHOS NUEVO GUIAS ---
@router.post("/bulk")
def crear_guias_masivo(
    lista_data: list[GuiaCreate],
    session: Session = Depends(get_db)
):
    
    nuevos_guias = [Guia(**guia.model_dump()) for guia in lista_data]
    
    session.add_all(nuevos_guias)
    session.commit()
    
    for guia in nuevos_guias:
        session.refresh(guia)

    return nuevos_guias



# --- PATCH: ACTUALIZACIÓN PARCIAL ---
@router.patch("/{id_guia}")
def actualizar_guia_parcial(
    id_guia: int,
    data: GuiaUpdate,
    session: Session = Depends(get_db)
):
    db_guia = session.get(Guia, id_guia)

    if not db_guia:
        raise HTTPException(status_code=404, detail="Guia no encontrado")

    datos_nuevos = data.model_dump(exclude_unset=True)

    for llave, valor in datos_nuevos.items():
        setattr(db_guia, llave, valor)

    session.add(db_guia)
    session.commit()
    session.refresh(db_guia)

    return db_guia


