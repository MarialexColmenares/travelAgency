from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database.conexion import get_db
from schemas.esquemas import GuiaCreate, GuiaUpdate, GuiaUpdateParcial
from models.modelos import Guia
from typing import Optional

router = APIRouter(prefix="/guias", tags=["Guias"])


# --- POST: CREAR UN NUEVO GUIA ---
@router.post("/")
def crear_guia(
    data: GuiaCreate,
    session: Session = Depends(get_db)
):
    nuevo_guia = Guia(
        **data.model_dump()
    )

    session.add(nuevo_guia)
    session.commit()
    session.refresh(nuevo_guia)

    return nuevo_guia

# --- POST BULK: CREAR MUCHOS NUEVO GUIAS ---
@router.post("/bulk")
def crear_guias_masivo(
    lista_data: list[GuiaCreate],
    session: Session = Depends(get_db)
):
    
    nuevos_guias = [
        Guia(
            **guia.model_dump()
            ) for guia in lista_data
        ]
    
    session.add_all(nuevos_guias)
    session.commit()
    
    for guia in nuevos_guias:
        session.refresh(guia)

    return nuevos_guias

# --- GET: OBTENER TODOS LOS GUIAS ---
@router.get("/")
def mostrar_guias(
    session: Session = Depends(get_db)
):
    statement = select(Guia)
    guias = session.exec(statement).all()

    if not guias:
        raise HTTPException(
            status_code=404,
            detail="No se Encontraron Guias"
        )
    
    return guias

#  --- GET: OBTENER GUIAS ACTIVOS ---
@router.get("/disponibles")
def mostrar_guias_Disponibles(
    session: Session = Depends(get_db)
):
    statement = select(Guia).where(Guia.estado == "Disponible") # Aqui no sabia si hacerlo boolean o varchar 
    guias = session.exec(statement).all()
    
    if not guias:
        raise HTTPException(
            status_code=404,
            detail="No se Encontraron Guias Disponibles"
        )
    
    return guias

# --- GET: OBTENER UN GUIAS FILTRADOS POR NOMBRE ---
@router.get("/filtros")
def filtros(
    nombre:  Optional[str] = None,
    experiencia:  Optional[int] = None,
    idiomas: Optional[str] = None,
    estado: Optional[str] = None,
    session: Session = Depends(get_db)
):
    if nombre:
        statement = select(Guia).where(Guia.nombre.ilike(f"%{nombre}%"))
    if experiencia:
        statement = select(Guia).where(Guia.experiencia >= experiencia)
    if idiomas:
        statement = select(Guia).where(Guia.idiomas.ilike(f"%{idiomas}%"))
    if estado:
        statement = select(Guia).where(Guia.estado.ilike(f"%{estado}%"))
        
    guias = session.exec(statement).all()
    
    if not guias:
        raise HTTPException(
            status_code=404,
            detail="No se Encontraron Guias"
        )

    return guias

#  --- GET: OBTENER GUIAS CON SUS PAQUETES ASOCIADOS ---
@router.get("/con-paquetes/")
def mostrar_guias_con_paquetes(
    session: Session = Depends(get_db)
):
    statement = select(Guia)
    guias = session.exec(statement).all()
    
    resultado = []
    
    for guia in guias:
        
        nombres_paquetes = [paquete.nombre for paquete in guia.paquetes]
        
        if nombres_paquetes:
            contenido_paquetes = nombres_paquetes
        else:
            contenido_paquetes = "Sin paquetes"

        resultado.append({
            "guia": guia.nombre,
            "paquetes": contenido_paquetes
        })
    
   
    
    return resultado

# --- GET: CARGA LABORAL DE LOS GUIAS ---
@router.get("/carga-laboral")
def obtener_carga_laboral_guias(
    session: Session = Depends(get_db)
):
    statement = select(Guia)
    guias = session.exec(statement).all()
    
    reporte_carga= []
    
    for guia in guias:
        cantidad_paquetes = len(guia.paquetes)
        
        reporte_carga.append({
            "guia_id": guia.id,
            "nombre": guia.nombre,
            "total_paquetes": cantidad_paquetes,
            "estado_actual": guia.estado,
            "nivel_prioridad": "Alta" if cantidad_paquetes > 3 else "Normal"
        })
        
    # Ordenamos de mayor a menor carga para que el usuario vea quién trabaja más
    reporte_carga.sort(key=lambda x: x["total_paquetes"], reverse=True)    
    
    return reporte_carga

# --- GET: OBTENER UN GUIA POR ID ---
@router.get("/{id_guia}")
def mostrar_guia_id(
    id_guia: int, 
    session: Session = Depends(get_db)
):
    guia = session.get(Guia, id_guia)
    
    if not guia:
        raise HTTPException(
            status_code=404, 
            detail="No se Encontro Ningun Guia con ese ID"
        )
    return guia

# --- PATCH: ACTUALIZACIÓN PARCIAL ---
@router.patch("/{id_guia}")
def actualizar_guia_parcial(
    id_guia: int,
    data: GuiaUpdateParcial,
    session: Session = Depends(get_db)
):
    db_guia = session.get(Guia, id_guia)

    if not db_guia:
        raise HTTPException(
            status_code=404, 
            detail="Guia no encontrado"
        )

    datos_nuevos = data.model_dump(exclude_unset=True)

    for llave, valor in datos_nuevos.items():
        setattr(db_guia, llave, valor)

    session.add(db_guia)
    session.commit()
    session.refresh(db_guia)

    return db_guia

# --- PUT: ACTUALIZACIÓN TOTAL ---
@router.put("/{id_guia}")
def actualizacion_completa(
    id: int,
    data: GuiaUpdate,
    session: Session = Depends(get_db)
):
    db_guia = session.get(Guia, id)
    if not db_guia:
        raise HTTPException(
            status_code=404, 
            detail="Guia no encontrado"
        )

    datos_nuevos = data.model_dump(exclude_unset=True)

    for llave, valor in datos_nuevos.items():
        setattr(db_guia, llave, valor)

    session.add(db_guia)
    session.commit()
    session.refresh(db_guia)
    
    return db_guia

# --- DELETE: ELIMINACION LOGICA ---
@router.delete("/{id_guia}")
def eliminar_guia(
    id_guia: int,
    session: Session = Depends(get_db)
):
    db_guia = session.get(Guia, id_guia)

    if not db_guia:
        raise HTTPException(
            status_code=404, 
            detail="Guia no encontrado"
        )

    db_guia.estado = "Inactivo"

    session.add(db_guia)
    session.commit()
    session.refresh(db_guia)

    return db_guia

