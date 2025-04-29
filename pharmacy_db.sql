-- Database schema for pharmacy management system
CREATE TABLE customers (
  customer_id int NOT NULL AUTO_INCREMENT,
  name varchar(100) NOT NULL,
  phone varchar(15) DEFAULT NULL,
  email varchar(100) DEFAULT NULL,
  address text DEFAULT NULL,
  age int DEFAULT NULL,
  loyalty_points int DEFAULT 0,
  created_at timestamp NOT NULL DEFAULT current_timestamp(),
  updated_at timestamp NULL DEFAULT NULL ON UPDATE current_timestamp(),
  PRIMARY KEY (customer_id),
  UNIQUE KEY email (email),
  KEY name (name)
);

CREATE TABLE employees (
  employee_id int NOT NULL AUTO_INCREMENT,
  name varchar(100) NOT NULL,
  role varchar(50) DEFAULT NULL,
  phone varchar(15) DEFAULT NULL,
  email varchar(100) DEFAULT NULL,
  salary decimal(10, 2) DEFAULT NULL,
  hire_date date DEFAULT NULL,
  created_at timestamp NOT NULL DEFAULT current_timestamp(),
  updated_at timestamp NULL DEFAULT NULL ON UPDATE current_timestamp(),
  PRIMARY KEY (employee_id),
  UNIQUE KEY email (email),
  KEY name (name),
  KEY role (role)
);

CREATE TABLE suppliers (
  supplier_id int NOT NULL AUTO_INCREMENT,
  name varchar(100) NOT NULL,
  contact_person varchar(85) DEFAULT NULL,
  phone varchar(15) DEFAULT NULL,
  email varchar(100) DEFAULT NULL,
  country varchar(50) DEFAULT NULL,
  payment_terms varchar(100) DEFAULT NULL,
  created_at timestamp NOT NULL DEFAULT current_timestamp(),
  updated_at timestamp NULL DEFAULT NULL ON UPDATE current_timestamp(),
  PRIMARY KEY (supplier_id),
  UNIQUE KEY email (email),
  KEY name (name)
);

CREATE TABLE medicines (
  medicine_id int NOT NULL AUTO_INCREMENT,
  name varchar(100) NOT NULL,
  quantity int NOT NULL DEFAULT 0,
  price decimal(10, 2) NOT NULL,
  expiry_date date DEFAULT NULL,
  manufacturer varchar(100) DEFAULT NULL,
  batch_number varchar(50) DEFAULT NULL,
  category varchar(50) DEFAULT NULL,
  description text DEFAULT NULL,
  supplier_id int DEFAULT NULL,
  created_at timestamp NOT NULL DEFAULT current_timestamp(),
  updated_at timestamp NULL DEFAULT NULL ON UPDATE current_timestamp(),
  PRIMARY KEY (medicine_id),
  KEY supplier_id (supplier_id),
  KEY name (name),
  KEY category (category),
  KEY expiry_date (expiry_date)
);

CREATE TABLE stock (
  stock_id int NOT NULL AUTO_INCREMENT,
  medicine_id int NOT NULL,
  quantity_in_stock int NOT NULL,
  reorder_level int NOT NULL,
  last_updated date DEFAULT NULL,
  created_at timestamp NOT NULL DEFAULT current_timestamp(),
  updated_at timestamp NULL DEFAULT NULL ON UPDATE current_timestamp(),
  PRIMARY KEY (stock_id),
  KEY medicine_id (medicine_id)
);

CREATE TABLE orders (
  order_id int NOT NULL AUTO_INCREMENT,
  customer_id int DEFAULT NULL,
  employee_id int DEFAULT NULL,
  order_type varchar(50) DEFAULT NULL,
  total_amount decimal(10, 2) NOT NULL,
  order_date timestamp NOT NULL DEFAULT current_timestamp(),
  created_at timestamp NOT NULL DEFAULT current_timestamp(),
  updated_at timestamp NULL DEFAULT NULL ON UPDATE current_timestamp(),
  PRIMARY KEY (order_id),
  KEY customer_id (customer_id),
  KEY employee_id (employee_id)
);

