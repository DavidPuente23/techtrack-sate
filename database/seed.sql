-- ============================================================
-- TechTrack SATE - Datos base
-- Ejecutar DESPUÉS de database/schema.sql
--
-- Usuario inicial:
--   Correo:     admin@techtrack.com
--   Contraseña: Admin123!
--
-- IMPORTANTE: cambia esta contraseña al primer inicio de sesión.
-- ============================================================

USE techtrack_sate;
SET NAMES utf8mb4;

INSERT IGNORE INTO departamentos (id, nombre) VALUES
    (1, 'SIT'),
    (2, 'Redes'),
    (3, 'Desarrollo'),
    (4, 'Soporte');

INSERT IGNORE INTO roles (id, nombre) VALUES
    (1, 'Administrador General'),
    (2, 'Dirección General'),
    (3, 'Técnico de Soporte'),
    (4, 'Usuario Solicitante'),
    (5, 'Administrador de Activos'),
    (6, 'Administrador de Redes'),
    (7, 'Desarrollador');

-- Hash generado con Werkzeug para la contraseña: Admin123!
INSERT IGNORE INTO usuarios
    (nombre, email, password, departamento_id, rol_id, activo, tema)
VALUES
    (
        'Administrador',
        'admin@techtrack.com',
        'scrypt:32768:8:1$1aBJEZg9A9WcDGPr$3c6c42cd7e32d958d8f323737d91c341ea566eaebd9b00b41cd92cacbf655880262881da38dbeaf3bb1d2dcad1a1a905bdbbe996aa1bcf7acd6a173ce83f6bfe',
        1,
        1,
        TRUE,
        'blue'
    );
