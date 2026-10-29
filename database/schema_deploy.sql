-- ============================================================
-- TechTrack SATE - Esquema completo de base de datos
-- Motor: MySQL 8+
-- Codificación: utf8mb4
--
-- Uso:
--   mysql -u root -p < database/schema.sql
--   mysql -u root -p < database/seed.sql
-- ============================================================

-- Version para hosting: la base ya existe y se selecciona al conectarse.
-- Importar con: mysql -h HOST -u USUARIO -p BASE < database/schema_deploy.sql

-- Se desactivan temporalmente las FK para poder recrear en orden.
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS auditoria;
DROP TABLE IF EXISTS historial_activos;
DROP TABLE IF EXISTS incidencias;
DROP TABLE IF EXISTS mantenimientos;
DROP TABLE IF EXISTS cambios;
DROP TABLE IF EXISTS problemas;
DROP TABLE IF EXISTS postulaciones;
DROP TABLE IF EXISTS mensajes_contacto;
DROP TABLE IF EXISTS proveedores;
DROP TABLE IF EXISTS activos;
DROP TABLE IF EXISTS usuarios;
DROP TABLE IF EXISTS roles;
DROP TABLE IF EXISTS departamentos;

SET FOREIGN_KEY_CHECKS = 1;

-- ------------------------------------------------------------
-- Catálogos base
-- ------------------------------------------------------------
CREATE TABLE departamentos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE
) ENGINE=InnoDB;

CREATE TABLE roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Usuarios del sistema
-- La contraseña SIEMPRE debe guardarse hasheada con Werkzeug.
-- ------------------------------------------------------------
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    departamento_id INT NULL,
    rol_id INT NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    tema VARCHAR(20) NOT NULL DEFAULT 'blue',
    debe_cambiar_password BOOLEAN NOT NULL DEFAULT FALSE,
    ultimo_acceso DATETIME NULL,
    fecha_registro TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_usuarios_departamento
        FOREIGN KEY (departamento_id) REFERENCES departamentos(id)
        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_usuarios_rol
        FOREIGN KEY (rol_id) REFERENCES roles(id)
        ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Inventario de activos
-- ------------------------------------------------------------
CREATE TABLE activos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    identificador VARCHAR(20) NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    marca VARCHAR(50) NULL,
    modelo VARCHAR(50) NULL,
    numero_serie VARCHAR(100) NULL,
    ubicacion VARCHAR(100) NULL,
    responsable VARCHAR(100) NULL,
    departamento_id INT NULL,
    estado VARCHAR(50) NOT NULL DEFAULT 'Operativo',
    fecha_registro TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_activos_departamento
        FOREIGN KEY (departamento_id) REFERENCES departamentos(id)
        ON DELETE SET NULL ON UPDATE CASCADE,
    INDEX idx_activos_estado (estado),
    INDEX idx_activos_numero_serie (numero_serie)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Mantenimientos
