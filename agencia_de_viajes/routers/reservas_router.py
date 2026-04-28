from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database.conexion import get_db
from modelos.models import Reserva, Transporte
from esquemas.schemas import ReservaCreate, ReservaUpdate

router = APIRouter(prefix="/reservas", tags=["Reservas"])

# --- GET: OBTENER TODOS LAS RESERVAS ---
@router.get("/reservas")
def leer_reservas(
    session: Session = Depends(get_db)):

    statement = select(Reserva)
    reservas = session.exec(statement).all()

    return reservas

# --- GET: OBTENER UNA RESERVA POR SU ID ---
@router.get("/reserva{id_reserva}")
def obtener_reserva_id(
    id_reserva: int, session: Session = Depends(get_db)):
    reserva = session.get(Reserva, id_reserva)

    if not reserva:

        raise HTTPException(status_code=404, detail="Cliente not found")

    return reserva

# --- POST: CREAR UNA NUEVA RESERVA ---
@router.post("/reservas")
def crear_reserva(
    data_reserva: ReservaCreate,
    session: Session = Depends(get_db)
):
    nueva_reserva = Reserva(
        fecha =data_reserva.fecha,
        cantidad_personas = data_reserva.cantidad_personas,
        estado = data_reserva.estado,
        monto_total = data_reserva.monto_total,
        comentarios = data_reserva.comentarios,
        cliente_id = data_reserva.cliente_id,
        paquete_id = data_reserva.paquete_id
    )

    session.add(nueva_reserva)
    session.commit()
    session.refresh(nueva_reserva)

    return nueva_reserva

# --- POST BULK: CREAR MUCHAS NUEVAS RESERVAS---
@router.post("/bulk")
def crear_reservas(
    reservas_data: list[ReservaCreate],
    session: Session = Depends(get_db)
):
    nuevas_reservas = [Reserva(**reserva.model_dump()) for reserva in reservas_data]
    session.add_all(nuevas_reservas)
    session.commit()

    for reserva in nuevas_reservas:
        session.refresh(reserva)

    return nuevas_reservas


# --- PATCH: ACTUALIZACION PARCIAL---
@router.patch("/{reserva_id}")
def actualizar_parcial_reserva(
    reserva_id: int,
    reserva_data: ReservaUpdate,
    session: Session = Depends(get_db)
):
    db_reserva = session.get(Reserva, reserva_id)
    if not db_reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")

    datos_nuevos = reserva_data.model_dump(exclude_unset=True)
    for llave, valor in datos_nuevos.items():
        setattr(db_reserva, llave, valor)

    session.add(db_reserva)
    session.commit()
    session.refresh(db_reserva)
    return db_reserva

# --- CONSULTAR SALDO PENDIENTE ---
@router.get("/{reserva_id}/saldo")
def consultar_saldo_reserva(reserva_id: int, session: Session = Depends(get_db)):
    # 1. Buscamos la reserva en la base de datos
    reserva = session.get(Reserva, reserva_id)
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")

    total_pagado = sum(pago.monto for pago in reserva.pagos)

    saldo_pendiente = reserva.monto_total - total_pagado

    estado_cuenta = {
        "cliente": reserva.cliente.nombre,
        "paquete": reserva.paquete.nombre,
        "monto_total_viaje": reserva.monto_total,
        "total_abonado": total_pagado,
        "saldo_restante": max(0, saldo_pendiente),
        "estado_pago": "Liquidado" if saldo_pendiente <= 0 else "Pendiente"
    }

    return estado_cuenta
