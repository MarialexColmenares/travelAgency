from models.modelos import Pago
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database.conexion import get_db
from schemas.esquemas import PagoCreate, PagoUpdate, PagoUpdateParcial

router = APIRouter(prefix="/pagos",tags=["Pagos"])

# --- GET: OBTENER TODOS LOS PAGOS ---
@router.get("/")
def mostrar_pago(session : Session = Depends(get_db) ):

    statement = select(Pago)
    pagos = session.exec(statement).all()

    if not pagos:
        raise HTTPException(
            status_code=404,
            detail="No se Encontraron Registros de Pagos"
        )

    return pagos

# --- POST: CREAR UN NUEVO PAGO---
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

# --- GET: OBTENER UN PAGO POR SU ID ---
@router.get("/{id_pago}")
def obtener_transporte_id(id_pago: int, session: Session = Depends(get_db)):
    
    pago = session.get(Pago, id_pago)

    if not pago:
        raise HTTPException(status_code=404, detail="Pago not found")

    return pago

# --- PATCH: ACTUALIZACION PARCIAL ---
@router.patch("/{id_pago}")
def actualizar_pago_parcial(
    id_pago: int,
    data: PagoUpdateParcial,
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

# --- PUT: ACTUALIZACIÓN TOTAL ---
@router.put("/{id_pago}")
def actualizacion_completa(
    id_pago: int,
    data: PagoUpdate,
    session: Session = Depends(get_db)
):
    db_pago = session.get(Pago, id_pago)
    if not db_pago:
        raise HTTPException(
            status_code=404, 
            detail="Pago no Encontrado"
        )

    datos_nuevos = data.model_dump(exclude_unset=True)

    for llave, valor in datos_nuevos.items():
        setattr(db_pago, llave, valor)

    session.add(db_pago)
    session.commit()
    session.refresh(db_pago)

    return db_pago
