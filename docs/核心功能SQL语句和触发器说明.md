# 车辆维修管理系统 - 核心功能SQL语句说明和触发器说明

## 一、系统架构概述

本车辆维修管理系统采用了**自研 ORM 框架（DBRM - Database Remote）**进行数据库操作，而非直接 SQL 语句编写。该 ORM 框架基于 [Lab1](https://github.com/wtalioy/DatabaseRemote) 实现，参考 SQLAlchemy ，提供了基础的对象关系映射功能，并通过 Python 装饰器和服务层模式实现了传统数据库触发器的功能。

### 技术架构特点：
- **自定义 ORM 框架**：`app.dbrm` 包提供完整的 Table、Column、Query 等功能
- **装饰器触发器**：通过 `@audit` 装饰器实现数据变更追踪和自动化操作
- **服务层自动化**：通过 Service 层实现复杂业务逻辑的自动触发
- **定时调度器**：实现定期数据处理和维护任务

## 二、ORM vs SQL

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
).filter(
    Condition.eq(Car.car_type, car_type)
)
```

**等价SQL语句：**
```sql
-- 简单查询（ORM: db.query(ServiceOrderModel).filter_by(customer_id=customer_id).all()）
SELECT * FROM ServiceOrder WHERE customer_id = '客户ID';

-- 复杂连接查询（ORM: db.query(ServiceOrderModel).join(Car, on=(Car.car_id, ServiceOrderModel.car_id)).filter(...)）
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
        # 立即触发分配尝试
        from app.background.assignment_processor import trigger_assignment
        trigger_assignment(db, order_obj.order_id)
        return order_obj
```

### 3.3 维修进度跟踪和费用计算

**ORM实现：**
```python
# CRUD层
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

# Service层
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

## 四、"触发器"功能的Python实现

### 4.1 审计装饰器 - 数据变更追踪

我们通过`@audit`装饰器实现了数据库触发器的功能，自动记录所有数据变更到AuditLog表：

```python
# 审计装饰器使用示例
@audit("Order", "CREATE")
def create_order(db: Session, obj_in: OrderCreate, customer_id: str, audit_context=None) -> Order:
    """Create a new service order"""
    order_obj = order.create_order_for_customer(db=db, obj_in=obj_in, customer_id=customer_id)
    # 立即触发分配尝试
    from app.background.assignment_processor import trigger_assignment
    trigger_assignment(db, order_obj.order_id)
    return order_obj

@audit("Order", "UPDATE")
def update_order_status(db: Session, order_id: str, new_status: int, audit_context=None) -> Order:
    """Update the status of an order"""
    valid_statuses = [OrderStatus.PENDING_ASSIGNMENT, OrderStatus.IN_PROGRESS, OrderStatus.COMPLETED]
    if new_status not in valid_statuses:
        raise ValueError(f"Invalid status: {new_status}")
    return order.update_order_status(db, order_id=order_id, new_status=new_status)

# 审计日志的实际创建
def create_audit_entry(
    db: Session,
    table_name: str,
    record_id: str,
    operation: str,
    old_values: Optional[Dict[str, Any]] = None,
    new_values: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None
) -> AuditLog:
    """创建审计日志记录"""
    # 生成唯一审计ID（10位随机字符串）
    audit_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    
    # 计算变更字段
    changed_fields = None
    if old_values and new_values:
        changed_fields = [
            field for field, value in new_values.items()
            if field in old_values and old_values[field] != value
        ]
    
    audit_entry = AuditLogModel(
        audit_id=audit_id,
        table_name=table_name,
        record_id=record_id,
        operation=operation.upper(),
        old_values=json.dumps(old_values) if old_values else None,
        new_values=json.dumps(new_values) if new_values else None,
        changed_fields=changed_fields,
        user_id=user_id
    )
    
    db.add(audit_entry)
    db.commit()
    return AuditLog.model_validate(audit_entry)
```

**触发器等价功能：**
- **数据变更前记录**：保存修改前的数据状态
- **数据变更后记录**：记录新的数据状态
- **操作审计日志**：自动记录操作者、时间、变更内容

### 4.2 智能工单分配系统

我们的系统采用了**后台自动分配处理器**架构，实现了智能的工单分配和管理：

