from fastapi import APIRouter, Depends,HTTPException
from sqlmodel import Session, select
from database.conexion import get_db
from schemas.esquemas import PaqueteCreate, PaqueteUpdate, PaqueteInfoCliente, DestinoSimple
from models.modelos import PaqueteDestinoLink, PaqueteTuristico, Destino
from typing import Optional


router = APIRouter(prefix="/paquetes-turisticos", tags=["Paquetes Turisticos"])

# --- GET: OBTENER TODOS LOS PAQUETES TURISTICOS ---
@router.get("/")
def mostrar_paquetes(
    session: Session = Depends(get_db)
):
    statement = select(PaqueteTuristico)
    paquetes = session.exec(statement).all()
    
    if not paquetes:
        raise HTTPException(
            status_code=404,
            detail="No se Encontraron Paquetes Turisticos"
        )
    return paquetes

# --- POST: CREAR UN NUEVO PAQUETE ---
@router.post("/")
def crear_paquete_turistico_con_destinos(
    paquete_data: PaqueteCreate,
    session: Session = Depends(get_db)
):
    nuevo_paquete = PaqueteTuristico(
        **paquete_data.model_dump()
    )

    session.add(nuevo_paquete)
    session.commit()
    session.refresh(nuevo_paquete)

    return nuevo_paquete

# --- POST BULK: CREAR MUCHOS NUEVOS PAQUETES---
@router.post("/bulk")
def crear_paquetes_con_destinos_masivo(
    lista_data: list[PaqueteCreate],
    session: Session = Depends(get_db)
):
    nuevos_paquetes_creados = []

    for data in lista_data:
        destinos_ids = data.destinos_ids
        datos_paquete = data.model_dump(exclude={"destinos_ids"})
        
        nuevo_paquete = PaqueteTuristico(**datos_paquete)
        
        session.add(nuevo_paquete)
        session.flush() 
        
        for d_id in destinos_ids:
            link = PaqueteDestinoLink(
                paquete_id=nuevo_paquete.id,
                destino_id=d_id
            )
            session.add(link)
            
        nuevos_paquetes_creados.append(nuevo_paquete)

    session.commit()
    
    for p in nuevos_paquetes_creados:
        session.refresh(p)

    return nuevos_paquetes_creados

# --- GET: FILTROS ---
@router.get("/filtros")
def filtros(
    nombre:Optional[str] = None,
    presupuesto: Optional[float] = None,
    duracion:Optional[str] = None,
    destino_ciudad:Optional[str] = None,
    session: Session = Depends(get_db)
):
    statement = select(PaqueteTuristico)
    
    if destino_ciudad:
        statement = statement.join(PaqueteDestinoLink).join(Destino).where(
            Destino.ciudad.ilike(f"%{destino_ciudad}%")
        )
    if nombre:
        statement = statement.where(PaqueteTuristico.nombre.ilike(f"%{nombre}%"))
    if presupuesto:
        statement = statement.where(PaqueteTuristico.precio <= presupuesto)
    if duracion:
        statement = statement.where(PaqueteTuristico.duracion.ilike(f"%{duracion}%"))
    
    paquetes = session.exec(statement).all()
    
    if not paquetes:
        raise HTTPException(
            status_code=404, 
            detail="No se Encontraron Paquetes"
        )
    return paquetes

#--- DISPONIBILIDAD DE CUPOS EN UN PAQUETE  ---
@router.get("/{id_paquete}/disponibilidad")
def consultar_disponibilidad(
    paquete_id: int, session: 
    Session = Depends(get_db)
):
    paquete = session.get(PaqueteTuristico, paquete_id)
    if not paquete:
        raise HTTPException(status_code=404, detail="Paquete no encontrado")
    
    total_reservado = sum(
        reserva.cantidad_personas
        for reserva in paquete.reservas
        if reserva.estado != "Cancelada"
    )
    cupos_libres = paquete.cupo - total_reservado
    
    reporte_disponibilidad = {
        "paquete": paquete.nombre,
        "cupo_total": paquete.cupo,
        "cupos_ocupados": total_reservado,
        "cupos_disponibles": max(0, cupos_libres),
        "estado": "Agotado" if cupos_libres <= 0 else "Disponible"
    }
    return reporte_disponibilidad