-- ------------------------------------------------------------
CREATE TABLE mantenimientos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    activo_id INT NOT NULL,
    tipo ENUM('Preventivo', 'Correctivo') NOT NULL,
    descripcion TEXT NOT NULL,
    fecha_programada DATE NOT NULL,
    responsable VARCHAR(100) NULL,
    estado ENUM('Pendiente', 'En proceso', 'Finalizado') NOT NULL DEFAULT 'Pendiente',
    observaciones TEXT NULL,
    fecha_registro TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_finalizacion DATETIME NULL,
    CONSTRAINT fk_mantenimientos_activo
        FOREIGN KEY (activo_id) REFERENCES activos(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX idx_mantenimientos_fecha (fecha_programada),
    INDEX idx_mantenimientos_estado (estado)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Incidencias / mesa de ayuda
-- ------------------------------------------------------------
CREATE TABLE incidencias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    activo_id INT NOT NULL,
    descripcion TEXT NOT NULL,
    prioridad ENUM('Baja', 'Media', 'Alta', 'Crítica') NOT NULL DEFAULT 'Media',
    responsable VARCHAR(100) NULL,
    estado VARCHAR(50) NOT NULL DEFAULT 'Nueva',
    diagnostico TEXT NULL,
    resolucion TEXT NULL,
    solicitante_id INT NULL,
    fecha_registro TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_cierre DATETIME NULL,
    CONSTRAINT fk_incidencias_activo
        FOREIGN KEY (activo_id) REFERENCES activos(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_incidencias_solicitante
        FOREIGN KEY (solicitante_id) REFERENCES usuarios(id)
        ON DELETE SET NULL ON UPDATE CASCADE,
    INDEX idx_incidencias_estado (estado),
    INDEX idx_incidencias_prioridad (prioridad),
    INDEX idx_incidencias_solicitante (solicitante_id),
    INDEX idx_incidencias_fecha (fecha_registro)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Historial de movimientos de activos
-- ------------------------------------------------------------
CREATE TABLE historial_activos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    activo_id INT NOT NULL,
    tipo_movimiento VARCHAR(100) NOT NULL,
    detalle TEXT NULL,
    usuario_id INT NULL,
    fecha TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_historial_activo
        FOREIGN KEY (activo_id) REFERENCES activos(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_historial_usuario
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        ON DELETE SET NULL ON UPDATE CASCADE,
    INDEX idx_historial_activo (activo_id)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Auditoría general
-- ------------------------------------------------------------
CREATE TABLE auditoria (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NULL,
    accion VARCHAR(100) NOT NULL,
    entidad VARCHAR(100) NOT NULL,
    entidad_id INT NULL,
    detalle TEXT NULL,
    fecha TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_auditoria_usuario
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        ON DELETE SET NULL ON UPDATE CASCADE,
    INDEX idx_auditoria_fecha (fecha)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Proveedores
-- ------------------------------------------------------------
CREATE TABLE proveedores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    contacto VARCHAR(100) NULL,
    correo VARCHAR(100) NULL,
    telefono VARCHAR(30) NULL,
    servicio VARCHAR(150) NULL,
    fecha_registro TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Control de cambios
-- ------------------------------------------------------------
CREATE TABLE cambios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    activo_id INT NULL,
    solicitante VARCHAR(100) NOT NULL,
    descripcion TEXT NOT NULL,
    impacto ENUM('Bajo', 'Medio', 'Alto') NOT NULL DEFAULT 'Medio',
    estado ENUM('Solicitado', 'Evaluación', 'Autorizado', 'Ejecutado', 'Rechazado', 'Cerrado')
        NOT NULL DEFAULT 'Solicitado',
    fecha_solicitud TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_cambios_activo
        FOREIGN KEY (activo_id) REFERENCES activos(id)
        ON DELETE SET NULL ON UPDATE CASCADE,
    INDEX idx_cambios_estado (estado)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Gestión de problemas
-- ------------------------------------------------------------
CREATE TABLE problemas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    activo_id INT NULL,
    descripcion TEXT NOT NULL,
    causa_raiz TEXT NULL,
    solucion_permanente TEXT NULL,
    estado ENUM('Investigación', 'Causa Identificada', 'Resuelto', 'Cerrado')
        NOT NULL DEFAULT 'Investigación',
    fecha_registro TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_problemas_activo
        FOREIGN KEY (activo_id) REFERENCES activos(id)
        ON DELETE SET NULL ON UPDATE CASCADE,
    INDEX idx_problemas_estado (estado)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Formularios públicos
-- ------------------------------------------------------------
CREATE TABLE mensajes_contacto (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    organizacion VARCHAR(150) NOT NULL,
    correo VARCHAR(100) NOT NULL,
    telefono VARCHAR(30) NULL,
    motivo VARCHAR(100) NOT NULL,
    mensaje TEXT NOT NULL,
    acepta_privacidad BOOLEAN NOT NULL DEFAULT FALSE,
    fecha_envio TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atendido BOOLEAN NOT NULL DEFAULT FALSE
) ENGINE=InnoDB;

CREATE TABLE postulaciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    puesto_id VARCHAR(100) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(100) NOT NULL,
    telefono VARCHAR(30) NULL,
    mensaje TEXT NULL,
    acepta_privacidad BOOLEAN NOT NULL DEFAULT FALSE,
    fecha TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estado ENUM('Pendiente', 'Revisada')
        NOT NULL DEFAULT 'Pendiente',
    INDEX idx_postulaciones_puesto (puesto_id)
) ENGINE=InnoDB;
