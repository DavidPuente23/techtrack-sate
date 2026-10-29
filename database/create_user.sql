-- ============================================================
-- Usuario dedicado de MySQL para SATE (recomendado)
--
-- Ejecutar como root:
--   mysql -u root -p < database/create_user.sql
--
-- Cambia la contraseña antes de ejecutarlo y usa la misma
-- en el archivo .env (DB_USER / DB_PASSWORD).
-- ============================================================

CREATE USER IF NOT EXISTS 'sate_app'@'localhost'
    IDENTIFIED BY 'CAMBIAR_ESTA_CONTRASENA';

GRANT SELECT, INSERT, UPDATE, DELETE
    ON techtrack_sate.*
    TO 'sate_app'@'localhost';

FLUSH PRIVILEGES;
