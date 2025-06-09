from typing import List

from app.dbrm import Session, func


from app.models import Log as LogModel
from app.schemas import LogCreate, Log, PeriodCostBreakdown


class CRUDLog:
    def get_logs_by_order(
        self, db: Session, order_id: str, skip: int = 0, limit: int = 100
    ) -> List[Log]:
        objs = db.query(LogModel).filter_by(
            order_id=order_id
        ).order_by_desc(LogModel.log_time).offset(skip).limit(limit).all()
        if not objs:
            return []
        return [Log.model_validate(obj) for obj in objs]
    
    def get_logs_by_worker(
        self, db: Session, worker_id: str, skip: int = 0, limit: int = 100
    ) -> List[Log]:
        objs = db.query(LogModel).filter_by(
            worker_id=worker_id
        ).order_by_desc(LogModel.log_time).offset(skip).limit(limit).all()
        if not objs:
            return []
        return [Log.model_validate(obj) for obj in objs]
        
    def calculate_avg_cost_by_car_type(self, db: Session, car_type: int) -> float:
        from app.models import ServiceOrder, Car
        from app.dbrm import Condition
        
        cost_result = db.query(func.avg(LogModel.cost)).join(
            ServiceOrder, on=(ServiceOrder.order_id, LogModel.order_id)
        ).join(
            Car, on=(Car.car_id, ServiceOrder.car_id)
        ).where(
            Condition.eq(Car.car_type, car_type)
        ).scalar()
        
        return float(cost_result) if cost_result else 0
    
    def get_car_type_consumption(self, db: Session, car_type: int) -> List[tuple]:
        from app.models import ServiceOrder, Car
        from app.dbrm import Condition
        
        return db.query(LogModel.consumption).join(
            ServiceOrder, on=(ServiceOrder.order_id, LogModel.order_id)
        ).join(
            Car, on=(Car.car_id, ServiceOrder.car_id)
        ).where(
            Condition.eq(Car.car_type, car_type)
        ).all()

    def count_tasks_by_worker_type(self, db: Session, worker_type: int, start_time: str, end_time: str) -> int:
        from app.models import Worker
        from app.dbrm import Condition
        
        return db.query(func.count(LogModel.id)).join(
            Worker, on=(Worker.user_id, LogModel.worker_id)
        ).where(
            Condition.eq(Worker.worker_type, worker_type),
            Condition.gte(LogModel.log_time, start_time),
            Condition.lte(LogModel.log_time, end_time)
        ).scalar() or 0

    def calculate_total_hours_by_worker_type(self, db: Session, worker_type: int, start_time: str, end_time: str) -> float:
        from app.models import Worker
        from app.dbrm import Condition

        hours_result = db.query(func.sum(LogModel.duration)).join(
            Worker, on=(Worker.user_id, LogModel.worker_id)
        ).where(
            Condition.eq(Worker.worker_type, worker_type),
            Condition.gte(LogModel.log_time, start_time),
            Condition.lte(LogModel.log_time, end_time)
        ).scalar()

        return float(hours_result) if hours_result else 0

    def create_log_for_order(
        self, db: Session, *, obj_in: LogCreate, worker_id: str
    ) -> Log:
        from datetime import datetime
        now = datetime.now()
        
        db_obj = LogModel(
            consumption=obj_in.consumption,
            cost=obj_in.cost,
            duration=obj_in.duration,
            order_id=obj_in.order_id,
            worker_id=worker_id,
            log_time=now,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        return Log.model_validate(db_obj)
    
    def get_total_duration_by_worker(self, db: Session, worker_id: str) -> float:
        result = db.query(func.sum(LogModel.duration)).filter_by(
            worker_id=worker_id
        ).scalar()
        return float(result) if result else 0.0
    
    def get_total_cost_by_order(self, db: Session, order_id: str) -> float:
        result = db.query(func.sum(LogModel.cost)).filter_by(
            order_id=order_id
        ).scalar()
        return float(result) if result else 0.0
    
    def get_logs_by_order_and_worker(
        self, db: Session, order_id: str, worker_id: str
    ) -> List[Log]:
        """Get logs for a specific order and worker combination"""
        objs = db.query(LogModel).filter_by(
            order_id=order_id,
            worker_id=worker_id
        ).all()
        if not objs:
            return []
        return [Log.model_validate(obj) for obj in objs]


    def get_cost_breakdown_by_period(self, db: Session, start_date, end_date, period_type: str = "month") -> List[PeriodCostBreakdown]:
        """Get detailed cost breakdown by month or quarter using enhanced DBRM"""
        from app.models import Distribute
        from app.dbrm import Condition, func
        
        if period_type == "quarter":
            # Group by quarter using enhanced DBRM functions
            material_date_part = func.concat(
                func.extract('year', LogModel.log_time), 
                '-Q', 
                func.ceil(func.arithmetic(func.extract('month', LogModel.log_time), '/', 3))
            )
            labor_date_part = func.concat(
                func.extract('year', Distribute.distribute_time), 
                '-Q', 
                func.ceil(func.arithmetic(func.extract('month', Distribute.distribute_time), '/', 3))
            )
        else:
            # Group by month using enhanced DBRM functions
            material_date_part = func.date_format(LogModel.log_time, '%Y-%m')
            labor_date_part = func.date_format(Distribute.distribute_time, '%Y-%m')
        
        # Get material costs by period from logs using enhanced DBRM
        material_query = db.query(material_date_part, func.sum(LogModel.cost)).where(
            Condition.gte(LogModel.log_time, start_date),
            Condition.lte(LogModel.log_time, end_date)
        ).group_by(material_date_part)
        
        material_results = material_query.all()
        
        # Get labor costs by period from actual payments using enhanced DBRM
        labor_query = db.query(labor_date_part, func.sum(Distribute.amount)).where(
            Condition.gte(Distribute.distribute_time, start_date),
            Condition.lte(Distribute.distribute_time, end_date)
        ).group_by(labor_date_part)
        
        labor_results = labor_query.all()
        
        # Combine results
        breakdown = {}
        
        # Add material costs
        for period, material_cost in material_results:
            breakdown[period] = {
                'period': period,
                'material_cost': float(material_cost) if material_cost else 0.0,
                'labor_cost': 0.0
            }
        
        # Add labor costs
        for period, labor_cost in labor_results:
            if period not in breakdown:
                breakdown[period] = {
                    'period': period,
                    'material_cost': 0.0,
                    'labor_cost': 0.0
                }
            breakdown[period]['labor_cost'] = float(labor_cost) if labor_cost else 0.0
        
        # Convert to Pydantic models and calculate totals
        result = []
        for period_data in breakdown.values():
            material_cost = period_data['material_cost']
            labor_cost = period_data['labor_cost']
            total_cost = material_cost + labor_cost
            labor_material_ratio = labor_cost / material_cost if material_cost > 0 else 0.0
            
            period_breakdown = PeriodCostBreakdown(
                period=period_data['period'],
                material_cost=material_cost,
                labor_cost=labor_cost,
                total_cost=total_cost,
                labor_material_ratio=labor_material_ratio
            )
            result.append(period_breakdown)
        
        # Return sorted list by period
        return sorted(result, key=lambda x: x.period)


log = CRUDLog()
