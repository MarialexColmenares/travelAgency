from fastapi import APIRouter, Depends,HTTPException
from sqlmodel import Session, select
from modelos.models import Hotel
from database.conexion import get_db
from esquemas.schemas import HotelCreate, HotelUpdate, HotelUpdateParcial

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

# --- GET: OBTENER UN GUIA POR SU ID ---
@router.get("/hotal{id_hotel}")
def obtener_transporte_id(
    id_hotel: int, 
    session: Session = Depends(get_db)):
    
    hotel = session.get(Hotel, id_hotel)

    if not hotel:
        raise HTTPException(status_code=404, detail=f"Hotel {hotel} not found")

    return hotel

# --- GET: OBTENER TODOS LOS GUIAS ---
@router.get("/")
def mostrar_hoteles(
    session: Session = Depends(get_db)
):
    statement = select(Hotel)
    hotel = session.exec(statement).all()

    return hotel

# --- POST BULK: CREAR MUCHOS NUEVOS HOTELES---
@router.post("/bulk")
def crear_hoteles_masivo(
    lista_data: list[HotelUpdateParcial],
    session: Session = Depends(get_db)
):
    nuevos_hoteles = [
        Hotel( **hotel.model_dump()) for hotel in lista_data]
    
    session.add_all(nuevos_hoteles)
    
    session.commit()
    
    for hotel in nuevos_hoteles:
        session.refresh(hotel)

    return nuevos_hoteles

# --- PUT: ACTUALIZACION TOTAL ---
@router.put("/{hotel_id}")
def actualizacion_completa(
    hotel_id: int,
    data: HotelUpdate,
    session: Session = Depends(get_db)
):
    db_hotel = session.get(Hotel, hotel_id)
    if not db_hotel:
        raise HTTPException(status_code=404, detail="Hotel no encontrado")

    datos_nuevos = data.model_dump(exclude_unset=True)

    # 3. Ciclo dinámico para actualizar los atributos del objeto
    for llave, valor in datos_nuevos.items():
        setattr(db_hotel, llave, valor)

    session.add(db_hotel)
    session.commit()
    session.refresh(db_hotel)
    return db_hotel

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

# --- GET: OBTENER HOTELES EN UN DESTINO ---
@router.get("/destino/{destino_id}")
def obtener_hoteles_por_destino(
    destino_id: int, 
    session: Session = Depends(get_db)
):
    statement = select(Hotel).where(Hotel.destino_id == destino_id).all()  
    hoteles = session.exec(statement).all()
    
    if not hoteles:
        raise HTTPException(
            status_code=404, 
            detail=f"No se encontró ningún hotel en el destino: '{destino_id}'"
        )

    return hoteles

# --- GET:FILTRAR HOTELES POR ESTRELLAS ---
@router.get("/estrellas/{cantidad_estrellas}")
def filtrar_por_cantida_de_estrellas(
    cantidad_estrellas: int,
    session: Session = Depends(get_db)
):

    statement = select(Hotel).where(Hotel.categoria == cantidad_estrellas)
    hoteles = session.exec(statement).all()
    
    if not hoteles:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontro ningun hotel de {cantidad_estrellas} estrellas"
        )
    
    return hoteles

# --- GET: FILTRAR POR NOMBRE ---
@router.get("/filter/{nombre}")
def filtrar_hotel_por_nombre(
    nombre: str,
    session: Session = Depends(get_db)
):
    statement = select(Hotel).where(Hotel.nombre.contains(nombre))
    hotel = session.exec(statement).all()
    
    if not hotel:
        raise HTTPException(
            status_code=404, 
            detail=f"No se encontró ningún hotel que coincida con '{nombre}'"
        )

    return hotel

# # --- GET: FILTRAR HOTEL POR CIUDAD ---
@router.get("/filtrar/{ciudad}")
def filtrar_hotel_por_ciudad(
    ciudad: str,
    session: Session = Depends(get_db)
):
    statement = select(Hotel).where(Hotel.ciudad.contains(ciudad))
    hoteles = session.exec(statement).all()
    
    if not hoteles:
        raise HTTPException(
            status_code=404, 
            detail=f"No se encontró ningúna ciudad que coincida con '{ciudad}'"
        )
    
    return hoteles
