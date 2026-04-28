from fastapi import APIRouter, Depends,HTTPException
from sqlmodel import Session, select
from models import Hotel
from conexion import get_db
from schemas import HotelCreate, HotelUpdate

router = APIRouter(prefix="/hoteles", tags=["Hoteles"])

# --- GET: OBTENER TODOS LOS GUIAS ---
@router.get("/")
def mostrar_hoteles(session: Session = Depends(get_db)):

    statement = select(Hotel)
    hotel = session.exec(statement).all()

    return hotel

# --- GET: OBTENER UN GUIA POR SU ID ---
@router.get("/hotal{id_hotel}")
def obtener_transporte_id(id_hotel: int, session: Session = Depends(get_db)):
    hotel = session.get(Hotel, id_hotel)

    if not hotel:

        raise HTTPException(status_code=404, detail="Hotelhotel not found")

    return hotel

# --- POST: CREAR NUEVO HOTEL---
@router.post("/")
def crearCliente(
    data: HotelCreate, # Recibe los datos validados por el esquema Pydantic
    session: Session = Depends(get_db)
    ):
    # Instanciamos el modelo Cliente con los datos recibidos
    nuevo_hotel = Hotel(
        **data.model_dump()
    )
    session.add(nuevo_hotel)     # Preparamos la inserción
    session.commit()              # Guardamos los cambios en la DB
    session.refresh(nuevo_hotel) # Refrescamos para obtener el ID generado automáticamente
    return nuevo_hotel

# --- POST BULK: CREAR MUCHOS NUEVOS HOTELES---
@router.post("/bulk")
def crear_Hoteles(
    lista_data: list[HotelCreate],
    session: Session = Depends(get_db)
):
    # Convertimos la lista de esquemas a lista de modelos
    nuevos_hoteles = [Hotel(**hotel.model_dump()) for hotel in lista_data]
    
    # 1. USAR add_all para listas
    session.add_all(nuevos_hoteles)
    
    # 2. Guardar cambios
    session.commit()
    
    # 3. REFRESCAR uno por uno (no se puede refrescar una lista completa)
    for hotel in nuevos_hoteles:
        session.refresh(hotel)

    return nuevos_hoteles
# --- PATCH: ACTUALIZACION PARCIAL ---
@router.patch("/{hotel_id}")
def actualizar_parcial_hotel(
    hotel_id: int,
    data: HotelUpdate,
    session: Session = Depends(get_db)
):
    db_hotel = session.get(Hotel, hotel_id)
    if not db_hotel:
        raise HTTPException(status_code=404, detail="Hotel no encontrado")

    datos_actualizar = data.model_dump(exclude_unset=True)

    for llave, valor in datos_actualizar.items():

        setattr(db_hotel, llave, valor)

    session.commit()
    session.add(db_hotel)

    session.refresh(db_hotel)
    return db_hotel
