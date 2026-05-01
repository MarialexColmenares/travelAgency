from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database.conexion import get_db
from modelos.models import Destino
from esquemas.schemas import CreateDestino, UpdateDestino

router = APIRouter(prefix="/destinos", tags=["Destinos"])


# --- POST: CREAR UN NUEVO DESTINO ---
@router.post("/crear")
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

# --- GET: OBTENER TODOS LOS DESTINOS ---
@router.get("/mostrar")
def mostrar_destinos(
    session : Session = Depends(get_db) ):

    statement = select(Destino)
    destinos = session.exec(statement).all()

    return destinos

# --- GET: OBTENER UN DESTINO POR ID ---
@router.get("/mostrar{id_destino}")
def mostrar_destino_id(
    id_destino: int,
    session: Session = Depends(get_db)
):
    destino = session.get(Destino, id_destino)

    if not destino:
        raise HTTPException(status_code=404, detail="Transportes not found")

    return destino

# --- GET: OBTENER DESTINOS ACTIVOS ---
@router.get("/activos")
def mostrar_destinos_activos(
    session: Session = Depends(get_db)
):
    statement = select(Destino).where(Destino.estado == True)
    destinos = session.exec(statement).all()

    return destinos

# --- POST BULK: CREAR MUCHOS NUEVOS DESTINOS ---
@router.post("/bulk")
def crear_destinos_masivo(
    lista_data: list[CreateDestino],
    session: Session = Depends(get_db)
):
    nuevos_destinos = [

        Destino(
            **destino.model_dump()
        )
        for destino in lista_data
]    
    session.add_all(nuevos_destinos)
    session.commit()

    for destino in nuevos_destinos:
        session.refresh(destino)

    return nuevos_destinos

# --- PATCH: ACTUALIZACIÓN PARCIAL ---
@router.patch("/actualizar/{id_destino}")
def actualizar_destino_parcial(
    id_destino: int,
    data: UpdateDestino,
    session: Session = Depends(get_db)
):
    db_destino = session.get(Destino, id_destino)

    if not db_destino:
        raise HTTPException(status_code=404, detail="Destino no encontrado")

    datos_nuevos = data.model_dump(exclude_unset=True)


    for llave, valor in datos_nuevos.items():
        setattr(db_destino, llave, valor)

    session.add(db_destino)
    session.commit()
    session.refresh(db_destino)

    return db_destino

# --- DELETE: ELIMINACION LOGICA ---
@router.delete("/desactivar/{id_destino}")
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
    
    return {"message": f"Destino con id {id_destino} ha sido eliminado"}

# -- GET: OBTENER DESTINOS FILLTRADOS POR NOMBRE---
@router.get("/nombre/{nombre}")
def filtrar_destinos_por_nombre(
    nombre: str,
    session: Session = Depends(get_db)
):
    statement = select(Destino).where(Destino.ciudad.contains(nombre))
    destinos = session.exec(statement).all()
    
    return destinos

# --- GET: OBTENER UN DESTINOS FILTRADOS POR CIUDAD Y PAIS --- 
@router.get("/ciudad-pais")
def filter_destinox_por_ciudad_y_pais(
    ciudad: str,
    pais: str,
    session: Session = Depends(get_db)
):
    destino = session.exec(select(Destino).where(Destino.ciudad == ciudad, Destino.pais == pais)).all()
    return destino

# --- GET: FILTRAR DESTINOS POR PAIS ---
@router.get("/pais/{pais}")
def filtrar_destinos_por_pais(
    pais: str,
    session: Session = Depends(get_db)
):
    statement = select(Destino).where(Destino.pais.contains(pais))
    destinos = session.exec(statement).all()
    
    return destinos

# --- GET: FILTRAR DESTINOS POR CLIMA ---
@router.get("/clima/{clima}")
def filtrar_destinos_por_clima(
    clima: str,
    session: Session = Depends(get_db)
):
    statement = select(Destino).where(Destino.clima.contains(clima))
    destinos = session.exec(statement).all()
    
    return destinos

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

# --- GET: OBTENER DESTINOS DE UN PAQUETE ESPECIFICO ---
@router.get("/paquete/{id_paquete}")
def obtener_destinos_por_paquete(
    id_paquete: int,
    session: Session = Depends(get_db)
):
    statement = select(Destino).where(Destino.paquetes.any(id=id_paquete))
    destinos = session.exec(statement).all()
    
    return destinos

