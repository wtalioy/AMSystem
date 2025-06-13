# 车辆维修管理系统 - 核心功能SQL语句说明和触发器说明

## 一、系统架构概述

本车辆维修管理系统采用了**自研 ORM 框架（DBRM - Database Remote）**进行数据库操作，而非直接 SQL 语句编写。该 ORM 框架基于 [Lab1](https://github.com/wtalioy/DatabaseRemote) 实现，参考 SQLAlchemy ，提供了完整的对象关系映射功能，并通过 Python 装饰器和服务层模式实现了传统数据库触发器的功能。

### 技术架构特点：
- **自定义 ORM 框架**：`app.dbrm` 包提供完整的 Table、Column、Query 等功能
- **装饰器触发器**：通过 `@audit` 装饰器实现数据变更追踪和自动化操作
- **服务层自动化**：通过 Service 层实现复杂业务逻辑的自动触发
- **定时调度器**：实现定期数据处理和维护任务

## 二、自研ORM框架核心功能

### 2.1 数据模型定义

我们的 ORM 框架使用 `@model_register` 装饰器和 `Table` 基类来定义数据模型：

```python
@model_register
class User(Table):
    __tablename__ = 'User'
    
    user_id = Column(Char(10), nullable=False, primary_key=True)
    user_name = Column(String(10), nullable=False)
    user_pwd = Column(String(100), nullable=False)
    user_type = Column(String(15), nullable=False, 
                      check="IN ('user', 'customer', 'worker', 'administrator')")
```

**等价SQL建表语句：**
```sql
CREATE TABLE IF NOT EXISTS User (
    user_id CHAR(10) NOT NULL,
    user_name VARCHAR(10) NOT NULL,
    user_pwd VARCHAR(100) NOT NULL,
    user_type VARCHAR(15) NOT NULL CHECK (user_type IN ('user', 'customer', 'worker', 'administrator')),
    PRIMARY KEY (user_id)
);
```

### 2.2 查询构建器

我们的 ORM 提供了链式查询构建器：

```python
# ORM查询示例
orders = db.query(ServiceOrderModel).filter_by(customer_id=customer_id).all()

# 复杂条件查询
query = db.query(ServiceOrderModel).join(
    Car, on=(Car.car_id, ServiceOrderModel.car_id)
).where(
    Condition.eq(Car.car_type, car_type)
)
```

**等价SQL语句：**
```sql
-- 简单查询（ORM: db.query(ServiceOrderModel).filter_by(customer_id=customer_id).all()）
SELECT * FROM ServiceOrder WHERE customer_id = '客户ID';

-- 复杂连接查询（ORM: db.query(ServiceOrderModel).join(Car, on=(Car.car_id, ServiceOrderModel.car_id)).where(...)）
SELECT ServiceOrder.* 
FROM ServiceOrder 
INNER JOIN Car ON Car.car_id = ServiceOrder.car_id 
WHERE Car.car_type = '车型';

-- 带条件和排序的查询
SELECT * FROM ServiceOrder 
WHERE customer_id = '客户ID' AND status = 1
ORDER BY start_time DESC
LIMIT 10 OFFSET 0;

-- 聚合查询示例
SELECT COUNT(*) FROM ServiceOrder WHERE status = 4;
```

## 三、核心业务功能的SQL实现说明

### 3.1 用户注册和认证功能

**ORM实现：**
```python
# CRUD层
def create(self, db: Session, *, obj_in: UserCreate) -> User:
    unique_id = generate_unique_id(db, obj_in.user_type)
    
    db_obj = UserModel(
        user_id=unique_id,
        user_name=obj_in.user_name,
        user_pwd=get_password_hash(obj_in.user_pwd),
        user_type=obj_in.user_type
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return User.model_validate(db_obj)

# Service层 - 带审计装饰器
@audit("User", "CREATE")
def create_user(db: Session, obj_in: UserCreate, audit_context=None) -> User:
    """Create a new user"""
    if obj_in.user_type == "customer":
        user_obj = customer.create(db, obj_in=obj_in)
    elif obj_in.user_type == "worker":
        wage_obj = wage.get_by_type(db, obj_in.worker_type)
        if not wage_obj:
            raise ValueError(f"Unsupported worker type: {obj_in.worker_type}")
        user_obj = worker.create(db, obj_in=obj_in)
    elif obj_in.user_type == "administrator":
        user_obj = admin.create(db, obj_in=obj_in)
    else:
        raise ValueError(f"Invalid user type: {obj_in.user_type}")
    return user_obj
```

**等价SQL实现：**
```sql
-- 创建用户（生成唯一ID，使用bcrypt密码哈希）
-- 注意：实际使用bcrypt哈希，这里用伪代码表示
INSERT INTO User (user_id, user_name, user_pwd, user_type) 
VALUES (CONCAT(LEFT(UPPER('类型'), 1), UNIX_TIMESTAMP(NOW(6)), 
               UPPER(SUBSTRING(MD5(RAND()), 1, 3))), 
        '用户名', '$bcrypt$hashed_password', '用户类型');

-- 用户认证查询（密码验证在应用层使用bcrypt进行）
SELECT user_id, user_name, user_type, user_pwd
FROM User 
WHERE user_name = '输入用户名';
-- 然后在应用层使用: bcrypt.verify('输入密码', stored_hash)

-- 创建客户时的完整事务
START TRANSACTION;
INSERT INTO User (user_id, user_name, user_pwd, user_type) VALUES (...);
INSERT INTO Customer (user_id) VALUES (LAST_INSERT_ID());
COMMIT;

-- 创建维修人员时的完整事务（需要验证工种）
START TRANSACTION;
SELECT COUNT(*) FROM Wage WHERE worker_type = '指定工种'; -- 验证工种存在
INSERT INTO User (user_id, user_name, user_pwd, user_type) VALUES (...);
INSERT INTO Worker (user_id, worker_type, availability_status) 
VALUES (LAST_INSERT_ID(), '工种', 1);
COMMIT;
```

### 3.2 维修工单管理

**ORM实现：**
```python
# CRUD层
def create_order_for_customer(self, db: Session, *, obj_in: OrderCreate, customer_id: str) -> Order:
    # 生成唯一订单ID
    from datetime import datetime
    import random
    import string
    now = datetime.now()
    random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
    order_id = f"O{now.strftime('%y%m%d')}{random_suffix}"

    db_obj = ServiceOrderModel(
        order_id=order_id,
        description=obj_in.description,
        start_time=obj_in.start_time,
        end_time=None,
        car_id=obj_in.car_id,
        customer_id=customer_id,
        status=OrderStatus.PENDING_ASSIGNMENT,
        rating=None,
        worker_id=None,
        comment=None,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return Order.model_validate(db_obj)

# Service层 - 带审计装饰器和自动分配
@audit("Order", "CREATE")
def create_order(db: Session, obj_in: OrderCreate, customer_id: str, audit_context=None) -> Order:
    """Create a new service order"""
    order_obj = order.create_order_for_customer(db=db, obj_in=obj_in, customer_id=customer_id)
    from app.services.assignment_service import AutoAssignmentService
    AutoAssignmentService.trigger_assignment(db, order_obj.order_id)
    return order_obj
```

**等价SQL实现：**
```sql
-- 创建工单（对应OrderService.create_order实现）
-- 1. 生成唯一ID（基于时间戳的ID生成算法）
SET @order_id = CONCAT('O', UNIX_TIMESTAMP(NOW(6)), UPPER(SUBSTRING(MD5(RAND()), 1, 3)));

-- 2. 验证客户和车辆的关联关系
SELECT COUNT(*) as valid_car 
FROM Car c
JOIN Customer cu ON c.customer_id = cu.user_id
WHERE c.car_id = '车辆ID' AND cu.user_id = '客户ID';

-- 3. 插入工单记录（使用事务确保数据一致性）
START TRANSACTION;

INSERT INTO ServiceOrder (
    order_id, description, start_time, end_time, car_id, customer_id, 
    status, rating, worker_id, comment, created_at, updated_at, total_cost
) VALUES (
    @order_id, '维修描述', NULL, NULL, '车辆ID', '客户ID', 
    1, NULL, NULL, NULL, NOW(), NOW(), 0
);

-- 4. 自动分配维修人员（对应AutoAssignmentService.trigger_assignment）
-- 首先获取车辆类型以确定所需工种
SELECT c.car_type INTO @required_worker_type
FROM ServiceOrder so
JOIN Car c ON so.car_id = c.car_id
WHERE so.order_id = @order_id;

-- 查找可用维修人员（考虑工作负载）
SELECT w.user_id INTO @selected_worker
FROM Worker w
LEFT JOIN (
    SELECT worker_id, COUNT(*) as workload
    FROM ServiceOrder
    WHERE status IN (1, 2)  -- 待分配或已分配
    GROUP BY worker_id
) wl ON w.user_id = wl.worker_id
WHERE w.worker_type = @required_worker_type 
    AND w.availability_status = 1
ORDER BY COALESCE(wl.workload, 0) ASC, RAND()
LIMIT 1;

-- 执行分配
IF @selected_worker IS NOT NULL THEN
    UPDATE ServiceOrder 
    SET worker_id = @selected_worker, 
        status = 2,
        updated_at = NOW()
    WHERE order_id = @order_id AND status = 1;
    
    -- 更新工人状态（基于工作负载）
    UPDATE Worker 
    SET availability_status = CASE 
        WHEN (
            SELECT COUNT(*) 
            FROM ServiceOrder 
            WHERE worker_id = @selected_worker AND status IN (1, 2)
        ) >= 5 THEN 0  -- 工单数达到上限设为忙碌
        ELSE 1
    END
    WHERE user_id = @selected_worker;
END IF;

COMMIT;

-- 5. 返回创建的工单信息
SELECT * FROM ServiceOrder WHERE order_id = @order_id;
```

### 3.3 维修进度跟踪和费用计算

**ORM实现：**
```python
# CRUD
def complete_order(self, db: Session, order_id: str, total_cost: Decimal) -> Order:
    db_obj = db.query(ServiceOrderModel).filter_by(order_id=order_id).first()
    if db_obj:
        db_obj.status = OrderStatus.COMPLETED
        db_obj.end_time = datetime.now()
        db_obj.total_cost = total_cost
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
    return Order.model_validate(db_obj)

# Service
def complete_order(db: Session, order_id: str, worker_id: str, audit_context=None) -> Order:
    order_obj = order.get_by_order_id(db, order_id=order_id)
    if not order_obj:
        raise ValueError("Order not found")
    if order_obj.worker_id != worker_id:
        raise ValueError("Order is not assigned to this worker")
    procedures = procedure.get_procedures_by_order(db, order_id=order_id)      
    for procedure_obj in procedures:
        if procedure_obj.current_status != ProcedureStatus.COMPLETED:
            raise ValueError(f"Procedure {procedure_obj.procedure_id} is not in completed state")
    # 维修费用计算
    total_cost = log.get_total_cost_by_order(db, order_id=order_id)
    return order.complete_order(db, order_id=order_id, total_cost=total_cost)
```

**等价SQL实现：**
```sql
-- 完成工单前检查所有维修程序是否完成
SELECT COUNT(*) FROM MaintenanceProcedure 
WHERE order_id = '工单ID' AND current_status != 4;

-- 计算总费用（对应log.get_total_cost_by_order实现）
-- 注意：实际系统中total_cost直接由业务逻辑计算，这里展示等价SQL逻辑
SET @total_cost = (
    SELECT COALESCE(SUM(
        CASE 
            WHEN mp.current_status = 4 THEN COALESCE(mp.cost, 0)  -- 只计算已完成的维修程序费用
            ELSE 0 
        END
    ), 0)
    FROM ServiceOrder so
    LEFT JOIN MaintenanceProcedure mp ON so.order_id = mp.order_id
    WHERE so.order_id = '工单ID'
);

-- 可选：如果系统有独立的工时费用记录
SET @labor_cost = (
    SELECT COALESCE(SUM(wl.hours_worked * w.wage_per_hour), 0)
    FROM ServiceOrder so
    LEFT JOIN WorkLog wl ON so.order_id = wl.order_id
    LEFT JOIN Worker wk ON wl.worker_id = wk.user_id
    LEFT JOIN Wage w ON wk.worker_type = w.worker_type
    WHERE so.order_id = '工单ID'
);

-- 实际使用中，total_cost是从业务逻辑传递的参数
SET @final_total_cost = @total_cost + COALESCE(@labor_cost, 0);

-- 完成工单（对应OrderService.complete_order实现）
-- 验证工单状态和工人权限
SELECT worker_id, status INTO @assigned_worker, @current_status
FROM ServiceOrder 
WHERE order_id = '工单ID';

-- 确保只有分配给该工人且状态正确的工单才能完成
IF @assigned_worker = '工人ID' AND @current_status = 3 THEN
    START TRANSACTION;
    
    -- 更新工单状态
    UPDATE ServiceOrder 
    SET status = 4, 
        end_time = NOW(), 
        total_cost = @final_total_cost,
        updated_at = NOW()
    WHERE order_id = '工单ID' AND worker_id = '工人ID';
    
    -- 释放维修人员（更新可用状态）
    UPDATE Worker 
    SET availability_status = 1
    WHERE user_id = '工人ID';
    
    COMMIT;
    
    -- 返回更新后的工单信息
    SELECT * FROM ServiceOrder WHERE order_id = '工单ID';
ELSE
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Order completion validation failed';
END IF;
```

## 四、"触发器"功能的Python实现

### 4.1 审计装饰器 - 数据变更追踪

我们通过`@audit`装饰器实现了数据库触发器的功能：

```python
# 实际的审计装饰器使用示例
@audit("Order", "CREATE")
def create_order(db: Session, obj_in: OrderCreate, customer_id: str, audit_context=None) -> Order:
    """Create a new service order"""
    order_obj = order.create_order_for_customer(db=db, obj_in=obj_in, customer_id=customer_id)
    from app.services.assignment_service import AutoAssignmentService
    AutoAssignmentService.trigger_assignment(db, order_obj.order_id)
    return order_obj

@audit("Order", "UPDATE")
def update_order_status(db: Session, order_id: str, new_status: int, audit_context=None) -> Order:
    """Update the status of an order"""
    valid_statuses = [OrderStatus.PENDING_ASSIGNMENT, OrderStatus.IN_PROGRESS, OrderStatus.COMPLETED]
    if new_status not in valid_statuses:
        raise ValueError(f"Invalid status: {new_status}")
    return order.update_order_status(db, order_id=order_id, new_status=new_status)

@audit("User", "CREATE")  
def create_user(db: Session, obj_in: UserCreate, audit_context=None) -> User:
    """Create a new user"""
    if obj_in.user_type == "customer":
        user_obj = customer.create(db, obj_in=obj_in)
    elif obj_in.user_type == "worker":
        wage_obj = wage.get_by_type(db, obj_in.worker_type)
        if not wage_obj:
            raise ValueError(f"Unsupported worker type: {obj_in.worker_type}")
        user_obj = worker.create(db, obj_in=obj_in)
    elif obj_in.user_type == "administrator":
        user_obj = admin.create(db, obj_in=obj_in)
    else:
        raise ValueError(f"Invalid user type: {obj_in.user_type}")
    return user_obj
```

**触发器等价功能：**
- **数据变更前记录**：保存修改前的数据状态
- **数据变更后记录**：记录新的数据状态
- **操作审计日志**：自动记录操作者、时间、变更内容

**等价SQL触发器：**
```sql
-- 创建审计日志表
CREATE TABLE AuditLog (
    log_id VARCHAR(36) PRIMARY KEY,
    table_name VARCHAR(50),
    record_id VARCHAR(50),
    operation VARCHAR(10),
    old_data JSON,
    new_data JSON,
    changed_by VARCHAR(50),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 订单更新触发器
DELIMITER $$
CREATE TRIGGER order_audit_trigger
AFTER UPDATE ON ServiceOrder
FOR EACH ROW
BEGIN
    INSERT INTO AuditLog (
        log_id, table_name, record_id, operation, 
        old_data, new_data, changed_by, changed_at
    ) VALUES (
        UUID(),
        'ServiceOrder',
        NEW.order_id,
        'UPDATE',
        JSON_OBJECT('status', OLD.status, 'end_time', OLD.end_time),
        JSON_OBJECT('status', NEW.status, 'end_time', NEW.end_time),
        USER(),
        NOW()
    );
END$$
DELIMITER ;
```

### 4.2 自动工单分配服务

```python
class AutoAssignmentService:
    """Service for automatic order assignment to available workers"""
    
    @staticmethod
    def trigger_assignment(db: Session, order_id: str) -> bool:
        """Ultra-simple random assignment - no separate tracking needed"""
        order_obj = order.get_by_order_id(db, order_id)
        if not order_obj or order_obj.status != OrderStatus.PENDING_ASSIGNMENT:
            return False
        
        # Find all available workers
        available_workers = worker.get_available_workers(db)
        
        if not available_workers:
            return False
        
        # Random selection
        selected_worker = random.choice(available_workers)
        
        # Update order: assign worker, set status to assigned
        order.update_order_assignment(db, order_id=order_id, worker_id=selected_worker.user_id, status=OrderStatus.ASSIGNED)
        
        # Update worker's availability status
        worker.update_availability(db, worker_id=selected_worker.user_id, status=WorkerAvailabilityStatus.BUSY)
        
        return True
    
    @staticmethod
    def handle_rejection(db: Session, order_id: str) -> bool:
        """Handle order rejection and trigger reassignment"""
        order_obj = order.get_by_order_id(db, order_id)
        if not order_obj:
            return False
                
        # Update worker's availability status
        if order_obj.worker_id:
            worker.update_availability(db, worker_id=order_obj.worker_id, status=WorkerAvailabilityStatus.AVAILABLE)
        
        order.update_order_assignment(db, order_id=order_id, worker_id=None, status=OrderStatus.PENDING_ASSIGNMENT)
        
        # Try to reassign to another worker
        return AutoAssignmentService.trigger_assignment(db, order_id)
    
    @staticmethod
    def handle_acceptance(db: Session, order_id: str, worker_id: str) -> bool:
        """Handle order acceptance - update status to in_progress"""
        order_obj = order.get_by_order_id(db, order_id)
        if not order_obj or order_obj.worker_id != worker_id:
            return False
        
        order.update_order_status(db, order_id=order_id, new_status=OrderStatus.IN_PROGRESS)
        
        return True
```

**等价SQL存储过程：**
```sql
DELIMITER $$
CREATE PROCEDURE AutoAssignOrder(IN p_order_id VARCHAR(10))
BEGIN
    DECLARE v_worker_id VARCHAR(10);
    DECLARE v_worker_count INT;
    DECLARE v_required_worker_type VARCHAR(50);
    
    -- 获取工单需要的工种类型
    SELECT c.car_type INTO v_required_worker_type
    FROM ServiceOrder so
    JOIN Car c ON so.car_id = c.car_id
    WHERE so.order_id = p_order_id;
    
    -- 查找该工种的可用维修人员（考虑工作负载）
    SELECT COUNT(*) INTO v_worker_count 
    FROM Worker w
    WHERE w.worker_type = v_required_worker_type 
        AND w.availability_status = 1;
    
    IF v_worker_count > 0 THEN
        -- 选择工作负载最轻的维修人员
        SELECT w.user_id INTO v_worker_id
        FROM Worker w
        LEFT JOIN (
            SELECT worker_id, COUNT(*) as workload
            FROM ServiceOrder
            WHERE status IN (1, 2)  -- 待分配或已分配
            GROUP BY worker_id
        ) wl ON w.user_id = wl.worker_id
        WHERE w.worker_type = v_required_worker_type 
            AND w.availability_status = 1
        ORDER BY COALESCE(wl.workload, 0) ASC, RAND()
        LIMIT 1;
        
        -- 分配工单
        UPDATE ServiceOrder 
        SET worker_id = v_worker_id, status = 2, updated_at = NOW()
        WHERE order_id = p_order_id AND status = 1;
        
        -- 根据工作负载更新维修人员状态
        UPDATE Worker 
        SET availability_status = CASE 
            WHEN (
                SELECT COUNT(*) 
                FROM ServiceOrder 
                WHERE worker_id = v_worker_id AND status IN (1, 2)
            ) >= 5 THEN 0  -- 工单数达到上限设为忙碌
            ELSE 1
        END
        WHERE user_id = v_worker_id;
    END IF;
END$$

-- 拒绝工单处理
CREATE PROCEDURE RejectOrderAssignment(IN p_order_id VARCHAR(10), IN p_worker_id VARCHAR(10))
BEGIN
    -- 重置工单状态
    UPDATE ServiceOrder 
    SET status = 1, worker_id = NULL, updated_at = NOW()
    WHERE order_id = p_order_id AND worker_id = p_worker_id;
    
    -- 更新工人可用状态
    UPDATE Worker 
    SET availability_status = 1
    WHERE user_id = p_worker_id;
    
    -- 尝试重新分配
    CALL AutoAssignOrder(p_order_id);
END$$

-- 接受工单处理
CREATE PROCEDURE AcceptOrderAssignment(IN p_order_id VARCHAR(10), IN p_worker_id VARCHAR(10))
BEGIN
    UPDATE ServiceOrder 
    SET status = 3, start_time = NOW(), updated_at = NOW()
    WHERE order_id = p_order_id AND worker_id = p_worker_id AND status = 2;
END$$
DELIMITER ;
```

### 4.3 定时工资结算调度器

```python
class EarningScheduler:
    """Service for managing scheduled tasks"""

    def __init__(self):
        self.running = False
        self.scheduler_thread: Optional[threading.Thread] = None
        self.tasks = []

    def add_monthly_task(self, task_name: str, day_of_month: int, hour: int = 0, minute: int = 0):
        """Add a task to run monthly on a specific day"""
        self.tasks.append({
            "name": task_name,
            "type": "monthly",
            "day_of_month": day_of_month,
            "hour": hour,
            "minute": minute,
            "last_run": None
        })

    def _run_monthly_earnings_distribution(self, current_time: datetime):
        """Run the monthly earnings distribution for the previous month"""
        # Calculate previous month
        if current_time.month == 1:
            prev_month = 12
            prev_year = current_time.year - 1
        else:
            prev_month = current_time.month - 1
            prev_year = current_time.year
        
        # Get database session
        db = next(get_db())
        
        try:
            # Create audit context for the scheduler
            audit_context = ChangeTrackingContext(
                user_id="SCHEDULER"
            )
            
            # Process monthly earnings
            result = EarningsService.process_monthly_earnings_distribution(
                db=db, 
                year=prev_year, 
                month=prev_month,
                audit_context=audit_context
            )
            
            logger.info(
                f"Monthly earnings distribution completed for {prev_year}-{prev_month:02d}: "
                f"{result.successful_distributions} successful, "
                f"{result.failed_distributions} failed, "
                f"${result.total_amount_distributed} distributed"
            )
            
        except Exception as e:
            logger.error(f"Failed to run monthly earnings distribution: {e}")
        finally:
            db.close()
```

**等价SQL定时任务：**
```sql
-- 创建工资计算存储过程（对应EarningsService.process_monthly_earnings_distribution）
DELIMITER $$
CREATE PROCEDURE CalculateMonthlyEarnings(IN p_year INT, IN p_month INT)
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE v_worker_id VARCHAR(10);
    DECLARE v_total_hours DECIMAL(10,2);
    DECLARE v_hourly_rate DECIMAL(10,2);
    DECLARE v_total_earnings DECIMAL(10,2);
    DECLARE v_distribution_id VARCHAR(36);
    DECLARE v_error_count INT DEFAULT 0;
    DECLARE v_success_count INT DEFAULT 0;
    
    DECLARE worker_cursor CURSOR FOR
        SELECT DISTINCT w.user_id
        FROM Worker w
        JOIN ServiceOrder so ON w.user_id = so.worker_id
        WHERE YEAR(so.end_time) = p_year 
        AND MONTH(so.end_time) = p_month
        AND so.status = 4;
    
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
    DECLARE CONTINUE HANDLER FOR SQLEXCEPTION 
    BEGIN
        SET v_error_count = v_error_count + 1;
        -- 记录错误但继续处理下一个工人
        INSERT INTO ErrorLog (error_msg, worker_id, created_at) 
        VALUES (CONCAT('Failed to calculate earnings for worker: ', v_worker_id), v_worker_id, NOW());
    END;
    
    -- 检查是否已经处理过该月份
    IF EXISTS (
        SELECT 1 FROM WorkerDistribution 
        WHERE distribution_year = p_year 
        AND distribution_month = p_month
    ) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Monthly earnings already processed for this period';
    END IF;
    
    START TRANSACTION;
    
    OPEN worker_cursor;
    
    read_loop: LOOP
        FETCH worker_cursor INTO v_worker_id;
        IF done THEN
            LEAVE read_loop;
        END IF;
        
        -- 计算工时（完成工单的实际工作时长）
        SELECT 
            COALESCE(SUM(TIMESTAMPDIFF(HOUR, so.start_time, so.end_time)), 0) 
        INTO v_total_hours
        FROM ServiceOrder so
        WHERE so.worker_id = v_worker_id
        AND YEAR(so.end_time) = p_year 
        AND MONTH(so.end_time) = p_month
        AND so.status = 4
        AND so.start_time IS NOT NULL 
        AND so.end_time IS NOT NULL;
        
        -- 获取时薪
        SELECT w.wage_per_hour INTO v_hourly_rate
        FROM Worker wk
        JOIN Wage w ON wk.worker_type = w.worker_type
        WHERE wk.user_id = v_worker_id;
        
        -- 只有工作时长大于0才发放工资
        IF v_total_hours > 0 THEN
            SET v_total_earnings = v_total_hours * v_hourly_rate;
            SET v_distribution_id = UUID();
            
            -- 插入工资记录（对应WorkerDistribution模型）
            INSERT INTO WorkerDistribution (
                distribution_id, worker_id, amount, 
                distribution_month, distribution_year, 
                hours_worked, hourly_rate,
                created_at, created_by
            ) VALUES (
                v_distribution_id, v_worker_id, v_total_earnings, 
                p_month, p_year, 
                v_total_hours, v_hourly_rate,
                NOW(), 'SCHEDULER'
            );
            
            SET v_success_count = v_success_count + 1;
        END IF;
        
    END LOOP;
    
    CLOSE worker_cursor;
    
    -- 记录处理结果
    INSERT INTO EarningsProcessingLog (
        processing_id, year, month, 
        successful_distributions, failed_distributions,
        total_amount_distributed, processed_at
    ) SELECT 
        UUID(), p_year, p_month,
        v_success_count, v_error_count,
        SUM(amount), NOW()
    FROM WorkerDistribution 
    WHERE distribution_year = p_year AND distribution_month = p_month;
    
    COMMIT;
END$$
DELIMITER ;

-- 创建定时事件（对应EarningScheduler调度）
CREATE EVENT monthly_earnings_calculation
ON SCHEDULE EVERY 1 MONTH
STARTS '2024-02-01 02:00:00'
COMMENT '每月自动工资计算和分发'
DO 
BEGIN
    DECLARE v_prev_month INT;
    DECLARE v_prev_year INT;
    
    -- 计算上个月的年月
    SET v_prev_month = MONTH(DATE_SUB(NOW(), INTERVAL 1 MONTH));
    SET v_prev_year = YEAR(DATE_SUB(NOW(), INTERVAL 1 MONTH));
    
    CALL CalculateMonthlyEarnings(v_prev_year, v_prev_month);
END;
```

## 五、复杂查询和统计分析功能

### 5.1 车型维修统计分析

**ORM实现：**
```python
def get_car_type_statistics(db: Session) -> List[CarTypeStatistics]:
    car_types = car.get_all_car_types(db)
    result = []
    
    for car_type_name in car_types:
        repair_count = order.count_orders_by_car_type(db, car_type_name)
        avg_cost = order.get_average_cost_by_car_type(db, car_type_name)
        
        stats = CarTypeStatistics(
            car_type=car_type_name,
            repair_count=repair_count,
            average_repair_cost=avg_cost
        )
        result.append(stats)
    
    return result
```

**等价SQL查询：**
```sql
-- 车型维修统计（对应AdminService.get_car_type_statistics）
SELECT 
    ct.car_type,
    COUNT(DISTINCT c.car_id) as car_count,
    COUNT(so.order_id) as repair_count,
    AVG(CASE WHEN so.status = 4 THEN so.total_cost END) as average_repair_cost,
    SUM(CASE WHEN so.status = 4 THEN so.total_cost ELSE 0 END) as total_repair_cost,
    (COUNT(so.order_id) * 100.0 / NULLIF(COUNT(DISTINCT c.car_id), 0)) as repair_frequency
FROM CarType ct
LEFT JOIN Car c ON ct.car_type = c.car_type
LEFT JOIN ServiceOrder so ON c.car_id = so.car_id
GROUP BY ct.car_type
ORDER BY repair_count DESC;

-- 获取所有车型（get_all_car_types的实际调用）
SELECT DISTINCT car_type FROM CarType;

-- 按车型统计维修次数（count_orders_by_car_type的实际实现）
SELECT COUNT(so.order_id)
FROM ServiceOrder so
JOIN Car c ON so.car_id = c.car_id
WHERE c.car_type = '指定车型';
```

### 5.2 维修人员绩效分析

**ORM实现：**
```python
def get_worker_productivity_analysis(db: Session, start_date: str, end_date: str) -> List[WorkerProductivityAnalysis]:
    worker_types = user.get_all_worker_types(db)
    result = []
    
    for worker_type in worker_types:
        completion_rate = order.get_completion_rate_by_worker_type(db, worker_type, start_dt, end_dt)
        avg_completion_time = order.get_average_completion_time_by_worker_type(db, worker_type, start_dt, end_dt)
        customer_satisfaction = order.get_average_rating_by_worker_type(db, worker_type, start_dt, end_dt)
        
        productivity = WorkerProductivityAnalysis(
            worker_type=worker_type,
            completion_rate_percentage=completion_rate,
            average_completion_time_hours=avg_completion_time,
            average_customer_rating=customer_satisfaction,
            productivity_score=(completion_rate * customer_satisfaction) / 5
        )
        result.append(productivity)
    
    return result
```

**等价SQL查询：**
```sql
-- 维修人员绩效统计（对应AdminService.get_worker_productivity_analysis）
-- 1. 获取所有工种
SELECT DISTINCT worker_type FROM Worker;

-- 2. 按工种统计绩效指标
SELECT 
    w.worker_type,
    COUNT(so.order_id) as total_assigned,
    COUNT(CASE WHEN so.status = 4 THEN 1 END) as completed_orders,
    (COUNT(CASE WHEN so.status = 4 THEN 1 END) * 100.0 / NULLIF(COUNT(so.order_id), 0)) as completion_rate,
    AVG(CASE 
        WHEN so.status = 4 THEN 
            TIMESTAMPDIFF(HOUR, so.start_time, so.end_time) 
        END) as avg_completion_hours,
    AVG(CASE WHEN so.status = 4 THEN so.rating END) as avg_customer_rating,
    ((COUNT(CASE WHEN so.status = 4 THEN 1 END) * 100.0 / NULLIF(COUNT(so.order_id), 0)) * 
     COALESCE(AVG(CASE WHEN so.status = 4 THEN so.rating END), 0) / 5) as productivity_score
FROM Worker w
LEFT JOIN ServiceOrder so ON w.user_id = so.worker_id
    AND so.start_time BETWEEN '开始日期' AND '结束日期'
GROUP BY w.worker_type
ORDER BY productivity_score DESC;

-- 3. 分别调用的查询方法
-- 完成率查询（get_completion_rate_by_worker_type）
SELECT 
    (COUNT(CASE WHEN so.status = 4 THEN 1 END) * 100.0 / NULLIF(COUNT(so.order_id), 0)) as completion_rate
FROM Worker w
LEFT JOIN ServiceOrder so ON w.user_id = so.worker_id
WHERE w.worker_type = '指定工种' 
    AND so.start_time BETWEEN '开始日期' AND '结束日期';

-- 平均完成时间查询（get_average_completion_time_by_worker_type）
SELECT AVG(TIMESTAMPDIFF(HOUR, so.start_time, so.end_time)) as avg_hours
FROM Worker w
JOIN ServiceOrder so ON w.user_id = so.worker_id
WHERE w.worker_type = '指定工种' 
    AND so.status = 4
    AND so.start_time BETWEEN '开始日期' AND '结束日期';

-- 客户满意度查询（get_average_rating_by_worker_type）
SELECT AVG(so.rating) as avg_rating
FROM Worker w
JOIN ServiceOrder so ON w.user_id = so.worker_id
WHERE w.worker_type = '指定工种' 
    AND so.status = 4
    AND so.rating IS NOT NULL
    AND so.start_time BETWEEN '开始日期' AND '结束日期';
```

### 5.3 成本分析按时间周期

**ORM实现：**
```python
def get_cost_analysis_by_period(db: Session, start_date: str, end_date: str, period_type: str = "month") -> CostAnalysisByPeriod:
    period_breakdown = []
    
    # 按月份分组统计
    for period_start, period_end in generate_periods(start_dt, end_dt, period_type):
        material_cost = procedure.get_total_material_cost_by_period(db, period_start, period_end)
        labor_cost = log.get_total_labor_cost_by_period(db, period_start, period_end)
        
        period_data = PeriodCostData(
            period_label=period_start.strftime("%Y-%m"),
            material_cost=material_cost,
            labor_cost=labor_cost,
            total_cost=material_cost + labor_cost
        )
        period_breakdown.append(period_data)
    
    return CostAnalysisByPeriod(period_breakdown=period_breakdown)
```

**等价SQL查询：**
```sql
-- 按月份统计成本分析（对应AdminService.get_cost_analysis_by_period）
-- 1. 材料费用分解（get_material_cost_breakdown_by_period）
SELECT 
    DATE_FORMAT(so.end_time, '%Y-%m') as period_label,
    SUM(COALESCE(so.total_cost, 0)) as material_cost
FROM ServiceOrder so
WHERE so.end_time BETWEEN '开始日期' AND '结束日期'
    AND so.total_cost IS NOT NULL
    AND so.status = 4
GROUP BY DATE_FORMAT(so.end_time, '%Y-%m')
ORDER BY period_label;

-- 2. 工时费用分解（get_labor_cost_breakdown_by_period）
SELECT 
    DATE_FORMAT(d.created_at, '%Y-%m') as period_label,
    SUM(d.amount) as labor_cost
FROM WorkerDistribution d
WHERE d.created_at BETWEEN '开始日期' AND '结束日期'
GROUP BY DATE_FORMAT(d.created_at, '%Y-%m')
ORDER BY period_label;

-- 3. 综合成本分析（完整版本）
WITH MaterialCosts AS (
    SELECT 
        DATE_FORMAT(so.end_time, '%Y-%m') as period,
        SUM(COALESCE(so.total_cost, 0)) as material_cost
    FROM ServiceOrder so
    WHERE so.end_time BETWEEN '开始日期' AND '结束日期'
        AND so.status = 4
    GROUP BY DATE_FORMAT(so.end_time, '%Y-%m')
),
LaborCosts AS (
    SELECT 
        DATE_FORMAT(d.created_at, '%Y-%m') as period,
        SUM(d.amount) as labor_cost
    FROM WorkerDistribution d
    WHERE d.created_at BETWEEN '开始日期' AND '结束日期'
    GROUP BY DATE_FORMAT(d.created_at, '%Y-%m')
)
SELECT 
    COALESCE(m.period, l.period) as period_label,
    COALESCE(m.material_cost, 0) as material_cost,
    COALESCE(l.labor_cost, 0) as labor_cost,
    (COALESCE(m.material_cost, 0) + COALESCE(l.labor_cost, 0)) as total_cost,
    CASE 
        WHEN COALESCE(m.material_cost, 0) > 0 
        THEN COALESCE(l.labor_cost, 0) / m.material_cost 
        ELSE 0 
    END as labor_material_ratio
FROM MaterialCosts m
FULL OUTER JOIN LaborCosts l ON m.period = l.period
ORDER BY period_label;

-- 4. 按季度统计（当period_type='quarter'时）
SELECT 
    CONCAT(YEAR(so.end_time), '-Q', CEILING(MONTH(so.end_time)/3.0)) as period_label,
    SUM(COALESCE(so.total_cost, 0)) as material_cost
FROM ServiceOrder so
WHERE so.end_time BETWEEN '开始日期' AND '结束日期'
    AND so.status = 4
GROUP BY YEAR(so.end_time), CEILING(MONTH(so.end_time)/3.0)
ORDER BY period_label;
```

### 5.4 负面反馈分析

**ORM实现：**
```python
def get_negative_feedback_analysis(db: Session, rating_threshold: int = 3) -> NegativeFeedbackAnalysis:
    low_rated_orders = order.get_orders_by_rating_threshold(db, rating_threshold)
    worker_feedback_summary = {}
    
    for order_item in low_rated_orders:
        if order_item.worker_id not in worker_feedback_summary:
            total_orders = order.count_completed_orders_by_worker(db, order_item.worker_id)
            avg_rating = order.get_average_rating_by_worker(db, order_item.worker_id)
            
            worker_feedback_summary[order_item.worker_id] = WorkerPerformanceSummary(
                worker_id=order_item.worker_id,
                low_rating_count=1,
                total_completed_orders=total_orders,
                average_rating=avg_rating
            )
        else:
            worker_feedback_summary[order_item.worker_id].low_rating_count += 1
    
    return NegativeFeedbackAnalysis(
        low_rated_orders=low_rated_orders,
        worker_performance_summary=list(worker_feedback_summary.values())
    )
```

**等价SQL查询：**
```sql
-- 负面反馈分析
WITH LowRatedOrders AS (
    SELECT so.*, w.worker_type
    FROM ServiceOrder so
    JOIN Worker w ON so.worker_id = w.user_id
    WHERE so.rating <= 3 AND so.rating IS NOT NULL
),
WorkerStats AS (
    SELECT 
        w.user_id as worker_id,
        w.worker_type,
        COUNT(so.order_id) as total_orders,
        AVG(so.rating) as avg_rating,
        COUNT(CASE WHEN so.rating <= 3 THEN 1 END) as low_rating_count
    FROM Worker w
    LEFT JOIN ServiceOrder so ON w.user_id = so.worker_id AND so.status = 4
    GROUP BY w.user_id, w.worker_type
)
SELECT 
    ws.worker_id,
    ws.worker_type,
    ws.total_orders,
    ws.avg_rating,
    ws.low_rating_count,
    (ws.low_rating_count * 100.0 / ws.total_orders) as low_rating_percentage
FROM WorkerStats ws
WHERE ws.low_rating_count > 0
ORDER BY low_rating_percentage DESC;
```

## 六、数据维护和事务控制

### 6.1 批量工单处理事务

**ORM实现：**
```python
# 注意：我们的ORM使用隐式事务管理，每个db.commit()都是一个事务
# 以下是批量处理的概念性示例（实际项目中主要通过单个操作实现）
def batch_create_orders_concept(db: Session, orders_data: List[OrderCreate], customer_id: str) -> List[Order]:
    """概念性的批量创建订单示例"""
    created_orders = []
    
    try:
        # 在我们的实现中，每个create_order调用内部都有完整的事务管理
        for order_data in orders_data:
            # 通过服务层创建订单（包含审计和自动分配）
            order_obj = OrderService.create_order(db, obj_in=order_data, customer_id=customer_id)
            created_orders.append(order_obj)
        
        return created_orders
        
    except Exception as e:
        # 错误处理由各个服务层方法内部管理
        raise e

# 实际的创建订单方法（带事务和审计）
@audit("Order", "CREATE")
def create_order(db: Session, obj_in: OrderCreate, customer_id: str, audit_context=None) -> Order:
    """Create a new service order"""
    # CRUD层创建 + 自动分配都在一个逻辑事务中
    order_obj = order.create_order_for_customer(db=db, obj_in=obj_in, customer_id=customer_id)
    from app.services.assignment_service import AutoAssignmentService
    AutoAssignmentService.trigger_assignment(db, order_obj.order_id)
    return order_obj
```

**等价SQL事务：**
```sql
START TRANSACTION;

-- 创建多个工单
INSERT INTO ServiceOrder (order_id, description, start_time, car_id, customer_id, status)
VALUES 
    ('O240101001', '描述1', NOW(), 'C001', 'U001', 1),
    ('O240101002', '描述2', NOW(), 'C002', 'U001', 1),
    ('O240101003', '描述3', NOW(), 'C003', 'U001', 1);

-- 为每个工单分配维修人员
UPDATE ServiceOrder so
JOIN (
    SELECT 
        so.order_id,
        (SELECT user_id FROM Worker WHERE availability_status = 1 ORDER BY RAND() LIMIT 1) as assigned_worker
    FROM ServiceOrder so
    WHERE so.order_id IN ('O240101001', 'O240101002', 'O240101003')
) assignments ON so.order_id = assignments.order_id
SET so.worker_id = assignments.assigned_worker, so.status = 2;

-- 更新维修人员状态
UPDATE Worker 
SET availability_status = 2 
WHERE user_id IN (
    SELECT DISTINCT worker_id FROM ServiceOrder 
    WHERE order_id IN ('O240101001', 'O240101002', 'O240101003')
);

COMMIT;
```

### 6.2 数据变更历史追踪

通过审计装饰器实现的数据变更追踪：

```python
# 审计装饰器的实际实现核心逻辑
def _execute_with_audit(func: Callable, table_name: str, operation: str, *args, **kwargs):
    """Core audit execution logic - separated for clarity"""
    # 验证session
    db = args[0] if args else kwargs.get('db')
    if not isinstance(db, Session):
        raise ValueError("db is not a valid session")
    
    # 提取上下文
    context = kwargs.get('audit_context') or kwargs.get('context')
    
    # 执行前: 获取更新操作的旧数据
    old_data = None
    if operation == "UPDATE":
        record_id = SimpleIdExtractor.extract_id(table_name, *args, **kwargs)
        if record_id:
            old_data = _get_old_data(db, table_name, record_id)
    
    # 执行原始函数
    result = func(*args, **kwargs)
    
    # 执行后: 记录变更
    try:
        _args = args[1:]    
        _kwargs = kwargs.copy()
        _kwargs.pop('db', None)
        _log_audit_change(db, table_name, operation, old_data, result, context, *_args, **_kwargs)
    except Exception as e:
        # 不要因为审计失败而影响业务操作
        print(f"Audit logging failed: {e}")
    
    return result

@audit("Order", "UPDATE")
def update_order_status(db: Session, order_id: str, new_status: int, audit_context=None) -> Order:
    """Update the status of an order"""
    # 装饰器自动在执行前记录旧数据，执行后记录新数据
    valid_statuses = [OrderStatus.PENDING_ASSIGNMENT, OrderStatus.IN_PROGRESS, OrderStatus.COMPLETED]
    if new_status not in valid_statuses:
        raise ValueError(f"Invalid status: {new_status}")
    
    return order.update_order_status(db, order_id=order_id, new_status=new_status)
```

**等价SQL实现：**
```sql
-- 手动记录变更历史的存储过程
DELIMITER $$
CREATE PROCEDURE UpdateOrderWithAudit(
    IN p_order_id VARCHAR(10), 
    IN p_new_status INT,
    IN p_user_id VARCHAR(10)
)
BEGIN
    DECLARE v_old_status INT;
    DECLARE v_old_end_time TIMESTAMP;
    
    -- 获取变更前数据
    SELECT status, end_time INTO v_old_status, v_old_end_time
    FROM ServiceOrder 
    WHERE order_id = p_order_id;
    
    -- 执行更新
    UPDATE ServiceOrder 
    SET status = p_new_status,
        end_time = CASE WHEN p_new_status = 4 THEN NOW() ELSE end_time END
    WHERE order_id = p_order_id;
    
    -- 记录审计日志
    INSERT INTO AuditLog (
        log_id, table_name, record_id, operation,
        old_data, new_data, changed_by, changed_at
    ) VALUES (
        UUID(), 'ServiceOrder', p_order_id, 'UPDATE',
        JSON_OBJECT('status', v_old_status, 'end_time', v_old_end_time),
        JSON_OBJECT('status', p_new_status, 'end_time', 
                   CASE WHEN p_new_status = 4 THEN NOW() ELSE v_old_end_time END),
        p_user_id, NOW()
    );
END$$
DELIMITER ;
```

## 七、系统特色功能说明

### 7.1 智能工单分配算法

我们的系统实现了自动工单分配功能，当客户提交维修申请时，系统会：

1. **自动触发分配**：通过 `AutoAssignmentService.trigger_assignment()`
2. **检查可用维修人员**：查询 `availability_status = AVAILABLE` 的工人
3. **随机分配策略**：当前使用随机选择，可扩展为按技能匹配
4. **状态自动更新**：同时更新工单状态和维修人员可用性

### 7.2 实时数据一致性保证

通过服务层模式确保数据操作的原子性：

```python
@audit("Order", "UPDATE")
def complete_order(db: Session, order_id: str, worker_id: str, audit_context=None) -> Order:
    """Mark an order as completed"""
    # 1. 验证订单和维修人员
    order_obj = order.get_by_order_id(db, order_id=order_id)
    if not order_obj:
        raise ValueError("Order not found")
    if order_obj.worker_id != worker_id:
        raise ValueError("Order is not assigned to this worker")
    
    # 2. 检查所有维修程序是否完成
    procedures = procedure.get_procedures_by_order(db, order_id=order_id)      
    for procedure_obj in procedures:
        if procedure_obj.current_status != ProcedureStatus.COMPLETED:
            raise ValueError(f"Procedure {procedure_obj.procedure_id} is not in completed state")
    
    # 3. 计算总费用
    total_cost = log.get_total_cost_by_order(db, order_id=order_id)
    
    # 4. 完成订单（此操作会触发其他相关更新）
    return order.complete_order(db, order_id=order_id, total_cost=total_cost)
    
    # 5. 审计日志自动通过装饰器记录
```
