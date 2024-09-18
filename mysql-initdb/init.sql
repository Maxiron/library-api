CREATE DATABASE IF NOT EXISTS frontend_db;
CREATE DATABASE IF NOT EXISTS backend_db;

CREATE USER 'frontend_user'@'%' IDENTIFIED BY 'frontend_password';
CREATE USER 'backend_user'@'%' IDENTIFIED BY 'backend_password';

GRANT ALL PRIVILEGES ON frontend_db.* TO 'frontend_user'@'%';
GRANT ALL PRIVILEGES ON backend_db.* TO 'backend_user'@'%';

FLUSH PRIVILEGES;
