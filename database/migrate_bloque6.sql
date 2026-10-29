-- ============================================================
-- TechTrack SATE - Migración Bloque 6
--
-- Agrega los tres roles que faltan de la estructura del PIA y
-- las columnas necesarias para la gestión de usuarios y el
-- alcance de incidencias por solicitante.
--
-- No borra datos. Es idempotente: puede ejecutarse varias veces.
--
-- Uso:
--   mysql -u root -p techtrack_sate < database/migrate_bloque6.sql
--   o bien: python scripts/apply_bloque6.py
-- ============================================================

USE techtrack_sate;

-- 1. Roles del PIA que faltaban en la instalación original.
INSERT IGNORE INTO roles (nombre) VALUES
    ('Administrador de Activos'),
    ('Administrador de Redes'),
    ('Desarrollador');

-- 2. Contraseña temporal y último acceso.
SET @sql = (
    SELECT IF(
        COUNT(*) = 0,
        'ALTER TABLE usuarios ADD COLUMN debe_cambiar_password BOOLEAN NOT NULL DEFAULT FALSE',
        'DO 0'
    )
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'usuarios'
      AND COLUMN_NAME = 'debe_cambiar_password'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @sql = (
    SELECT IF(
        COUNT(*) = 0,
        'ALTER TABLE usuarios ADD COLUMN ultimo_acceso DATETIME NULL',
        'DO 0'
    )
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'usuarios'
      AND COLUMN_NAME = 'ultimo_acceso'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 3. Solicitante de cada incidencia (para el alcance del rol Usuario Solicitante).
SET @sql = (
    SELECT IF(
        COUNT(*) = 0,
        'ALTER TABLE incidencias ADD COLUMN solicitante_id INT NULL',
        'DO 0'
    )
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'incidencias'
      AND COLUMN_NAME = 'solicitante_id'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @sql = (
    SELECT IF(
        COUNT(*) = 0,
        'ALTER TABLE incidencias ADD CONSTRAINT fk_incidencias_solicitante FOREIGN KEY (solicitante_id) REFERENCES usuarios(id) ON DELETE SET NULL ON UPDATE CASCADE',
        'DO 0'
    )
    FROM information_schema.TABLE_CONSTRAINTS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'incidencias'
      AND CONSTRAINT_NAME = 'fk_incidencias_solicitante'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @sql = (
    SELECT IF(
        COUNT(*) = 0,
        'CREATE INDEX idx_incidencias_solicitante ON incidencias (solicitante_id)',
        'DO 0'
    )
    FROM information_schema.STATISTICS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'incidencias'
      AND INDEX_NAME = 'idx_incidencias_solicitante'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;
