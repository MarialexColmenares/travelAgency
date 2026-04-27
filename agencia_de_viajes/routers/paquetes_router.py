from fastapi import APIRouter, Depends,HTTPException
from sqlmodel import Session, select
from conexion import get_db
from schemas import PaqueteCreate, PaqueteUpdate
from models import PaqueteTuristico

router = APIRouter(prefix="/paquetes", tags=["Paquetes_Turisticos"])

# --- GET: OBTENER TODOS LOS PAQUETES TURISTICOS ---
@router.get("/paquetesTuristicos")
def mostrar_paquetes(session: Session = Depends(get_db)):

    statement = select(PaqueteTuristico)
    paquetes = session.exec(statement).all()

    return paquetes

# --- GET: OBTENER UN PAQUETE POR SU ID ---
@router.get("/paquete{id_paquete}")
def obtener_transporte_id(id_paquete: int, session: Session = Depends(get_db)):
    paquete = session.get(PaqueteTuristico, id_paquete)

    if not paquete:

        raise HTTPException(status_code=404, detail="Paquete not found")

    return paquete

# --- POST: CREAR UN NUEVO PAQUETE ---
@router.post("/paquetesTuristicos")
def crear_paquete_turistico(
    paquete_data: PaqueteCreate,
    session: Session = Depends(get_db)
):
    nuevo_paquete = PaqueteTuristico(
        nombre=paquete_data.nombre,
        descripcion=paquete_data.descripcion,
        duracion=paquete_data.duracion,
        precio=paquete_data.precio,
        cupo=paquete_data.cupo,
        estado=paquete_data.estado,
        guia_id=paquete_data.guia_id,
        transporte_id=paquete_data.transporte_id,
        hotel_id=paquete_data.hotel_id
    )

    session.add(nuevo_paquete)
    session.commit()
    session.refresh(nuevo_paquete)

    return nuevo_paquete

# --- PATCH: ACTUALIZACION PARCIAL ---
@router.patch("/{paquete_id}")
def actualizar_paquete(
    paquete_id: int,
    paquete_data: PaqueteUpdate,
    session: Session = Depends(get_db)
):
    db_paquete = session.get(PaqueteTuristico, paquete_id)
    if not db_paquete:
        raise HTTPException(status_code=404, detail="Paquete no encontrado")

    datos_nuevos = paquete_data.model_dump(exclude_unset=True)
    for llave, valor in datos_nuevos.items():
        setattr(db_paquete, llave, valor)

    session.add(db_paquete)
    session.commit()
    session.refresh(db_paquete)
    return db_paquete

#--- DISPONIBILIDAD DE CUPOS EN UN PAQUETE  ---
@router.get("/{paquete_id}/disponibilidad")
def consultar_disponibilidad(paquete_id: int, session: Session = Depends(get_db)):
    # 1. Buscamos el paquete
    paquete = session.get(PaqueteTuristico, paquete_id)
    if not paquete:
        raise HTTPException(status_code=404, detail="Paquete no encontrado")

    # 2. Lógica matemática
    total_reservado = sum(
        reserva.cantidad_personas
        for reserva in paquete.reservas
        if reserva.estado != "Cancelada"
    )
    cupos_libres = paquete.cupo - total_reservado

    # 3. Guardamos todo en una variable (diccionario)
    reporte_disponibilidad = {
        "paquete": paquete.nombre,
        "cupo_total": paquete.cupo,
        "cupos_ocupados": total_reservado,
        "cupos_disponibles": max(0, cupos_libres),
        "estado": "Agotado" if cupos_libres <= 0 else "Disponible"
    }

    # 4. Retornamos la variable
    return reporte_disponibilidad
