from fastapi import APIRouter, Depends, HTTPException
from schemas.esquemas import ClienteCreate, clienteUpdate
from sqlmodel import Session, select
from database.conexion import get_db
from models.modelos import Cliente, Guia, Reserva

router = APIRouter(prefix="/clientes", tags=["Clientes"])

# --- GET: OBTENER TODOS LOS CLIENTES ---
@router.get("/")
def mostrar_clientes(
    session: Session = Depends(get_db)
):
    statement = select(Cliente)
    clientes = session.exec(statement).all()

    if not clientes:
        raise HTTPException(
            status_code=404, 
            detail="No se Encontraron Clientes"
        )
    return clientes

# --- POST: CREAR UN NUEVO CLIENTE ---
@router.post("/")
def crear_cliente(
    cliente_data: ClienteCreate, 
    session: Session = Depends(get_db)
):
    NuevoCliente = Cliente(
        nombre = cliente_data.nombre,
        documento = cliente_data.documento,
        telefono = cliente_data.telefono,
        correo = cliente_data.correo
    )

    session.add(NuevoCliente)
    session.commit()
    session.refresh(NuevoCliente)

    return NuevoCliente

# --- POST BULK: CREAR MUCHOS NUEVOS CLIENTES ---
@router.post("/bulk")
def crear_clientes_masivo(
    lista_data: list[ClienteCreate],
    session: Session = Depends(get_db)
):
    nuevos_clientes = [
        Cliente(
            **cliente.model_dump()
        ) for cliente in lista_data
        ]
    
    session.add_all(nuevos_clientes)
    session.commit()

    for cliente in nuevos_clientes:
        session.refresh(cliente)

    return nuevos_clientes

# --- GET: CLIENTES ACTIVOS ---
@router.get("/activos/")
def mostrar_clientes_activos(
    session: Session = Depends(get_db)
):
    statement = select(Cliente).where(Cliente.is_active == True)
    clientes = session.exec(statement).all()
    
    if not clientes:
        raise HTTPException(
            status_code= 404,
            detail="No se Encontraron clientes Activos"
        )
    return clientes

# --- GET: RESERVAS ASOCIADAS A UN CLIENTE ---
@router.get("/{cliente_id}/reservas")
def mostrar_reservas_de_cliente(
    cliente_id: int,
    session: Session = Depends(get_db)
):
    statement = select(Reserva).where(Reserva.cliente_id == cliente_id)
    reservas = session.exec(statement).all()

    if not reservas:
        raise HTTPException(status_code=404, detail="No se encontraron reservas para este cliente")

    return reservas

# --- GET: SELECCION DE CLIENTE POR SU DOCUMENTO Y RESPUESTA DE ESTADOS DE RESERVA  ---
@router.get("/{documento}")
def filtrar_clientes_por_documento(
    documento: str, 
    session: Session = Depends(get_db)
):
    statement = select(Cliente).where(Cliente.documento == documento)
    cliente = session.exec(statement).first()
    
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente not found")
    
    info_cliente = {
        "nombre": cliente.nombre,
        "documento": cliente.documento,
        "telefono": cliente.telefono,
        "correo": cliente.correo,
        "fechas de reservas": [reserva.fecha for reserva in cliente.reservas],
        "estado de reservas": [reserva.estado for reserva in cliente.reservas]
    }
    return info_cliente

# --- GET: RESUMEN DE VIAJERO ---
@router.get("/{cliente_id}/resumen")
def obtener_resumen_viajero(
    cliente_id: int,
    session: Session = Depends(get_db)
):
    cliente = session.get(Cliente, cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    total_invertido = sum(r.monto_total for r in cliente.reservas)
    nombres_paquetes = list(set(r.paquete.nombre for r in cliente.reservas))
    
    if nombres_paquetes == []:
        raise HTTPException(
            status_code=404,
            detail=f"no se encontraron paquetes para el cliente {cliente.nombre}"
        )
    
    return {
        "cliente": cliente.nombre,
        "documento": cliente.documento,
        "cantidad_viajes": len(cliente.reservas),
        "total_gastado": total_invertido,
        "paquetes_disfrutados": nombres_paquetes
         
    }
    
# --- GET: OBTENER UN CLIENTE POR ID ---
@router.get("/{cliente_id}")
def mostrar_cliente_id(
    cliente_id: int, 
    session: Session = Depends(get_db)
):
    cliente = session.get(Cliente, cliente_id)
    
    if not cliente:
        raise HTTPException(
            status_code=404, 
            detail="Cliente no Encontrado"
        )
    
    return cliente

# --- PATCH: ACTUALIZACIÓN PARCIAL ---
@router.patch("/{cliente_id}")
def actualizacion_parcial(
    cliente_id: int,
    cliente_data: clienteUpdate,
    session: Session = Depends(get_db)
):
    db_cliente = session.get(Cliente, cliente_id)
    if not db_cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    datos_actualizar = cliente_data.model_dump(exclude_unset=True)

    for llave, valor in datos_actualizar.items():
        setattr(db_cliente, llave, valor)

    session.add(db_cliente)
    session.commit()
    session.refresh(db_cliente)
    return db_cliente

# --- PUT: ACTUALIZACIÓN TOTAL ---
@router.put("/{cliente_id}")
def actualizacion_completa(
    cliente_id: int,
    cliente_data: clienteUpdate,
    session: Session = Depends(get_db)
):
    db_cliente = session.get(Cliente, cliente_id)
    if not db_cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    datos_nuevos = cliente_data.model_dump(exclude_unset=True)

    for llave, valor in datos_nuevos.items():
        setattr(db_cliente, llave, valor)

    session.add(db_cliente)
    session.commit()
    session.refresh(db_cliente)

    return db_cliente

# --- DELETE: ELIMINACIÓN LÓGICA ---
@router.delete("/{cliente_id}")
def eliminacion_logica(
    cliente_id: int,
    session: Session = Depends(get_db)
):
    db_cliente = session.get(Cliente, cliente_id)
    if not db_cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    db_cliente.is_active = False

    session.add(db_cliente)
    session.commit()
    session.refresh(db_cliente)
    return db_cliente
