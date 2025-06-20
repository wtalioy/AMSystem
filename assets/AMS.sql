-- Automobile Maintenance System (AMS) Database Schema

-- ====================================
-- USER MANAGEMENT TABLES
-- ====================================

-- Base user table that stores common user information for all user types
CREATE TABLE IF NOT EXISTS User (
    user_id CHAR(10) NOT NULL, -- Unique identifier for each user
    user_name VARCHAR(10) NOT NULL, -- Display name for the user
    user_pwd VARCHAR(100) NOT NULL, -- Encrypted password (should be hashed)
    user_type VARCHAR(15) NOT NULL CHECK (
        user_type IN (
            'user',
            'customer',
            'worker',
            'administrator'
        )
    ), -- Role-based access control
    PRIMARY KEY (user_id)
);

-- Customer-specific information (inherits from User)
CREATE TABLE IF NOT EXISTS Customer (
    user_id CHAR(10) NOT NULL, -- References User table for customer details
    PRIMARY KEY (user_id),
    FOREIGN KEY (user_id) REFERENCES User (user_id) ON DELETE CASCADE
);

-- Administrator-specific information (inherits from User)
CREATE TABLE IF NOT EXISTS Administrator (
    user_id CHAR(10) NOT NULL, -- References User table for admin details
    PRIMARY KEY (user_id),
    FOREIGN KEY (user_id) REFERENCES User (user_id) ON DELETE CASCADE
);

-- ====================================
-- VEHICLE MANAGEMENT TABLES
-- ====================================

-- Defines available car types/models in the system
CREATE TABLE IF NOT EXISTS CarType (
    car_type VARCHAR(20) NOT NULL, -- Car model/type identifier (e.g., "Sedan", "SUV", "Truck")
    PRIMARY KEY (car_type)
);

-- Individual cars registered in the system
CREATE TABLE IF NOT EXISTS Car (
    car_id CHAR(10) NOT NULL, -- Unique car identifier (license plate)
    car_type VARCHAR(20) NOT NULL, -- Type of car (references CarType)
    customer_id CHAR(10), -- Owner of the car (can be NULL for unassigned cars)
    PRIMARY KEY (car_id),
    FOREIGN KEY (car_type) REFERENCES CarType (car_type),
    FOREIGN KEY (customer_id) REFERENCES Customer (user_id)
);

-- ====================================
-- WORKER MANAGEMENT TABLES
-- ====================================

-- Wage structure for different worker types
CREATE TABLE IF NOT EXISTS Wage (
    worker_type VARCHAR(20) NOT NULL, -- Type of worker (e.g., "Mechanic", "Technician", "Inspector")
    wage_per_hour INTEGER NOT NULL, -- Hourly wage rate for this worker type
    PRIMARY KEY (worker_type)
);

-- Worker-specific information (inherits from User)
CREATE TABLE IF NOT EXISTS Worker (
    user_id CHAR(10) NOT NULL, -- References User table for worker details
    worker_type VARCHAR(20) NOT NULL, -- Specialization/type of worker
    availability_status INTEGER NOT NULL DEFAULT 0, -- 0=Available, 1=Busy
    PRIMARY KEY (user_id),
    FOREIGN KEY (user_id) REFERENCES User (user_id) ON DELETE CASCADE,
    FOREIGN KEY (worker_type) REFERENCES Wage (worker_type)
);