```python
class AssignmentProcessor:
    """统一的后台工单分配处理器，支持自动分配和失效处理"""
    
    def __init__(self, interval_seconds: int = 30):
        self.interval_seconds = interval_seconds
        self.running = False
        self.thread = None
        self._stop_event = threading.Event()
    
    def _run_processor(self):
        """主处理循环 - 定期处理待分配工单和失效分配"""
        while self.running and not self._stop_event.is_set():
            try:
                for db in get_db():
                    # 处理待分配工单
                    result = self.process_pending_assignments(db)
                    
                    # 只记录重要的分配活动（5+工单）
                    if result >= 5:
                        logger.info(f"Assignment processor assigned {result} pending orders")
                    
                    # 处理失效分配（已分配但超时未接受）
                    self._handle_stale_assignments(db)
                    break
                
            except Exception as e:
                logger.error(f"Assignment processor error: {e}")
            
            # 等待下一个处理周期
            self._stop_event.wait(self.interval_seconds)
    
    def process_pending_assignments(self, db: Session) -> int:
        """
        处理所有待分配工单，优先处理加急工单
        返回成功分配的工单数量
        """
        pending_orders = order.get_orders_by_status(db, status=OrderStatus.PENDING_ASSIGNMENT)
        
        if not pending_orders:
            return 0
        
        # 按加急标志排序（加急工单优先）
        sorted_orders = sorted(pending_orders, key=lambda o: o.expedite_flag, reverse=True)
        
        assigned_count = 0
        
        for order_obj in sorted_orders:
            if self.trigger_assignment(db, order_obj.order_id):
                assigned_count += 1
            else:
                # 没有更多可用维修人员，停止处理
                break
        
        return assigned_count
    
    def _handle_stale_assignments(self, db: Session):
        """处理失效分配 - 已分配但超过10分钟未接受的工单"""
        stale_cutoff = datetime.now() - timedelta(minutes=10)
        
        try:
            stale_orders = order.get_stale_assigned_orders(db, cutoff_time=stale_cutoff)
            
            if stale_orders:
                logger.info(f"Processing {len(stale_orders)} stale assignments")
                
            for stale_order in stale_orders:
                # 重置为待分配状态
                order.update_order_assignment(
                    db, order_id=stale_order.order_id, 
                    worker_id=None, status=OrderStatus.PENDING_ASSIGNMENT
                )
                # 释放维修人员
                if stale_order.worker_id:
                    worker.update_availability(
                        db, worker_id=stale_order.worker_id, 
                        status=WorkerAvailabilityStatus.AVAILABLE
                    )
                
        except Exception as e:
            logger.error(f"Error handling stale assignments: {e}")
    
    def trigger_assignment(self, db: Session, order_id: str) -> bool:
        """即时工单分配 - 随机选择可用维修人员"""
        order_obj = order.get_by_order_id(db, order_id)
        if not order_obj or order_obj.status != OrderStatus.PENDING_ASSIGNMENT:
            return False
        
        # 查找所有可用维修人员
        available_workers = worker.get_available_workers(db)
        
        if not available_workers:
            # 无可用维修人员 - 工单保持待分配状态
            return False
        
        # 随机选择维修人员
        selected_worker = random.choice(available_workers)
        
        # 更新工单：分配维修人员，设置状态为已分配
        order.update_order_assignment(
            db, order_id=order_id, 
            worker_id=selected_worker.user_id, 
            status=OrderStatus.ASSIGNED
        )
        
        # 更新维修人员可用状态
        worker.update_availability(
            db, worker_id=selected_worker.user_id, 
            status=WorkerAvailabilityStatus.BUSY
        )
        
        return True

# 全局实例管理
def start_background_processor(interval_seconds: int = 30):
    """启动全局后台分配处理器"""
    processor = get_assignment_processor()
    processor.interval_seconds = interval_seconds
    processor.start()

def trigger_assignment(db: Session, order_id: str) -> bool:
    """触发单个工单分配"""
    return get_assignment_processor().trigger_assignment(db, order_id)
```

### 5.3 定时工资结算调度器

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

### 6.2 维修人员绩效分析

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

## 六、系统特色功能说明

### 6.1 智能工单分配系统

我们的系统实现了**后台自动分配处理器**架构，提供了完整的工单分配和管理功能：

#### 核心特性：

1. **即时分配触发**：通过 `trigger_assignment()` 在工单创建时立即尝试分配
2. **后台定期处理**：每30秒自动处理所有待分配工单
3. **加急工单优先**：按 `expedite_flag` 排序，优先处理加急工单
4. **失效分配处理**：自动处理超过10分钟未接受的分配
5. **智能状态管理**：自动更新工单和维修人员状态

#### 分配流程：

1. **工单创建** → 立即触发分配尝试
2. **无可用人员** → 工单保持 `PENDING_ASSIGNMENT` 状态
3. **后台处理器** → 定期扫描待分配工单
4. **优先级排序** → 加急工单优先分配
5. **随机选择** → 从可用维修人员中随机选择
6. **状态更新** → 工单状态变为 `ASSIGNED`，维修人员变为 `BUSY`
7. **失效检测** → 超时未接受的分配自动重置

#### 技术优势：

- **高可用性**：即使即时分配失败，后台处理器确保最终分配
- **负载均衡**：随机分配策略避免工作负载集中
- **自动恢复**：失效分配自动重置，确保工单不会丢失
- **优先级支持**：加急工单得到优先处理
- **监控友好**：提供详细的分配统计和状态信息

### 6.2 实时数据一致性保证

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
