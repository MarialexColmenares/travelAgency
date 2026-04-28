from models import Pago
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from conexion import get_db
from schemas import PagoCreate, PagoUpdate

router = APIRouter(prefix="/pagos",tags=["Pagos"])

# --- GET: OBTENER TODOS LOS PAGOS ---
@router.get("/")
def mostrar_pago(session : Session = Depends(get_db) ):

    statement = select(Pago)
    pago = session.exec(statement).all()

    return pago

# --- GET: OBTENER UN PAGO POR SU ID ---
@router.get("/pago{id_pago}")
def obtener_transporte_id(id_pago: int, session: Session = Depends(get_db)):
    pago = session.get(Pago, id_pago)

    if not pago:

        raise HTTPException(status_code=404, detail="Pago not found")

    return pago

# --- POST: CREAR UN VUEVO PAGO---
@router.post("/")
def crear_pago (
    data : PagoCreate,
    session : Session = Depends(get_db) ):
    nuevo_pago = Pago(
        **data.model_dump()
    )
    session.add(nuevo_pago)
    session.commit()
    session.refresh(nuevo_pago)

    return nuevo_pago

# --- POST BULK: CREAR MUCHOS NUEVOS PAGOS---
@router.post("/bulk") 
def crear_pagos_masivo(
    lista_data: list[PagoCreate],
    session: Session = Depends(get_db)
):

    nuevos_pagos = [Pago(**pago.model_dump()) for pago in lista_data]

    session.add_all(nuevos_pagos)
    session.commit()

    for pago in nuevos_pagos:
        session.refresh(pago)

    return nuevos_pagos

# --- PATCH: ACTUALIZACION PARCIAL ---
@router.patch("/{id_pago}")
def actualizar_pago_parcial(
    id_pago: int,
    data: PagoUpdate,
    session: Session = Depends(get_db)
):
    db_pago = session.get(Pago, id_pago)

    if not db_pago:
        raise HTTPException(status_code=404, detail="Pago no encontrado")

    datos_nuevos = data.model_dump(exclude_unset=True)

    for llave, valor in datos_nuevos.items():
        setattr(db_pago, llave, valor)

    session.add(db_pago)
    session.commit()
    session.refresh(db_pago)

    return db_pago


