CREATE TABLE IF NOT EXISTS bills (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(50) NOT NULL,
  amount DECIMAL(10,2) NOT NULL,
  description VARCHAR(255) NOT NULL
);
INSERT INTO bills (name, amount, description) VALUES
('Alice', 50.00, 'Groceries'),
('Bob', 75.25, 'Internet'),
('Charlie', 30.00, 'Power bill');