CREATE TABLE order_items (
  item_id int NOT NULL AUTO_INCREMENT,
  order_id int NOT NULL,
  medicine_id int NOT NULL,
  quantity int NOT NULL,
  unit_price decimal(10, 2) NOT NULL,
  subtotal decimal(10, 2) NOT NULL,
  created_at timestamp NOT NULL DEFAULT current_timestamp(),
  updated_at timestamp NULL DEFAULT NULL ON UPDATE current_timestamp(),
  PRIMARY KEY (item_id),
  KEY order_id (order_id),
  KEY medicine_id (medicine_id)
);

CREATE TABLE prescriptions (
  prescription_id int NOT NULL AUTO_INCREMENT,
  customer_id int NOT NULL,
  doctor_name varchar(100) DEFAULT NULL,
  doctor_license varchar(50) DEFAULT NULL,
  issue_date date NOT NULL,
  expiry_date date DEFAULT NULL,
  notes text DEFAULT NULL,
  created_at timestamp NOT NULL DEFAULT current_timestamp(),
  updated_at timestamp NULL DEFAULT NULL ON UPDATE current_timestamp(),
  PRIMARY KEY (prescription_id),
  KEY customer_id (customer_id)
);

CREATE TABLE prescription_items (
  item_id int NOT NULL AUTO_INCREMENT,
  prescription_id int NOT NULL,
  medicine_id int NOT NULL,
  quantity int NOT NULL,
  dosage varchar(50) DEFAULT NULL,
  instructions text DEFAULT NULL,
  created_at timestamp NOT NULL DEFAULT current_timestamp(),
  updated_at timestamp NULL DEFAULT NULL ON UPDATE current_timestamp(),
  PRIMARY KEY (item_id),
  KEY prescription_id (prescription_id),
  KEY medicine_id (medicine_id)
);

-- Foreign key constraints

-- Foreign key for medicines → suppliers
ALTER TABLE medicines
ADD FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
ON DELETE SET NULL 
ON UPDATE CASCADE;

-- orders → customers
ALTER TABLE orders
ADD FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
ON DELETE CASCADE
ON UPDATE CASCADE;

-- orders → employees
ALTER TABLE orders
ADD FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
ON DELETE SET NULL
ON UPDATE CASCADE;

-- order_items → orders
ALTER TABLE order_items
ADD FOREIGN KEY (order_id) REFERENCES orders(order_id)
ON DELETE CASCADE
ON UPDATE CASCADE;

-- order_items → medicines
ALTER TABLE order_items
ADD FOREIGN KEY (medicine_id) REFERENCES medicines(medicine_id)
ON DELETE CASCADE
ON UPDATE CASCADE;

-- prescriptions → customers
ALTER TABLE prescriptions
ADD FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
ON DELETE CASCADE
ON UPDATE CASCADE;

-- prescription_items → prescriptions
ALTER TABLE prescription_items
ADD FOREIGN KEY (prescription_id) REFERENCES prescriptions(prescription_id)
ON DELETE CASCADE
ON UPDATE CASCADE;

-- prescription_items → medicines
ALTER TABLE prescription_items
ADD FOREIGN KEY (medicine_id) REFERENCES medicines(medicine_id)
ON DELETE CASCADE
ON UPDATE CASCADE;


-- stock → medicines
ALTER TABLE stock
ADD FOREIGN KEY (medicine_id) REFERENCES medicines(medicine_id)
ON DELETE CASCADE
ON UPDATE CASCADE;



