CREATE TABLE IF NOT EXISTS bills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    description VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    receipt_url VARCHAR(500)
);

CREATE TABLE IF NOT EXISTS expense_analytics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    event_data JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO bills (name, amount, description) VALUES
('Alice', 50.00, 'Groceries'),
('Bob', 75.25, 'Internet'),
('Charlie', 30.00, 'Power bill');