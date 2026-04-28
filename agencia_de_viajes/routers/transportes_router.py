from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from modelos.models import Transporte
from database.conexion import get_db
from esquemas.schemas import TransporteCreate, TransporteUpdate

router = APIRouter(prefix="/transportes", tags=["Transporte"])

# --- GET: OBTENER TODOS LOS TRANSPORTES ---
@router.get("/")
def mostrar_tansportes(session: Session = Depends(get_db)):

    statement = select(Transporte)
    transporte = session.exec(statement).all()

    return transporte

# --- GET: OBTENER UN TRANSPORTE POR SU ID ---
@router.get("/transporte{id_transporte}")
def obtener_transporte_id(id_transporte: int, session: Session = Depends(get_db)):
    transporte = session.get(Transporte, id_transporte)

    if not transporte:

        raise HTTPException(status_code=404, detail="Transportes not found")

    return transporte

# --- POST: CREAR NUEVO TRANSPORTE---
@router.post("")
def crear_transporte(
    tansporte_data: TransporteCreate,
    session: Session = Depends(get_db)
):
    nuevo_Transporte = Transporte(
        tipo = tansporte_data.tipo,
        empresa = tansporte_data.empresa,
        capacidad = tansporte_data.capacidad,
        estado = tansporte_data.estado
    )
    session.add(nuevo_Transporte)
    session.commit()
    session.refresh(nuevo_Transporte)

    return nuevo_Transporte


@router.post("/bulk")
def crear_transportes(
    transportes_data: list[TransporteCreate],
    session: Session = Depends(get_db)
):
    nuevos_transportes = [Transporte(**transporte.model_dump()) for transporte in transportes_data]
    session.add_all(nuevos_transportes)
    session.commit()

    for transporte in nuevos_transportes:
        session.refresh(transporte)

    return nuevos_transportes


# --- PATCH ACTUALIZACION PARCIAL ---

@router.patch("actualizar")
def actualizacion_parcial(
    data : TransporteUpdate,
    transporte_id : int,
    session: Session = Depends(get_db)
):
    db_transporte = session.get(Transporte, transporte_id)
    if not db_transporte:
        raise HTTPException(status_code=404, detail="Transporte no encontrado")

    # model_dump(exclude_unset=True) para: evita sobreescribir con valores nulos
    datos_actualizar = data.model_dump(exclude_unset=True)

    for llave, valor in datos_actualizar.items():
        setattr(db_transporte, llave, valor)

    session.add(db_transporte)
    session.commit()
    session.refresh(db_transporte)
    return db_transporte