# --- GET: DETALLES DEL PAQUETE ---
@router.get("/{id_paquete}/info-publica", response_model=PaqueteInfoCliente)
def obtener_info_detalles_paquete(
    id_paquete: int, 
    session: Session = Depends(get_db)
):
    paquete = session.get(PaqueteTuristico, id_paquete)
    
    if not paquete:
        raise HTTPException(status_code=404, detail="Paquete no encontrado")
    
    resultado = PaqueteInfoCliente(
        nombre=paquete.nombre,
        descripcion=paquete.descripcion,
        duracion=paquete.duracion,
        precio=paquete.precio,
        cupo=paquete.cupo,
        estado=paquete.estado,
        
        nombre_guia=paquete.guia.nombre if paquete.guia else "No asignado",
        transporte_empresa=paquete.transporte.empresa if paquete.transporte else "No asignado",

        destinos=[
            DestinoSimple(ciudad=d.ciudad, pais=d.pais) 
            for d in paquete.destinos
        ]
    )
    return resultado

# --- GET: PAQUETE CON DESTINOS
@router.get("/{id_paquete}/itinerario")
def ver_destinos_del_paquete(
    id_paquete: int, 
    session: Session = Depends(get_db)):
    paquete = session.get(PaqueteTuristico, id_paquete)
    
    if not paquete:
        raise HTTPException(
            status_code=404, 
            detail="Paquete no encontrado"
        )
    lista_destinos = [
        {"ciudad": d.ciudad, "pais": d.pais} 
        for d in paquete.destinos
    ]
    return {
        "paquete": paquete.nombre,
        "precio": paquete.precio,
        "itinerario": lista_destinos if lista_destinos else "No tiene destinos asignados"
    }
    
# --- GET: OBTENER UN PAQUETE POR SU ID ---
@router.get("/{id_paquete}")
def obtener_transporte_id(
    id_paquete: int, 
    session: Session = Depends(get_db)
):
    paquete = session.get(PaqueteTuristico, id_paquete)

    if not paquete:

        raise HTTPException(status_code=404, detail="Paquete not found")

    return paquete

# --- PATCH: ACTUALIZACION PARCIAL ---
@router.patch("/{id_paquete}")
def actualizar_paquete(
    id_paquete: int,
    paquete_data: PaqueteUpdate,
    session: Session = Depends(get_db)
):
    db_paquete = session.get(PaqueteTuristico, id_paquete)
    if not db_paquete:
        raise HTTPException(status_code=404, detail="Paquete no encontrado")

    datos_nuevos = paquete_data.model_dump(exclude_unset=True)
    for llave, valor in datos_nuevos.items():
        setattr(db_paquete, llave, valor)

    session.add(db_paquete)
    session.commit()
    session.refresh(db_paquete)
    return db_paquete

# --- PUT: ACTUALIZACIÓN TOTAL ---
@router.put("/{paquete_id}")
def actualizacion_completa(
    paquete_id: int,
    paquete_data: PaqueteUpdate,
    session: Session = Depends(get_db)
):
    db_paquete = session.get(PaqueteTuristico, paquete_id)
    if not db_paquete:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    datos_nuevos = paquete_data.model_dump(exclude_unset=True)

    for llave, valor in datos_nuevos.items():
        setattr(db_paquete, llave, valor)

    session.add(db_paquete)
    session.commit()
    session.refresh(db_paquete)

    return db_paquete


# --- DELETE: ELIMINACIÓN LÓGICA DE PAQUETE ---
@router.delete("/desactivar/{id_paquete}")
def desactivar_paquete(
    id_paquete: int,
    session: Session = Depends(get_db)
):
    # 1. Buscamos el paquete en la base de datos
    db_paquete = session.get(PaqueteTuristico, id_paquete)

    if not db_paquete:
        raise HTTPException(status_code=404, detail="Paquete no encontrado")

    db_paquete.estado = "Inactivo"

    session.add(db_paquete)
    session.commit()
    session.refresh(db_paquete)

    return {"mensaje": f"El paquete '{db_paquete.nombre}' ha sido desactivado exitosamente"}


# --- PATCH: RE-ACTIVACION ---
@router.patch("/{id_paquete}/activar")
def activar_paquete(
    id_paquete: int,
    session: Session = Depends(get_db)
):
    db_paquete = session.get(PaqueteTuristico, id_paquete)
    
    if not id_paquete:
        raise HTTPException(status_code=404, detail="Paquete no encontrado")
    if db_paquete.estado == "Disponible":
        raise HTTPException(status_code=400, detail=f"El Hotel {db_paquete.nombre} Se ya se Encuentra Disponible")
    
    db_paquete.estado = "Diasponible"
    
    session.add(db_paquete)
    session.commit()
    session.refresh(db_paquete)
    
    return {"message": f"El Paquete {db_paquete.nombre} ha Sido Reactivado con Exito"}
