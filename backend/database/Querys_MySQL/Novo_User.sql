CREATE USER IF NOT EXISTS 'fallguard_user'@'localhost'
IDENTIFIED BY 'FallGuard2026!';

GRANT SELECT, INSERT, UPDATE, DELETE
ON fallguard.*
TO 'fallguard_user'@'localhost';

SHOW GRANTS FOR 'fallguard_user'@'localhost';