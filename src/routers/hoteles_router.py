from fastapi import APIRouter, Depends,HTTPException
from sqlmodel import Session, select
from models.modelos import Hotel, Destino
from database.conexion import get_db
from schemas.esquemas import HotelCreate, HotelUpdate, HotelUpdateParcial
from typing import Optional

router = APIRouter(prefix="/hoteles", tags=["Hoteles"])

# --- POST: CREAR NUEVO HOTEL---
@router.post("/")
def crear_hotel(
    data: HotelCreate, 
    session: Session = Depends(get_db)
):
    nuevo_hotel = Hotel(
        **data.model_dump()
    )
    session.add(nuevo_hotel)   
    session.commit()             
    session.refresh(nuevo_hotel)
    
    return nuevo_hotel

# --- POST BULK: CREAR MUCHOS NUEVOS HOTELES---
@router.post("/bulk")
def crear_hoteles_masivo(
    lista_data: list[HotelCreate],
    session: Session = Depends(get_db)
):
    nuevos_hoteles = [
        Hotel( **hotel.model_dump()) for hotel in lista_data]
    
    session.add_all(nuevos_hoteles)
    session.commit()
    
    for hotel in nuevos_hoteles:
        session.refresh(hotel)

    return nuevos_hoteles

# --- GET: MOSTRAR TODOS LOS HOTELES ---
@router.get("/")
def mostrar_hoteles(
    session: Session = Depends(get_db)
):
    statement = select(Hotel)
    hoteles = session.exec(statement).all()

    if not hoteles:
        raise HTTPException(
            status_code=404, 
            detail="No se Encontraron Hoteles"
        )
    return hoteles

# --- GET: FILTROS ---
@router.get("/filtros")
def filtros(
    nombre:Optional[str],
    estrellas: Optional[int],
    ciudad: Optional[str],
    session: Session = Depends(get_db)
):

    if nombre:
        statement = select(Hotel).where(Hotel.nombre.ilike(f"%{nombre}%"))
    if estrellas:
        statement = select(Hotel).where(Hotel.categoria == estrellas)
    if ciudad:
        statement = statement.join(Destino).where(Destino.ciudad.ilike(f"%{ciudad}%"))
        
    hoteles = session.exec(statement).all()
    
    if not hoteles:
        raise HTTPException(
            status_code=404, 
            detail="No se Encontraron hoteles"               
        )

    return hoteles

# --- GET: OBTENER UN HOTEL POR SU ID ---
@router.get("/{id_hotel}")
def obtener_transporte_id(
    id_hotel: int, 
    session: Session = Depends(get_db)
):
    hotel = session.get(Hotel, id_hotel)

    if not hotel:
        raise HTTPException(
            status_code=404, 
            detail=f"Hotel {hotel} No encontrado"
        )
    return hotel

# --- PATCH: ACTUALIZACION PARCIAL ---
@router.patch("/{hotel_id}")
def actualizar_parcial_hotel(
    hotel_id: int,
    data: HotelUpdate,
    session: Session = Depends(get_db)
):
    db_hotel = session.get(Hotel, hotel_id)

    if not db_hotel:
        raise HTTPException(
            status_code=404, 
            detail="Hotel no encontrado"
        )
    datos_actualizar = data.model_dump(exclude_unset=True)

    for llave, valor in datos_actualizar.items():
        setattr(db_hotel, llave, valor)

    session.commit()
    session.add(db_hotel)
    session.refresh(db_hotel)
    
    return db_hotel

# --- PUT: ACTUALIZACION TOTAL ---
@router.put("/{hotel_id}")
def actualizacion_completa(
    hotel_id: int,
    data: HotelUpdate,
    session: Session = Depends(get_db)
):
    db_hotel = session.get(Hotel, hotel_id)
    if not db_hotel:
        raise HTTPException(
            status_code=404, 
            detail="Hotel no encontrado"
        )

    datos_nuevos = data.model_dump(exclude_unset=True)

    for llave, valor in datos_nuevos.items():
        setattr(db_hotel, llave, valor)

    session.add(db_hotel)
    session.commit()
    session.refresh(db_hotel)
    
    return db_hotel

# --- DELETE: ELIMINACION LOGICA ---
@router.delete("/{id_destino}")
def eliminar_hotel(
    id: int,
    session: Session = Depends(get_db)
):
    db_hotel= session.get(Hotel, id)
    
    if not db_hotel:
        raise HTTPException(status_code=404, detail="Destino no encontrado")
    
    db_hotel.estado = False
    
    session.add(db_hotel)
    session.commit()
    session.refresh(db_hotel)
    
    return {"message": f"Destino con id {db_hotel} ha sido eliminado"}
