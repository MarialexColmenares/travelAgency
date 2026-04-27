from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from conexion import get_db
from models import Reserva
from schemas import ReservaCreate, ReservaUpdate

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

    # 2. Calculamos el total pagado sumando la lista de pagos de la reserva
    # Usamos la relación 'reserva.pagos' que definiste en tus modelos
    total_pagado = sum(pago.monto for pago in reserva.pagos)

    # 3. Calculamos cuánto falta
    saldo_pendiente = reserva.monto_total - total_pagado

    # 4. Guardamos todo en una variable para un retorno ordenado
    estado_cuenta = {
        "cliente": reserva.cliente.nombre,
        "paquete": reserva.paquete.nombre,
        "monto_total_viaje": reserva.monto_total,
        "total_abonado": total_pagado,
        "saldo_restante": max(0, saldo_pendiente),
        "estado_pago": "Liquidado" if saldo_pendiente <= 0 else "Pendiente"
    }

    return estado_cuenta