-- Sample data insertion
INSERT INTO customers (name, phone, email, address) VALUES
('Ahmed Ali', '07700000001', 'ahmed@example.com', 'Baghdad'),
('Sara Hasan', '07700000002', 'sara@example.com', 'Basra'),
('Omar Yasin', '07700000003', 'omar@example.com', 'Mosul'),
('Fatima Noor', '07700000004', 'fatima@example.com', 'Erbil'),
('Ali Kareem', '07700000005', 'ali@example.com', 'Karbala'),
('Laila Nabil', '07700000006', 'laila@example.com', 'Najaf'),
('Hassan Tarek', '07700000007', 'hassan@example.com', 'Kirkuk'),
('Mona Adel', '07700000008', 'mona@example.com', 'Baghdad'),
('Yousef Sami', '07700000009', 'yousef@example.com', 'Basra'),
('Zainab Rami', '07700000010', 'zainab@example.com', 'Diyala');
INSERT INTO employees (name, position, salary, phone, email) VALUES
('Ahmed Sami', 'Pharmacist', 1200.00, '07800000001', 'sami@example.com'),
('Lina Abbas', 'Assistant', 800.00, '07800000002', 'lina@example.com'),
('Khalid Omar', 'Manager', 2000.00, '07800000003', 'khalid@example.com'),
('Nadia Ihsan', 'Technician', 950.00, '07800000004', 'nadia@example.com'),
('Mustafa Adel', 'Cashier', 600.00, '07800000005', 'mustafa@example.com'),
('Huda Mazin', 'Pharmacist', 1250.00, '07800000006', 'huda@example.com'),
('Rami Fadel', 'Assistant', 750.00, '07800000007', 'rami@example.com'),
('Zahraa Karim', 'Cleaner', 400.00, '07800000008', 'zahraa@example.com'),
('Bassam Talib', 'Technician', 950.00, '07800000009', 'bassam@example.com'),
('Farah Munir', 'Manager', 2100.00, '07800000010', 'farah@example.com');


INSERT INTO suppliers (supplier_id, name, contact_person, phone, email, address) VALUES
(1, 'Dar Alshifa', 'Ahmed', '0781111111', 'ahmed@darshifa.com', 'Baghdad, Iraq'),
(2, 'Future Pharmacy', 'Layla', '0782222222', 'layla@futureph.com', 'Basrah, Iraq'),
(3, 'Arab Meds', 'Omar', '0783333333', 'omar@arabmeds.com', 'Erbil, Iraq'),
(4, 'Medical Top', 'Rana', '0784444444', 'rana@medtop.com', 'Baghdad, Iraq'),
(5, 'Noor Health', 'Yousef', '0785555555', 'yousef@noorhealth.com', 'Mosul, Iraq'),
(6, 'Gulf Shifa', 'Huda', '0786666666', 'huda@gulfshifa.com', 'Najaf, Iraq'),
(7, 'Bayt Tibb', 'Hassan', '0787777777', 'hassan@bayttibb.com', 'Baghdad, Iraq'),
(8, 'Dawa & Shifa', 'Fatima', '0788888888', 'fatima@dawashifa.com', 'Kirkuk, Iraq'),
(9, 'Health Bridge', 'Zainab', '0789999999', 'zainab@healthbridge.com', 'Sulaymaniyah, Iraq'),
(10, 'Pharma Trust', 'Ali', '0781234567', 'ali@pharmatrust.com', 'Karbala, Iraq');

INSERT INTO medicines (name, quantity, price, expiry_date, manufacturer, batch_number, category, description, supplier_id) VALUES
('Paracetamol 500mg', 200, 1.25, '2026-12-31', 'GSK', 'GB12345', 'Painkiller', 'For fever and mild pain', 1),
('Amoxicillin 500mg', 150, 2.50, '2025-08-15', 'Pfizer', 'A98765', 'Antibiotic', 'Broad spectrum antibiotic', 2),
('Ibuprofen 400mg', 180, 1.75, '2024-05-10', 'Sanofi', 'IB3042', 'Painkiller', 'Inflammation relief', 1),
('Cetirizine 10mg', 120, 0.90, '2026-11-01', 'Novartis', 'CT2022', 'Antihistamine', 'Allergy relief', 2),
('Metformin 850mg', 130, 3.00, '2027-01-20', 'Merck', 'M85087', 'Diabetes', 'Blood sugar control', 3),
('Expired Cough Syrup', 50, 1.00, '2022-06-30', 'Hikma', 'HCX001', 'Cough', 'Expired medicine', 4),
('Rare Injection', 10, 20.00, '2025-02-28', 'AbbVie', 'RJN888', 'Injection', 'High-cost rare use', 5),
('Vitamin C 1000mg', 0, 0.50, '2026-09-01', 'Bayer', 'VC999', 'Supplement', 'Out of stock', 6),
('Aspirin 100mg', 250, 0.40, '2027-03-15', 'GSK', 'AS100', 'Antiplatelet', 'Blood thinner', 1),
('Unknown Med', 5, 15.00, '2024-01-01', 'Unknown', 'UK001', 'Misc', 'Unclassified item', 7);

