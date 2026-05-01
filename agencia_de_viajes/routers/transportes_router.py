from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from modelos.models import PaqueteTuristico, Transporte
from database.conexion import get_db
from esquemas.schemas import TransporteCreate, TransporteUpdate 

router = APIRouter(prefix="/transportes", tags=["Transporte"])

# --- POST: CREAR NUEVO TRANSPORTE---
@router.post("/crear")
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

# --- GET: OBTENER TODOS LOS TRANSPORTES ---
@router.get("/mostrar")
def mostrar_tansportes(
    session: Session = Depends(get_db)):

    statement = select(Transporte)
    transporte = session.exec(statement).all()

    return transporte

# --- GET: OBTENER UN TRANSPORTE POR SU ID ---
@router.get("/mostrar/{id_transporte}")
def mostrar_transporte_id(
    id_transporte: int, 
    session: Session = Depends(get_db)):
    
    transporte = session.get(Transporte, id_transporte)

    if not transporte:
        raise HTTPException(status_code=404, detail="Transportes not found")

    return transporte

# --- POST: CREACION MASIVA ---
@router.post("/bulk")
def crear_transportes_masivo(
    transportes_data: list[TransporteCreate],
    session: Session = Depends(get_db)
):
    nuevos_transportes = [
        
        Transporte(
            **transporte.model_dump()) 
        
        for transporte in transportes_data]
    
    session.add_all(nuevos_transportes)
    session.commit()

    for transporte in nuevos_transportes:
        session.refresh(transporte)

    return nuevos_transportes

# --- PATCH ACTUALIZACION PARCIAL ---
@router.patch("/actualizar")
def actualizacion_parcial(
    data : TransporteUpdate,
    transporte_id : int,
    session: Session = Depends(get_db)
):
    db_transporte = session.get(Transporte, transporte_id)
    if not db_transporte:
        raise HTTPException(status_code=404, detail="Transporte no encontrado")

    # model_dump(exclude_unset=True) para: evita sobreescribir con valores nulos
    datos_actualizar = data.model_dump(exclude_unset=True)

    for llave, valor in datos_actualizar.items():
        setattr(db_transporte, llave, valor)

    session.add(db_transporte)
    session.commit()
    session.refresh(db_transporte)
    return db_transporte

# --- DELETE: ELIMINACION LOGICA ---
@router.delete("/eliminar/{transporte_id}")
def eliminacion_logica(
    transporte_id : int,
    session: Session = Depends(get_db)
):
    db_transporte = session.get(Transporte, transporte_id)
    
    if not db_transporte:
        raise HTTPException(status_code=404, detail="Transporte no encontrado")
    
    db_transporte.estado = "Inactivo"
    
    session.add(db_transporte)
    session.commit()
    session.refresh(db_transporte)
    
    return db_transporte
    
#  --- GET: OBTENER TRANSPORTE POR EMPRESA ---
@router.get("/empresa/{nombre_empresa}")
def filtrar_transporte_por_empresa(
    nombre_empresa: str,
    session: Session = Depends(get_db)
):
    statement = select(Transporte).where(Transporte.empresa.contains(nombre_empresa))
    transportes = session.exec(statement).all()
    
    if not transportes:
        raise HTTPException(status_code=404, datail="No se encontraron transportes para esta empresa")
    
    return transportes

# --- GET: OBTENER EL TRANSPORTE ASOCIADO A UN PAQUETE ---
@router.get("/paquete/{paquete_nombre}")
def filtrar_transporte_por_paquete(
    paquete_nombre: str,
    session: Session = Depends(get_db)
):
    paquete = session.exec(
        select(PaqueteTuristico).where(PaqueteTuristico.nombre.contains(paquete_nombre))).first()

    if not paquete or not paquete.transporte:
        raise HTTPException(status_code=404, detail="No se encontró transporte para este paquete")

    return paquete.transporte

# --- GET: FILTRAR TRANSPORTES POR CAPACIDAD MÍNIMA ---
@router.get("/capacidad/{min_capacidad}")
def filtrar_transportes_por_capacidad(
    min_capacidad: int,
    session: Session = Depends(get_db)
):
    # Buscamos transportes donde la capacidad sea mayor o igual al valor recibido
    statement = select(Transporte).where(Transporte.capacidad >= min_capacidad)
    transportes = session.exec(statement).all()
    
    if not transportes:
        raise HTTPException(
            status_code=404, 
            detail=f"No hay transportes con capacidad para {min_capacidad} personas"
        )
    
    return transportes

# --- GET: OBTENER TRANSPORTES ACTIVOS ---
@router.get("/disponibles")
def obtener_transportes_disponibles(
    session: Session = Depends(get_db)
):
    statement = select(Transporte).where(Transporte.estado.contains("Activo"))
    transportes = session.exec(statement).all()
    
    return transportes