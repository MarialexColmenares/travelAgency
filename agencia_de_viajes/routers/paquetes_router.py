from fastapi import APIRouter, Depends,HTTPException
from sqlmodel import Session, select
from database.conexion import get_db
from esquemas.schemas import PaqueteCreate, PaqueteUpdate, PaqueteInfoCliente, DestinoSimple
from modelos.models import PaqueteDestinoLink, PaqueteTuristico

router = APIRouter(prefix="/paquetes", tags=["Paquetes Turisticos"])

# --- POST: CREAR UN NUEVO PAQUETE ---
@router.post("/paquetesTuristicos")
def crear_paquete_turistico_con_destinos(
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

# --- GET: OBTENER TODOS LOS PAQUETES TURISTICOS ---
@router.get("/paquetesTuristicos")
def mostrar_paquetes(
    session: Session = Depends(get_db)
):

    statement = select(PaqueteTuristico)
    paquetes = session.exec(statement).all()

    return paquetes

# --- POST BULK: CREAR MUCHOS NUEVOS PAQUETES---
@router.post("/bulk")
def crear_paquetes_con_destinos_masivo(
    lista_data: list[PaqueteCreate],
    session: Session = Depends(get_db)
):
    nuevos_paquetes_creados = []

    for data in lista_data:
        # 1. Extraer los IDs de destinos y limpiar los datos para el modelo Paquete
        destinos_ids = data.destinos_ids
        datos_paquete = data.model_dump(exclude={"destinos_ids"})
        
        # 2. Crear la instancia del Paquete
        nuevo_paquete = PaqueteTuristico(**datos_paquete)
        session.add(nuevo_paquete)
        session.flush() # Esto genera el ID del paquete sin cerrar la transacción

        # 3. Crear las conexiones en la tabla link
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

# --- GET: OBTENER UN PAQUETE POR SU ID ---
@router.get("/paquete/{id_paquete}")
def obtener_transporte_id(
    id_paquete: int, 
    session: Session = Depends(get_db)
):
    paquete = session.get(PaqueteTuristico, id_paquete)

    if not paquete:

        raise HTTPException(status_code=404, detail="Paquete not found")

    return paquete

# --- GET: OBTENER PAQUETE POR NOMBRE ---
@router.get("/nombre/{nombre_paquete}")
def obtener_paquete_por_nombre(
    nombre_paquete: str,
    session: Session = Depends(get_db)
):

    statement = select(PaqueteTuristico).where(PaqueteTuristico.nombre.contains(nombre_paquete))
    paquetes = session.exec(statement).all()

    if not paquetes:
        raise HTTPException(
            status_code=404, 
            detail=f"No se encontró ningún paquete que coincida con '{nombre_paquete}'"
        )

    return paquetes

@router.get("/{id_paquete}/info-cliente", response_model=PaqueteInfoCliente)
def obtener_info_publica_paquete(
    id_paquete: int, 
    session: Session = Depends(get_db)
):
    # Buscamos el paquete
    paquete = session.get(PaqueteTuristico, id_paquete)
    
    if not paquete:
        raise HTTPException(status_code=404, detail="Paquete no encontrado")

    # Construimos la respuesta extrayendo los nombres de las relaciones
    return PaqueteInfoCliente(
        nombre=paquete.nombre,
        descripcion=paquete.descripcion,
        duracion=paquete.duracion,
        precio=paquete.precio,
        cupo=paquete.cupo,
        estado=paquete.estado,
        # Accedemos a los objetos relacionados gracias a Relationship en models.py
        nombre_guia=paquete.guia.nombre if paquete.guia else "No asignado",
        transporte_empresa=paquete.transporte.empresa if paquete.transporte else "No asignado",
        nombre_hotel=paquete.hotel.nombre if paquete.hotel else "No asignado",
        # Mapeamos la lista de destinos a nuestro esquema simple
        destinos=[
            DestinoSimple(ciudad=d.ciudad, pais=d.pais) 
            for d in paquete.destinos
        ]
    )