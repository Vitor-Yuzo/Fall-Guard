CREATE TABLE falls (
    id INT AUTO_INCREMENT PRIMARY KEY,
    evento VARCHAR(50) NOT NULL,
    classe VARCHAR(20) NOT NULL,
    confianca DECIMAL(5,4),
    timestamp_evento DATETIME NOT NULL,
    data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);