INSERT INTO employees (employee_id, name, role, phone, email, address, hire_date, salary) VALUES
(1, 'Ahmed Kareem', 'Pharmacist', '0781111111', 'ahmed@pharmacy.com', 'Baghdad', '2020-01-15', 900.00),
(2, 'Hanan Ali', 'Assistant', '0782222222', 'hanan@pharmacy.com', 'Basrah', '2021-03-10', 550.00),
(3, 'Yousef Saad', 'Cashier', '0783333333', 'yousef@pharmacy.com', 'Erbil', '2022-06-01', 450.00),
(4, 'Rana Nabil', 'Pharmacist', '0784444444', 'rana@pharmacy.com', 'Baghdad', '2019-09-12', 1000.00),
(5, 'Omar Talib', 'Cleaner', '0785555555', 'omar@pharmacy.com', 'Mosul', '2023-01-20', 300.00),
(6, 'Fatima Hassan', 'Manager', '0786666666', 'fatima@pharmacy.com', 'Najaf', '2018-05-05', 1200.00),
(7, 'Ali Zaid', 'Security', '0787777777', 'ali@pharmacy.com', 'Kirkuk', '2020-10-10', 400.00),
(8, 'Zainab Hadi', 'Pharmacist', '0788888888', 'zainab@pharmacy.com', 'Sulaymaniyah', '2022-12-12', 950.00),
(9, 'Hassan Qasim', 'Assistant', '0789999999', 'hassan@pharmacy.com', 'Baghdad', '2021-08-08', 570.00),
(10, 'Salma Mahdi', 'Cashier', '0781234567', 'salma@pharmacy.com', 'Karbala', '2024-02-02', 430.00);

INSERT INTO customers (customer_id, name, phone, email, address) VALUES
(1, 'Ammar Salman', '0791111111', 'ammar@mail.com', 'Baghdad'),
(2, 'Mona Ali', '0792222222', 'mona@mail.com', 'Basrah'),
(3, 'Zaid Ahmed', '0793333333', 'zaid@mail.com', 'Erbil'),
(4, 'Sara Hussein', '0794444444', 'sara@mail.com', 'Mosul'),
(5, 'Khalid Abbas', '0795555555', 'khalid@mail.com', 'Najaf'),
(6, 'Lina Majid', '0796666666', 'lina@mail.com', 'Kirkuk'),
(7, 'Tariq Saeed', '0797777777', 'tariq@mail.com', 'Baghdad'),
(8, 'Nour Fadel', '0798888888', 'nour@mail.com', 'Sulaymaniyah'),
(9, 'Bilal Karim', '0799999999', 'bilal@mail.com', 'Basrah'),
(10, 'Dina Zaki', '0791234567', 'dina@mail.com', 'Baghdad');

INSERT INTO prescriptions (prescription_id, customer_id, employee_id, date_issued, notes) VALUES
(1, 1, 1, '2024-04-01', 'Take after meals'),
(2, 2, 2, '2024-04-02', 'Avoid alcohol'),
(3, 3, 3, '2024-04-03', '3 times daily'),
(4, 4, 4, '2024-04-04', 'Finish full dose'),
(5, 5, 5, '2024-04-05', 'No sugar'),
(6, 6, 6, '2024-04-06', 'Monitor BP'),
(7, 7, 7, '2024-04-07', 'Before sleeping'),
(8, 8, 8, '2024-04-08', 'Apply on skin'),
(9, 9, 9, '2024-04-09', 'Use for 5 days'),
(10, 10, 10, '2024-04-10', 'Take with water');


