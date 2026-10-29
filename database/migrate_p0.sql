-- ============================================================
-- TechTrack SATE - Migración P0 para bases de datos existentes
--
-- Este script NO borra datos. Agrega las columnas que el código
-- actual necesita y que no existían en instalaciones anteriores.
--
-- Uso:
--   mysql -u root -p techtrack_sate < database/migrate_p0.sql
--
-- Es idempotente: se puede ejecutar varias veces sin errores.
-- ============================================================

USE techtrack_sate;

DROP PROCEDURE IF EXISTS sate_add_column;

DELIMITER $$

CREATE PROCEDURE sate_add_column(
    IN p_tabla VARCHAR(64),
    IN p_columna VARCHAR(64),
    IN p_definicion VARCHAR(255)
)
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = p_tabla
          AND COLUMN_NAME = p_columna
    ) THEN
        SET @sql = CONCAT(
            'ALTER TABLE `', p_tabla, '` ADD COLUMN `', p_columna, '` ', p_definicion
        );
        PREPARE stmt FROM @sql;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;
    END IF;
END$$

DELIMITER ;

-- Usuarios
CALL sate_add_column('usuarios', 'fecha_registro', 'TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP');

-- Mantenimientos
CALL sate_add_column('mantenimientos', 'fecha_finalizacion', 'DATETIME NULL');

-- Incidencias
CALL sate_add_column('incidencias', 'fecha_cierre', 'DATETIME NULL');

-- Auditoría
CALL sate_add_column('auditoria', 'detalle', 'TEXT NULL');

-- Proveedores
CALL sate_add_column('proveedores', 'fecha_registro', 'TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP');

-- Formularios públicos
CALL sate_add_column('mensajes_contacto', 'acepta_privacidad', 'BOOLEAN NOT NULL DEFAULT FALSE');
CALL sate_add_column('postulaciones', 'acepta_privacidad', 'BOOLEAN NOT NULL DEFAULT FALSE');

-- Normaliza el estado legado de incidencias y su valor por defecto.
UPDATE incidencias SET estado = 'Nueva' WHERE estado = 'Pendiente';
ALTER TABLE incidencias ALTER COLUMN estado SET DEFAULT 'Nueva';

DROP PROCEDURE IF EXISTS sate_add_column;

-- Índices de apoyo (se ignoran si ya existen).
SET @sql = (
    SELECT IF(
        COUNT(*) = 0,
        'CREATE INDEX idx_incidencias_estado ON incidencias (estado)',
        'SELECT 1'
    )
    FROM information_schema.STATISTICS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'incidencias'
      AND INDEX_NAME = 'idx_incidencias_estado'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @sql = (
    SELECT IF(
        COUNT(*) = 0,
        'CREATE INDEX idx_auditoria_fecha ON auditoria (fecha)',
        'SELECT 1'
    )
    FROM information_schema.STATISTICS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'auditoria'
      AND INDEX_NAME = 'idx_auditoria_fecha'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;
