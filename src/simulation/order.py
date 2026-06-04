"""
Order Entity - Represents production orders in surface treatment
"""
from dataclasses import dataclass, field
from typing import List
from datetime import datetime, timedelta


@dataclass
class Order:
    """Production order for surface treatment"""
    order_id: str
    customer_id: str
    arrival_time: float  # Simulation time
    promised_due_date: float  # Simulation time
    product_type: str  # e.g., "COATING_A", "COATING_B"
    batch_size: int
    required_operations: List[str] = field(default_factory=list)
    
    # Runtime tracking
    start_time: float = None
    completion_time: float = None
    processing_times: dict = field(default_factory=dict)
    current_station: str = None
    batch_id: str = None
    
    def __post_init__(self):
        if not self.required_operations:
            self.required_operations = self._get_operations_for_type()
    
    def _get_operations_for_type(self) -> List[str]:
        """Get operation sequence based on product type"""
        operations_map = {
            "COATING_A": ["CLEANING", "COATING", "DRYING", "INSPECTION"],
            "COATING_B": ["SURFACE_PREP", "COATING", "CURING", "INSPECTION"],
            "COATING_C": ["CLEANING", "PRIMING", "COATING", "DRYING", "INSPECTION"],
        }
        return operations_map.get(self.product_type, ["CLEANING", "COATING", "INSPECTION"])
    
    def set_batch(self, batch_id: str):
        """Assign order to batch"""
        self.batch_id = batch_id
    
    def record_operation_time(self, station: str, duration: float):
        """Record processing time at a station"""
        self.processing_times[station] = duration
        self.current_station = station
    
    def get_total_processing_time(self) -> float:
        """Calculate total processing time"""
        return sum(self.processing_times.values())
    
    def get_lead_time(self) -> float:
        """Get actual lead time from arrival to completion"""
        if self.completion_time is not None:
            return self.completion_time - self.arrival_time
        return None
    
    def get_lateness(self) -> float:
        """Calculate lateness (negative if early)"""
        if self.completion_time is not None:
            return max(0, self.completion_time - self.promised_due_date)
        return None
    
    def is_late(self) -> bool:
        """Check if order was completed late"""
        lateness = self.get_lateness()
        return lateness > 0 if lateness is not None else False
