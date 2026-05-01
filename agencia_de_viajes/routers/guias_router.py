from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database.conexion import get_db
from esquemas.schemas import GuiaCreate, GuiaUpdate
from modelos.models import Guia

router = APIRouter(prefix="/guias", tags=["Guias"])

# --- POST: CREAR UN NUEVO GUIA ---
@router.post("")
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

# --- GET: OBTENER TODOS LOS GUIAS ---
@router.get("/mostrar")
def mostrar_guias(
    session: Session = Depends(get_db)):

    statement = select(Guia)
    guias = session.exec(statement).all()

    return guias

# --- GET: OBTENER UN GUIA POR ID ---
@router.get("/mostrar{id_guia}")
def mostrar_guia_id(
    id_guia: int, 
    session: Session = Depends(get_db)):
    guia = session.get(Guia, id_guia)

    if not guia:

        raise HTTPException(status_code=404, detail="guia not found")

    return guia

#  --- GET: OBTENER GUIAS ACTIVOS ---
@router.get("/activos")
def mostrar_guias_activos(
    session: Session = Depends(get_db)
):
    statement = select(Guia).where(Guia.estado == True)
    guias = session.exec(statement).all()
    
    return guias

# --- POST BULK: CREAR MUCHOS NUEVO GUIAS ---
@router.post("/bulk")
def crear_guias_masivo(
    lista_data: list[GuiaCreate],
    session: Session = Depends(get_db)
):
    
    nuevos_guias = [Guia(**guia.model_dump()) for guia in lista_data]
    
    session.add_all(nuevos_guias)
    session.commit()
    
    for guia in nuevos_guias:
        session.refresh(guia)

    return nuevos_guias

# --- PATCH: ACTUALIZACIÓN PARCIAL ---
@router.patch("/{id_guia}")
def actualizar_guia_parcial(
    id_guia: int,
    data: GuiaUpdate,
    session: Session = Depends(get_db)
):
    db_guia = session.get(Guia, id_guia)

    if not db_guia:
        raise HTTPException(status_code=404, detail="Guia no encontrado")

    datos_nuevos = data.model_dump(exclude_unset=True)

    for llave, valor in datos_nuevos.items():
        setattr(db_guia, llave, valor)

    session.add(db_guia)
    session.commit()
    session.refresh(db_guia)

    return db_guia

# --- DELETE: ELIMINACION LOGICA ---
@router.delete("/desactivar/{id_guia}")
def eliminar_guia(
    id_guia: int,
    session: Session = Depends(get_db)
):
    db_guia = session.get(Guia, id_guia)

    if not db_guia:
        raise HTTPException(status_code=404, detail="Guia no encontrado")

    db_guia.estado = "Inactivo"

    session.add(db_guia)
    session.commit()
    session.refresh(db_guia)

    return db_guia

# --- GET: OBTENER UN GUIAS FILTRADOS POR NOMBRE ---
@router.get("/filter/{nombre}")
def filtrar_guias_por_nombre(
    nombre: str,
    session: Session = Depends(get_db)
):
    statement = select(Guia).where(Guia.nombre.contains(nombre))
    guias = session.exec(statement).all()

    return guias

# --- GET: FILTRO POR AÑOS DE EXPERIENCIA ---
@router.get("/experiencia/{anios}")
def filtrar_guias_por_experiencia(
    anios: int,
    session: Session = Depends(get_db)
):
    statement = select(Guia).where(Guia.anios_experiencia >= anios)
    guias = session.exec(statement).all()

    return guias

# --- GET: FILTRO GUIAS POR IDIOMA ---
@router.get("/idioma/{idioma}")
def filtrar_guias_por_idioma(
    idioma: str,
    session: Session = Depends (get_db)
):
    statement = select(Guia).where(Guia.idiomas.contains(idioma))
    guias = session.exec(statement).all()
    
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
        resultado.append({
            "guia": guia.nombre,
            "paquetes": [paquete.nombre for paquete in guia.paquetes]
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
            # Una lógica simple para saber si está muy ocupado
            "nivel_prioridad": "Alta" if cantidad_paquetes > 3 else "Normal"
        })
        
    # Ordenamos de mayor a menor carga para que el usuario vea quién trabaja más
    reporte_carga.sort(key=lambda x: x["total_paquetes"], reverse=True)    
    
    return reporte_carga