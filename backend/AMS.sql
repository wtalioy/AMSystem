-- User表（基类）
CREATE TABLE User (
    user_id CHAR(10) PRIMARY KEY,   -- 主键
    user_name VARCHAR(10) NOT NULL,
    user_pwd VARCHAR(100) NOT NULL,
    user_type VARCHAR(15) NOT NULL CHECK (user_type IN ('Customer', 'Worker', 'Administrator'))
);

-- 子类表（直接继承user_id为主键）
CREATE TABLE Customer (
    user_id CHAR(10) PRIMARY KEY,
    FOREIGN KEY (user_id) REFERENCES User(user_id)
);

CREATE TABLE Worker (
    user_id CHAR(10) PRIMARY KEY,
    worker_type TINYINT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES User(user_id),
    FOREIGN KEY (worker_type) REFERENCES Wage(worker_type)
);

CREATE TABLE Administrator (
    user_id CHAR(10) PRIMARY KEY,
    FOREIGN KEY (user_id) REFERENCES User(user_id)
);

-- Car表（包含Customer关联）
CREATE TABLE Car (
    car_id CHAR(10) PRIMARY KEY,
    customer_id CHAR(10) NOT NULL,  -- 用户外键
    car_type CHAR(30) NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES Customer(user_id)
);

-- Order表（包含Car、Customer关联）
CREATE TABLE Order (
    order_id CHAR(10) PRIMARY KEY,
    worker_id CHAR(10) NOT NULL,  -- 工人外键
    customer_id CHAR(10) NOT NULL,  -- 用户外键
    car_id CHAR(10) NOT NULL,       -- 车辆外键
    description TEXT NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,   -- 已完成的订单才有结束时间
    rating TINYINT CHECK (rating BETWEEN 1 AND 5),  -- 评分
    comment TEXT,
    FOREIGN KEY (worker_id) REFERENCES Worker(worker_id),
    FOREIGN KEY (customer_id) REFERENCES Customer(user_id),
    FOREIGN KEY (car_id) REFERENCES Car(car_id)
);

-- Procedure表（包含Order关联）
CREATE TABLE Procedure (
    order_id CHAR(10) NOT NULL,
    procedure_id TINYINT NOT NULL AUTO_INCREMENT,
    procedure_text TINYTEXT NOT NULL,
    current_status TINYINT NOT NULL,
    PRIMARY KEY (order_id, procedure_id),
    FOREIGN KEY (order_id) REFERENCES Order(order_id)
);

-- Wage表（工资标准）
CREATE TABLE Wage (
    worker_type TINYINT AUTO_INCREMENT PRIMARY KEY,   -- 工人类型为主键
    wage_per_hour INTEGER NOT NULL
);

-- Log 表
CREATE TABLE Log (
    worker_id CHAR(10) NOT NULL,
    order_id CHAR(10) NOT NULL,
    log_time TIMESTAMP NOT NULL,
    consumption TEXT NOT NULL,
    cost DECIMAL(10,2) NOT NULL,
    duration DECIMAL(3,1) NOT NULL,   -- 以小时为单位
    PRIMARY KEY (order_id, log_time),
    FOREIGN KEY (worker_id) REFERENCES Worker(worker_id),
    FOREIGN KEY (order_id) REFERENCES Order(order_id)
);

-- Distribute 表
CREATE TABLE Distribute (
    distribute_id INTEGER AUTO_INCREMENT PRIMARY KEY,
    worker_id CHAR(10) NOT NULL,
    distribute_time TIMESTAMP NOT NULL,
    amount DECIMAL(10,1) NOT NULL,
    FOREIGN KEY (worker_id) REFERENCES Worker(worker_id)
);