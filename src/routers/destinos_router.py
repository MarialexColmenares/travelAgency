from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database.conexion import get_db
from models.modelos import Destino
from schemas.esquemas import CreateDestino, UpdateDestino, UpdateDestinoParcial
from typing import Optional, List

router = APIRouter(prefix="/destinos", tags=["Destinos"])


# --- POST: CREAR UN NUEVO DESTINO ---
@router.post("/")
def crear_destino(
    data : CreateDestino,
    session : Session = Depends(get_db)
):
    nuevo_destino = Destino(
        **data.model_dump()
    )
    
    session.add(nuevo_destino)
    session.commit()
    session.refresh(nuevo_destino)

    return nuevo_destino

# --- POST BULK: CREAR MUCHOS NUEVOS DESTINOS ---
@router.post("/bulk")
def crear_destinos_masivo(
    lista_data: List[CreateDestino],
    session: Session = Depends(get_db)
):
    nuevos_destinos = [
        Destino(
            **destino.model_dump()
        ) for destino in lista_data
    ]    
    
    session.add_all(nuevos_destinos)
    session.commit()

    for destino in nuevos_destinos:
        session.refresh(destino)

    return nuevos_destinos

# --- GET: OBTENER TODOS LOS DESTINOS ---
@router.get("/")
def mostrar_destinos(
    session : Session = Depends(get_db) 
):
    statement = select(Destino)
    destinos = session.exec(statement).all()
    
    if not destinos:
        raise HTTPException(
            status_code=404, 
            detail="No se encontraron registros de destinos"
        )

    return destinos

# --- GET: OBTENER DESTINOS ACTIVOS ---
@router.get("/activos")
def mostrar_destinos_activos(
    session: Session = Depends(get_db)
):
    statement = select(Destino).where(Destino.estado == True)
    destinos = session.exec(statement).all()

    return destinos

# --- GET: FILTRAR DESTINOS ---
@router.get("/filtros")
def filtros(
    ciudad: Optional[str] = None,
    pais: Optional[str] = None,
    descripcion: Optional[str] = None,
    clima: Optional[str] = None,
    
    session: Session = Depends(get_db)
):
    
    statement = select(Destino).where(
        Destino.estado == True)
    
    if ciudad:
        statement = statement.where(Destino.ciudad.ilike(f"%{ciudad}%"))
    if pais:
        statement = statement.where(Destino.pais.ilike(f"%{pais}%"))
    if descripcion:
        statement = statement.where(Destino.descripcion.ilike(f"%{descripcion}%"))
    if clima:
        statement = statement.where(Destino.clima.ilike(f"%{clima}%"))
        
    destinos_filtrados = session.exec(statement).all()
    
    if not destinos_filtrados:
        raise HTTPException(
            status_code=404,
            detail="No se Encontraron Destinos"
        )
    
    return destinos_filtrados

#  --- GET:OBTENER TODOS LOS DESTINOS CON SUS PAQUETES ASOCIADOS ---
@router.get("/con-paquetes/")
def mostrar_destinos_con_paquetes(
    session: Session = Depends(get_db)
):
    statement = select(Destino)
    destinos = session.exec(statement).all()
    
    resultado = []
    
    for destino in destinos:
        resultado.append({
            "destino": destino.ciudad,
            "pais": destino.pais,
            "paquetes_asociados": [p.nombre for p in destino.paquetes]
        })
        
    session.commit()
    
    return resultado

# --- GET: OBTENER UN DESTINO POR ID ---
@router.get("/{id_destino}")
def mostrar_destino_id(
    id_destino: int,
    session: Session = Depends(get_db)
):
    destino = session.get(Destino, id_destino)

    if not destino:
        raise HTTPException(
            status_code=404, 
            detail="No se Encontro Ningun Destino con ese ID"
        )

    return destino

# --- PATCH: ACTUALIZACIÓN PARCIAL ---
@router.patch("/{id_destino}")
def actualizar_destino_parcial(
    id_destino: int,
    data: UpdateDestinoParcial,
    session: Session = Depends(get_db)
):
    db_destino = session.get(Destino, id_destino)

    if not db_destino:
        raise HTTPException(
            status_code=404, 
            detail="Destino no encontrado"
        )

    datos_nuevos = data.model_dump(exclude_unset=True)

    for llave, valor in datos_nuevos.items():
        setattr(db_destino, llave, valor)

    session.add(db_destino)
    session.commit()
    session.refresh(db_destino)

    return db_destino

# --- PUT: ACTUALIZACIÓN TOTAL ---
@router.put("/{id_destino}")
def actualizacion_completa(
    id: int,
    data: UpdateDestino,
    session: Session = Depends(get_db)
):
    db_destino = session.get(Destino, id )
    if not db_destino:
        raise HTTPException(
            status_code=404, 
            detail="Destino no encontrado"
        )

    datos_nuevos = data.model_dump(exclude_unset=True)

    for llave, valor in datos_nuevos.items():
        setattr(db_destino, llave, valor)

    session.add(db_destino)
    session.commit()
    session.refresh(db_destino)
    
    return db_destino

# --- DELETE: ELIMINACION LOGICA ---
@router.delete("/{id_destino}")
def eliminar_destino(
    id_destino: int,
    session: Session = Depends(get_db)
):
    db_destino = session.get(Destino, id_destino)
    
    if not db_destino:
        raise HTTPException(status_code=404, detail="Destino no encontrado")
    
    db_destino.estado = False
    
    session.add(db_destino)
    session.commit()
    session.refresh(db_destino)
    
    return {"message": f"Destino {db_destino.ciudad} ha sido eliminado"}
