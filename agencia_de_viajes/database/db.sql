CREATE TABLE cliente (
    id SERIAL PRIMARY KEY
    nombre VARCHAR (50),
	pasaporte VARCHAR (50),
	telefono VARCHAR (50),
	corre VARCHAR (50)
);

CREATE TABLE paqueteTuristico(
	id SERIAL PRIMARY KEY,
	nombre VARCHAR (50),
	descripcion VARCHAR(100),
	duracion INT
	precio NUMERIC (10 , 2),
	cupo INT,
	estado VARCHAR(50),
);

CREATE TABLE destino(
	id SERIAL PRIMARY KEY,
	ciudad VARCHAR(50),
	pais VARCHAR(50),
	descripcion VARCHAR(50),
	clima VARCHAR(50),
    observaciones VARCHAR(50)
);

CREATE TABLE Reserva(
    id SERIAL PRIMARY KEY,
    fecha DATE,
    cantidad_personas INT,
    estado VARCHAR(50),
    monto NUMERIC(10, 2),
    comentarios VARCHAR(50)
);

CREATE TABLE Pago(
    id SERIAL PRIMARY KEY,
    fecha DATE,
    monto NUMERIC(10, 2),
    método_pago VARCHAR(50),
    estado VARCHAR(50)
);

CREATE TABLE PersonaGuia(
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50),
    idiomas VARCHAR(50),
    experiencia VARCHAR(50),
    disponibilidad date
);

CREATE TABLE Transporte(
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(50),
    empresa VARCHAR(50),
    capacidad VARCHAR(50)
);

CREATE TABLE Hotel
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50),
    categoria VARCHAR(50),
    direccion VARCHAR(50),
    contactoVARCHAR(50);