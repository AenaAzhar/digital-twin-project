"""
Resources - Resource definitions for surface treatment workshops
"""
from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class Machine:
    """Machine/Station resource"""
    station_name: str
    machine_id: str
    capacity: int  # Number of parts it can process in parallel
    process_time_distribution: str  # e.g., "exponential", "normal"
    process_time_mean: float
    process_time_std: float = None
    compatible_products: List[str] = field(default_factory=list)
    
    # Runtime tracking
    is_available: bool = True
    current_batch_id: str = None
    utilization_time: float = 0.0


@dataclass
class Operator:
    """Operator resource"""
    operator_id: str
    skills: List[str] = field(default_factory=list)  # e.g., ["CLEANING", "COATING"]
    is_available: bool = True
    current_task: str = None
    total_work_time: float = 0.0


@dataclass
class WorkshopResources:
    """Collection of resources in a workshop"""
    machines: Dict[str, Machine] = field(default_factory=dict)
    operators: Dict[str, Operator] = field(default_factory=dict)
    
    def add_machine(self, machine: Machine):
        """Add machine to workshop"""
        self.machines[machine.machine_id] = machine
    
    def add_operator(self, operator: Operator):
        """Add operator to workshop"""
        self.operators[operator.operator_id] = operator
    
    def get_machine_by_station(self, station_name: str) -> Machine:
        """Get machine by station name"""
        for machine in self.machines.values():
            if machine.station_name == station_name:
                return machine
        return None
    
    def get_available_machine(self, station_name: str) -> Machine:
        """Get first available machine at station"""
        machine = self.get_machine_by_station(station_name)
        if machine and machine.is_available:
            return machine
        return None
    
    def get_operators_with_skill(self, skill: str) -> List[Operator]:
        """Get available operators with specific skill"""
        return [op for op in self.operators.values() 
                if skill in op.skills and op.is_available]


@dataclass
class BatchComposition:
    """Batch composition for batching orders"""
    batch_id: str
    product_type: str
    order_ids: List[str] = field(default_factory=list)
    total_quantity: int = 0
    creation_time: float = None
    
    def add_order(self, order_id: str, quantity: int):
        """Add order to batch"""
        self.order_ids.append(order_id)
        self.total_quantity += quantity
    
    def get_batch_size(self) -> int:
        """Get total batch size"""
        return self.total_quantity
