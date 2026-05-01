from fastapi import APIRouter, Depends, HTTPException
from esquemas.schemas import ClienteCreate, clienteUpdate
from sqlmodel import Session, select
from database.conexion import get_db
from modelos.models import Cliente, Guia, Reserva

# Definición del router para agrupar las rutas de 'Clientes' en la documentación (Swagger)
router = APIRouter(prefix="/clientes", tags=["Clientes"])


# --- POST: CREAR UN NUEVO CLIENTE ---
@router.post("/")
def crear_cliente(
    cliente_data: ClienteCreate, # Recibe los datos validados por el esquema Pydantic
    session: Session = Depends(get_db)
    ):
    # Instanciamos el modelo Cliente con los datos recibidos
    NuevoCliente = Cliente(
        nombre = cliente_data.nombre,
        documento = cliente_data.documento,
        telefono = cliente_data.telefono,
        correo = cliente_data.correo
    )
    session.add(NuevoCliente)     # Preparamos la inserción
    session.commit()              # Guardamos los cambios en la DB
    session.refresh(NuevoCliente) # Refrescamos para obtener el ID generado automáticamente
    return NuevoCliente

# --- GET: OBTENER TODOS LOS CLIENTES ---
@router.get("/mostrar")
def mostrar_clientes(
    session: Session = Depends(get_db)):
    # Se crea la sentencia SQL: SELECT * FROM cliente
    statement = select(Cliente)
    # Ejecutamos la sentencia y convertimos los resultados en una lista
    clientes = session.exec(statement).all()
    return clientes

# --- GET: OBTENER UN CLIENTE POR ID ---
@router.get("/mostrar/{cliente_id}")
def mostrar_cliente_id(
    cliente_id: int, 
    session: Session = Depends(get_db)):
    # session.get busca directamente por la llave primaria
    cliente = session.get(Cliente, cliente_id)
    # Si no existe, lanzamos un error 404 (Not Found)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente not found")
    
    return cliente

# --- GET: CLIENTES ACTIVOS ---
@router.get("/activas/")
def mostrar_clientes_activos(
    session: Session = Depends(get_db)
):
    statement = select(Cliente).where(Cliente.estado == True)
    cliente = session.exec(statement).all()
    
    return cliente

# --- POST BULK: CREAR MUCHOS NUEVOS CLIENTES ---
@router.post("/bulk")
def crear_clientes_masivo(
    lista_data: list[ClienteCreate],
    session: Session = Depends(get_db)
):
    nuevos_clientes = [

        Cliente(
            **cliente.model_dump()
        )
        for cliente in lista_data
]    
    session.add_all(nuevos_clientes)
    session.commit()

    for cliente in nuevos_clientes:
        session.refresh(cliente)

    return nuevos_clientes

# --- PUT: ACTUALIZACIÓN TOTAL ---
@router.put("/{cliente_id}")
def actualizacion_completa(
    cliente_id: int,
    cliente_data: clienteUpdate,
    session: Session = Depends(get_db)
):
    # 1. Buscamos el registro actual
    db_cliente = session.get(Cliente, cliente_id)
    if not db_cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    # 2. Convertimos el esquema a diccionario excluyendo campos no enviados
    datos_nuevos = cliente_data.model_dump(exclude_unset=True)

    # 3. Ciclo dinámico para actualizar los atributos del objeto
    for llave, valor in datos_nuevos.items():
        setattr(db_cliente, llave, valor)

    session.add(db_cliente)
    session.commit()
    session.refresh(db_cliente)
    return db_cliente

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

    # model_dump(exclude_unset=True) para: evita sobreescribir con valores nulos
    datos_actualizar = cliente_data.model_dump(exclude_unset=True)

    for llave, valor in datos_actualizar.items():
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

    # No borramos el registro físicamente, solo lo desactivamos
    db_cliente.is_active = False

    session.add(db_cliente)
    session.commit()
    session.refresh(db_cliente)
    return db_cliente

# --- GET: RESERVAS ASOCIADAS A UN CLIENTE ---
@router.get("/reservas/{cliente_id}")
def mostrar_reservas_de_cliente(
    cliente_id: int,
    session: Session = Depends(get_db)
):
    # Filtramos la tabla Reserva usando la llave foránea cliente_id
    statement = select(Reserva).where(Reserva.cliente_id == cliente_id)
    reservas = session.exec(statement).all()

    if not reservas:
        raise HTTPException(status_code=404, detail="No se encontraron reservas para este cliente")

    return reservas

# --- GET: SELECCION DE CLIENTE POR SU DOCUMENTO Y RESPUESTA DE ESTADOS DE RESERVA  ---
@router.get("/mostrar/{documento}")
def filtrar_clientes_por_documento(
    documento: str, 
    session: Session = Depends(get_db)
):
    # Usamos select para buscar por un campo que no es la llave primaria
    statement = select(Cliente).where(Cliente.documento == documento)
    cliente = session.exec(statement).first() # first() devuelve el primer resultado o None
    
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente not found")
    
    info_cliente = {
        "nombre": cliente.nombre,
        "documento": cliente.documento,
        "telefono": cliente.telefono,
        "correo": cliente.correo,
        "fechas de reservas": [reserva.fecha for reserva in cliente.reservas],# Lista de IDs de reservas asociadas
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

    # Calculamos datos interesantes
    total_invertido = sum(r.monto_total for r in cliente.reservas)
    
    # Obtenemos los nombres de los paquetes (sin repetir)
    nombres_paquetes = list(set(r.paquete.nombre for r in cliente.reservas))

    return {
        "cliente": cliente.nombre,
        "documento": cliente.documento,
        "cantidad_viajes": len(cliente.reservas),
        "total_gastado": total_invertido,
        "paquetes_disfrutados": nombres_paquetes
    }