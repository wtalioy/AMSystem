CREATE TABLE IF NOT EXISTS User (
  user_id CHAR(10) NOT NULL,
  user_name VARCHAR(10) NOT NULL,
  user_pwd VARCHAR(100) NOT NULL,
  user_type VARCHAR(15) NOT NULL CHECK (user_type IN ('user', 'customer', 'worker', 'administrator')),
  PRIMARY KEY (user_id)
)
CREATE TABLE IF NOT EXISTS Customer (
  user_id CHAR(10) NOT NULL,
  PRIMARY KEY (user_id),
  FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE
)
CREATE TABLE IF NOT EXISTS CarType (
  car_type VARCHAR(20) NOT NULL,
  PRIMARY KEY (car_type)
)
CREATE TABLE IF NOT EXISTS Car (
  car_id CHAR(10) NOT NULL,
  car_type VARCHAR(20) NOT NULL,
  customer_id CHAR(10),
  PRIMARY KEY (car_id),
  FOREIGN KEY (car_type) REFERENCES CarType(car_type),
  FOREIGN KEY (customer_id) REFERENCES Customer(user_id)
)
CREATE TABLE IF NOT EXISTS Wage (
  worker_type VARCHAR(20) NOT NULL,
  wage_per_hour INTEGER NOT NULL,
  PRIMARY KEY (worker_type)
)
CREATE TABLE IF NOT EXISTS Worker (
  user_id CHAR(10) NOT NULL,
  worker_type VARCHAR(20) NOT NULL,
  availability_status INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (user_id),
  FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE,
  FOREIGN KEY (worker_type) REFERENCES Wage(worker_type)
)
CREATE TABLE IF NOT EXISTS Distribute (
  distribute_id INTEGER NOT NULL AUTO_INCREMENT,
  distribute_time TIMESTAMP NOT NULL,
  amount DECIMAL(10,1) NOT NULL,
  worker_id CHAR(10) NOT NULL,
  PRIMARY KEY (distribute_id),
  FOREIGN KEY (worker_id) REFERENCES Worker(user_id) ON DELETE CASCADE ON UPDATE CASCADE
)
CREATE TABLE IF NOT EXISTS ServiceOrder (
  order_id CHAR(10) NOT NULL,
  start_time TIMESTAMP NOT NULL,
  end_time TIMESTAMP,
  description TEXT NOT NULL,
  rating INTEGER CHECK (rating BETWEEN 1 AND 5),
  comment TEXT,
  status INTEGER NOT NULL DEFAULT 0,
  total_cost DECIMAL(10,2),
  expedite_flag BOOLEAN NOT NULL DEFAULT False,
  assignment_attempts INTEGER NOT NULL DEFAULT 0,
  last_assignment_at TIMESTAMP,
  worker_id CHAR(10),
  car_id CHAR(10) NOT NULL,
  customer_id CHAR(10) NOT NULL,
  PRIMARY KEY (order_id),
  FOREIGN KEY (worker_id) REFERENCES Worker(user_id) ON DELETE SET NULL ON UPDATE CASCADE,
  FOREIGN KEY (car_id) REFERENCES Car(car_id) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (customer_id) REFERENCES Customer(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
  INDEX idx_ServiceOrder_worker_id (worker_id),
  INDEX idx_ServiceOrder_car_id (car_id),
  INDEX idx_ServiceOrder_customer_id (customer_id)
)
CREATE TABLE IF NOT EXISTS ServiceLog (
  log_time TIMESTAMP NOT NULL,
  consumption TEXT NOT NULL,
  cost DECIMAL(10,2) NOT NULL,
  duration DECIMAL(3,1) NOT NULL,
  order_id CHAR(10) NOT NULL,
  worker_id CHAR(10) NOT NULL,
  PRIMARY KEY (log_time, order_id),
  FOREIGN KEY (order_id) REFERENCES ServiceOrder(order_id) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (worker_id) REFERENCES Worker(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
  INDEX idx_ServiceLog_worker_id (worker_id)
)
CREATE TABLE IF NOT EXISTS ServiceProcedure (
  procedure_id INTEGER NOT NULL,
  procedure_text TINYTEXT NOT NULL,
  current_status INTEGER NOT NULL DEFAULT 0,
  order_id CHAR(10),
  PRIMARY KEY (procedure_id, order_id),
  FOREIGN KEY (order_id) REFERENCES ServiceOrder(order_id) ON DELETE CASCADE ON UPDATE CASCADE
)
CREATE TABLE IF NOT EXISTS Administrator (
  user_id CHAR(10) NOT NULL,
  PRIMARY KEY (user_id),
  FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE
)
CREATE TABLE IF NOT EXISTS AuditLog (
  audit_id CHAR(10) NOT NULL,
  table_name CHAR(50) NOT NULL,
  record_id CHAR(10) NOT NULL,
  operation CHAR(10) NOT NULL,
  old_values TEXT,
  new_values TEXT,
  changed_fields TEXT,
  timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  user_id CHAR(10),
  PRIMARY KEY (audit_id)
)