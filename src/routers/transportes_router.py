from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from models.modelos import PaqueteTuristico, Transporte
from database.conexion import get_db
from schemas.esquemas import TransporteCreate, TransporteUpdate, TransporteUpdateParcial
from typing import Optional

router = APIRouter(prefix="/transportes", tags=["Transporte"])



# --- POST: CREAR NUEVO TRANSPORTE---
@router.post("/")
def crear_transporte(
    data: TransporteCreate,
    session: Session = Depends(get_db)
):
    nuevo_Transporte = Transporte(
        **data.model_dump() 
    )
    session.add(nuevo_Transporte)
    session.commit()
    session.refresh(nuevo_Transporte)

    return nuevo_Transporte

# --- POST: CREACION MASIVA ---
@router.post("/bulk")
def crear_transportes_masivo(
    transportes_data: list[TransporteCreate],
    session: Session = Depends(get_db)
):
    nuevos_transportes = [
        Transporte(
            **transporte.model_dump()
        ) for transporte in transportes_data
    ]
    
    session.add_all(nuevos_transportes)
    session.commit()

    for transporte in nuevos_transportes:
        session.refresh(transporte)

    return nuevos_transportes

# --- GET: OBTENER TODOS LOS TRANSPORTES ---
@router.get("/")
def mostrar_tansportes(
    session: Session = Depends(get_db)
):
    statement = select(Transporte)
    transporte = session.exec(statement).all()

    if not transporte:
        raise HTTPException(
            status_code=404,
            detail="No se Encontraron Transportes"
        )
    return transporte

# --- GET: OBTENER TRANSPORTES ACTIVOS ---
@router.get("/disponibles")
def obtener_transportes_disponibles(
    session: Session = Depends(get_db)
):
    statement = select(Transporte).where(Transporte.estado == "Activo")
    transportes = session.exec(statement).all()
    
    if not transportes:
        raise HTTPException(
            status_code=404,
            detail="No se Encontraron Transportes Disponibles"
        )
    
    return transportes


@router.get("/filtros")
def filtros(
    empresa: Optional[str] = None,
    paquete: Optional[str] = None,
    capacidad: Optional[int] = None,
    estado: Optional[str] = None,
    session: Session = Depends(get_db)
):
    if empresa:
        statement = select(Transporte).where(Transporte.empresa.ilike(f"%{empresa}%"))
    if paquete:
        statement = select(PaqueteTuristico).where(PaqueteTuristico.nombre.ilike(f"%{paquete}%"))
    if capacidad:
        statement = select(Transporte).where(Transporte.capacidad >= capacidad)
    if estado:
        statement = select(Transporte).where(Transporte.estado.ilike(f"%{estado}%"))

    Transportes = session.exec(statement).all()
    
    if not Transportes:
        raise HTTPException(
            status_code=404,
            detail="No se Encontraron Transportes"
        )
    
    return Transportes

# -- GET: OBTENER UN TRANSPORTE POR SU ID ---
@router.get("/{id_transporte}")
def mostrar_transporte_id(
    id_transporte: int, 
    session: Session = Depends(get_db)
):
    transporte = session.get(Transporte, id_transporte)

    if not transporte:
        raise HTTPException(status_code=404, detail="No se Encontro Ningun transporte con ese ID")

    return transporte

# --- PATCH ACTUALIZACION PARCIAL ---
@router.patch("/{id_transporte}")
def actualizacion_parcial(
    data : TransporteUpdateParcial,
    id_transporte : int,
    session: Session = Depends(get_db)
):
    db_transporte = session.get(Transporte, id_transporte)
    if not db_transporte:
        raise HTTPException(
            status_code=404,
            detail="Transporte no encontrado"
        )
    datos_actualizar = data.model_dump(exclude_unset=True)

    for llave, valor in datos_actualizar.items():
        setattr(db_transporte, llave, valor)

    session.add(db_transporte)
    session.commit()
    session.refresh(db_transporte)
    
    return db_transporte

# --- PUT: ACTUALIZACIÓN TOTAL ---
@router.put("/{id_transporte}")
def actualizacion_completa(
    id: int,
    data: TransporteUpdate,
    session: Session = Depends(get_db)
):
    db_transporte = session.get(Transporte, id)
    if not db_transporte:
        raise HTTPException(
            status_code=404, 
            detail="Transporte no encontrado"
        )

    datos_nuevos = data.model_dump(exclude_unset=True)

    for llave, valor in datos_nuevos.items():
        setattr(db_transporte, llave, valor)

    session.add(db_transporte)
    session.commit()
    session.refresh(db_transporte)
    
    return db_transporte

# --- DELETE: ELIMINACION LOGICA ---
@router.delete("/{transporte_id}")
def eliminacion_logica(
    transporte_id : int,
    session: Session = Depends(get_db)
):
    db_transporte = session.get(Transporte, transporte_id)
    
    if not db_transporte:
        raise HTTPException(
            status_code=404, 
            detail="Transporte no encontrado"
        )
    
    db_transporte.estado = "Inactivo"
    
    session.add(db_transporte)
    session.commit()
    session.refresh(db_transporte)
    
    return db_transporte
    
