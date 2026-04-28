from fastapi import APIRouter, Depends, HTTPException
from schemas import ClienteCreate, clienteUpdate
from sqlmodel import Session, select
from conexion import get_db
from models import Cliente, Guia, Reserva

# Definición del router para agrupar las rutas de 'Clientes' en la documentación (Swagger)
router = APIRouter(prefix="/clientes", tags=["Clientes"])

# --- GET: OBTENER TODOS LOS CLIENTES ---
@router.get("/")
def leer_clientes(session: Session = Depends(get_db)):
    # Se crea la sentencia SQL: SELECT * FROM cliente
    statement = select(Cliente)
    # Ejecutamos la sentencia y convertimos los resultados en una lista
    clientes = session.exec(statement).all()
    return clientes

# --- GET: OBTENER UN CLIENTE POR ID ---
@router.get("/id{cliente_id}")
def get_id_cliente(cliente_id: int, session: Session = Depends(get_db)):
    # session.get busca directamente por la llave primaria
    cliente = session.get(Cliente, cliente_id)
    # Si no existe, lanzamos un error 404 (Not Found)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente not found")
    return cliente

# --- POST: CREAR UN NUEVO CLIENTE ---
@router.post("/")
def crearCliente(
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

# --- POST BULK: CREAR MUCHOS NUEVOS CLIENTES ---
@router.post("/bulk") # Sugiero llamarlo /bulk para diferenciarlo del individual
def crear_CLIENTES_masivo(
    lista_data: list[ClienteCreate],
    session: Session = Depends(get_db)
):
    # Convertimos la lista de esquemas a lista de modelos de BD
    nuevos_clientes = [Cliente(**cliente.model_dump()) for cliente in lista_data]
    
    # IMPORTANTE: Usar add_all para listas
    session.add_all(nuevos_clientes)
    session.commit()
    
    # Refrescamos cada uno para obtener su ID generado
    for cliente in nuevos_clientes:
        session.refresh(cliente)

    return nuevos_clientes


# --- PUT: ACTUALIZACIÓN TOTAL ---
@router.put("/{cliente_id}")
def actualizar_cliente(
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
def actualizar_parcial_cliente(
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
def eliminacion_logica_cliente(
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
def leer_reservas_por_cliente(
    cliente_id: int,
    session: Session = Depends(get_db)
):
    # Filtramos la tabla Reserva usando la llave foránea cliente_id
    statement = select(Reserva).where(Reserva.cliente_id == cliente_id)
    reservas = session.exec(statement).all()

    if not reservas:
        raise HTTPException(status_code=404, detail="No se encontraron reservas para este cliente")

    return reservas
