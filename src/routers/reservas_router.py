from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database.conexion import get_db
from models.modelos import Reserva, PaqueteTuristico
from schemas.esquemas import ReservaCreate, ReservaUpdate

router = APIRouter(prefix="/reservas", tags=["Reservas"])

# --- GET: OBTENER TODOS LAS RESERVAS ---
@router.get("/")
def mostrar_reservas(
    session: Session = Depends(get_db)):

    statement = select(Reserva)
    reservas = session.exec(statement).all()

    if not reservas:
        raise HTTPException(
            status_code=404,
            detail="No se Encontraron Reservas"
        )
    return reservas

# --- POST: CREAR UNA NUEVA RESERVA ---
@router.post("/reservas/")
def crear_reserva(reserva: Reserva, session: Session = Depends(get_db)):
    paquete = session.get(PaqueteTuristico, reserva.paquete_id)
    
    if not paquete:
        raise HTTPException(status_code=404, detail="El paquete seleccionado no existe")
    
    if paquete.cupo < reserva.cantidad_personas:
        raise HTTPException(
            status_code=400, 
            detail=f"No hay cupo suficiente. Lugares disponibles: {paquete.cupo}"
        )

    reserva.monto_total = paquete.precio * reserva.cantidad_personas
    paquete.cupo -= reserva.cantidad_personas
    
    if paquete.cupo == 0:
        paquete.estado = "Agotado"

    session.add(reserva) 
    session.add(paquete) 
    session.commit()
    session.refresh(reserva)
    
    return {
        "mensaje": "Reserva creada exitosamente",
        "detalle": reserva,
        "cupos_restantes_en_paquete": paquete.cupo
    }

# --- POST BULK: CREAR MUCHAS NUEVAS RESERVAS---
@router.post("/bulk")
def crear_reservas_masivo(
    reservas_data: list[ReservaCreate],
    session: Session = Depends(get_db)
):
    nuevas_reservas = [
        Reserva(**reserva.model_dump()
        ) for reserva in reservas_data
    ]
    session.add_all(nuevas_reservas)
    session.commit()

    for reserva in nuevas_reservas:
        session.refresh(reserva)

    return nuevas_reservas

# --- CONSULTAR SALDO PENDIENTE ---
@router.get("/{id_reserva}/saldo")
def consultar_saldo_reserva(
    id_reserva: int, 
    session: Session = Depends(get_db)
):
    reserva = session.get(Reserva, id_reserva)
    
    if not reserva:
        raise HTTPException(
            status_code=404, 
            detail="Reserva no encontrada"
        )

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

# --- GET: OBTENER UNA RESERVA POR SU ID ---
@router.get("/{id_reserva}")
def obtener_reserva_id(
    id_reserva: int, session: Session = Depends(get_db)):
    reserva = session.get(Reserva, id_reserva)

    if not reserva:
        raise HTTPException(
            status_code=404,
            detail="Reserva no Encontrada"
        )

    return reserva

# --- PATCH: ACTUALIZACION PARCIAL---
@router.patch("/{id_reserva}")
def actualizar_parcial_reserva(
    id_reserva: int,
    reserva_data: ReservaUpdate,
    session: Session = Depends(get_db)
):
    db_reserva = session.get(Reserva, id_reserva)
    if not db_reserva:
        raise HTTPException(
            status_code=404, 
            detail="Reserva no encontrada"
        )
    datos_nuevos = reserva_data.model_dump(exclude_unset=True)
    for llave, valor in datos_nuevos.items():
        setattr(db_reserva, llave, valor)

    session.add(db_reserva)
    session.commit()
    session.refresh(db_reserva)

    return db_reserva

# --- PUT: ACTUALIZACIÓN TOTAL ---
@router.put("/{id_reserva}")
def actualizacion_completa(
    id_reserva: int,
    data: ReservaUpdate,
    session: Session = Depends(get_db)
):
    db_reserva = session.get(Reserva, id_reserva)
    if not db_reserva:
        raise HTTPException(
            status_code=404, 
            detail="Cliente no encontrado"
        )

    datos_nuevos = data.model_dump(exclude_unset=True)

    for llave, valor in datos_nuevos.items():
        setattr(db_reserva, llave, valor)

    session.add(db_reserva)
    session.commit()
    session.refresh(db_reserva)

    return db_reserva

#  cancelaciones
@router.delete("/{id_reserva}")
def cancelar_reserva(
    
    id_reserva: int,
    session: Session = Depends(get_db)
):
    reserva = session.get(Reserva, id_reserva)
    
    if not reserva:
        raise HTTPException(
            status_code=404,
            detail="Reserva no Encontrada"
        )
    
    reserva.estado = "Cancelada"
    
    return reserva

