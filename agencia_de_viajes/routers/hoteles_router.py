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
@router.post("")
def crear_Hotel(
    hotel_data: HotelCreate,
    session: Session = Depends(get_db)
):
    nuevo_hotel = Hotel(
        nombre = hotel_data.nombre,
        categoria = hotel_data.categoria,
        direccion = hotel_data.direccion,
        ciudad = hotel_data.ciudad,
        contacto = hotel_data.contacto
    )

    session.add(nuevo_hotel)
    session.commit()
    session.refresh(nuevo_hotel)

    return nuevo_hotel

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