-- Payment distribution records for workers
CREATE TABLE IF NOT EXISTS Distribute (
    distribute_id INTEGER NOT NULL AUTO_INCREMENT, -- Unique payment record ID
    distribute_time TIMESTAMP NOT NULL, -- When payment was made
    amount DECIMAL(10, 1) NOT NULL, -- Payment amount
    worker_id CHAR(10) NOT NULL, -- Worker receiving payment
    PRIMARY KEY (distribute_id),
    FOREIGN KEY (worker_id) REFERENCES Worker (user_id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- ====================================
-- SERVICE ORDER MANAGEMENT
-- ====================================

-- Main service orders table - tracks all service requests
CREATE TABLE IF NOT EXISTS ServiceOrder (
    order_id CHAR(10) NOT NULL, -- Unique service order identifier
    start_time TIMESTAMP NOT NULL, -- When service was requested/started
    end_time TIMESTAMP, -- When service was completed (NULL if ongoing)
    description TEXT NOT NULL, -- Detailed description of service needed
    rating INTEGER CHECK (rating BETWEEN 1 AND 5), -- Customer satisfaction rating (1-5 stars)
    comment TEXT, -- Additional customer feedback
    status INTEGER NOT NULL DEFAULT 0, -- 0=Pending Assignment, 1=Assigned, 2=In Progress, 3=Completed
    total_cost DECIMAL(10, 2), -- Final cost of service (calculated from logs)
    expedite_flag BOOLEAN NOT NULL DEFAULT False, -- Priority service flag
    assignment_attempts INTEGER NOT NULL DEFAULT 0, -- Number of worker assignment attempts
    last_assignment_at TIMESTAMP, -- Last time worker assignment was attempted (NULL if not assigned)
    worker_id CHAR(10), -- Assigned worker (NULL if unassigned)
    car_id CHAR(10) NOT NULL, -- Car being serviced
    customer_id CHAR(10) NOT NULL, -- Customer requesting service
    PRIMARY KEY (order_id),
    FOREIGN KEY (worker_id) REFERENCES Worker (user_id) ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (car_id) REFERENCES Car (car_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (customer_id) REFERENCES Customer (user_id) ON DELETE CASCADE ON UPDATE CASCADE,
    -- Indexes for performance optimization on frequently queried columns
    INDEX idx_ServiceOrder_worker_id (worker_id),
    INDEX idx_ServiceOrder_car_id (car_id),
    INDEX idx_ServiceOrder_customer_id (customer_id)
);

-- Detailed service activity logs - tracks work performed and resources used
CREATE TABLE IF NOT EXISTS ServiceLog (
    log_time TIMESTAMP NOT NULL, -- When the log was created
    consumption TEXT NOT NULL, -- Parts/materials consumed during service
    cost DECIMAL(10, 2) NOT NULL, -- Cost of this specific service activity
    duration DECIMAL(3, 1) NOT NULL, -- Time spent on this activity (in hours)
    order_id CHAR(10) NOT NULL, -- Service order this log belongs to
    worker_id CHAR(10) NOT NULL, -- Worker who performed this activity
    PRIMARY KEY (log_time, order_id), -- Composite key allows multiple logs per order
    FOREIGN KEY (order_id) REFERENCES ServiceOrder (order_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (worker_id) REFERENCES Worker (user_id) ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX idx_ServiceLog_worker_id (worker_id) -- Performance index for worker queries
);

-- Service procedure checklist - breaks down service orders into steps
CREATE TABLE IF NOT EXISTS ServiceProcedure (
    procedure_id INTEGER NOT NULL, -- Step number in the service procedure (1, 2, 3, ...)
    procedure_text TINYTEXT NOT NULL, -- Description of this procedure step
    current_status INTEGER NOT NULL DEFAULT 0, -- 0=Pending, 1=In Progress, 2=Completed
    order_id CHAR(10), -- Service order this procedure belongs to
    PRIMARY KEY (procedure_id, order_id), -- Composite key for procedure steps per order
    FOREIGN KEY (order_id) REFERENCES ServiceOrder (order_id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- ====================================
-- AUDIT AND LOGGING
-- ====================================

-- System audit trail - tracks all database changes for security and compliance
CREATE TABLE IF NOT EXISTS AuditLog (
    audit_id CHAR(10) NOT NULL, -- Unique audit record identifier
    table_name CHAR(50) NOT NULL, -- Which table was modified
    record_id CHAR(10) NOT NULL, -- ID of the record that was changed
    operation CHAR(10) NOT NULL, -- Type of operation (INSERT, UPDATE, DELETE)
    old_values TEXT, -- Previous values before change (JSON format)
    new_values TEXT, -- New values after change (JSON format)
    changed_fields TEXT, -- List of fields that were modified
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, -- When the change occurred
    user_id CHAR(10), -- Who made the change (NULL for system changes)
    PRIMARY KEY (audit_id)
);