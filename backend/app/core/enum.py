from enum import IntEnum


class ProcedureStatus(IntEnum):
    PENDING = 0
    IN_PROGRESS = 1
    COMPLETED = 2


class OrderStatus(IntEnum):
    PENDING_ASSIGNMENT = 0
    ASSIGNED = 1
    IN_PROGRESS = 2
    COMPLETED = 3


class WorkerAvailabilityStatus(IntEnum):
    AVAILABLE = 0
    BUSY = 1