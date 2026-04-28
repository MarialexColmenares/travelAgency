from fastapi import APIRouter, Depends,HTTPException
from sqlmodel import Session, select
from modelos.models import Hotel
from database.conexion import get_db
from esquemas.schemas import HotelCreate, HotelUpdate

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
def crear_Hoteles(
    lista_data: list[HotelCreate],
    session: Session = Depends(get_db)
):
    nuevos_hoteles = [Hotel(**hotel.model_dump()) for hotel in lista_data]
    
    session.add_all(nuevos_hoteles)
    
    session.commit()
    
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
