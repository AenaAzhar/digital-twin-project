"""
Workshop Simulation Model - Core DES using SimPy
Finite capacity simulation for surface treatment workshops
"""
import simpy
import random
from typing import List, Dict, Tuple
from datetime import datetime
from .order import Order
from .resources import Machine, Operator, WorkshopResources, BatchComposition


class SurfaceTreatmentWorkshop:
    """Discrete Event Simulation model for surface treatment workshop"""
    
    def __init__(self, env: simpy.Environment, workshop_id: str):
        self.env = env
        self.workshop_id = workshop_id
        self.resources = WorkshopResources()
        self.machine_resources: Dict[str, simpy.Resource] = {}
        
        # Tracking
        self.orders: Dict[str, Order] = {}
        self.batches: Dict[str, BatchComposition] = {}
        self.completed_orders: List[Order] = []
        self.events_log: List[Dict] = []
        
        # Metrics
        self.total_orders_processed = 0
        self.total_late_orders = 0
        self.average_lead_time = 0.0
        
    def add_machine(self, station_name: str, machine_id: str, capacity: int,
                   process_time_mean: float, process_time_std: float = None,
                   compatible_products: List[str] = None):
        """Add machine to workshop"""
        machine = Machine(
            station_name=station_name,
            machine_id=machine_id,
            capacity=capacity,
            process_time_distribution="normal",
            process_time_mean=process_time_mean,
            process_time_std=process_time_std or process_time_mean * 0.1,
            compatible_products=compatible_products or []
        )
        self.resources.add_machine(machine)
        
        # Create SimPy resource for this station if not exists
        if station_name not in self.machine_resources:
            self.machine_resources[station_name] = simpy.Resource(self.env, capacity=1)
    
    def add_operator(self, operator_id: str, skills: List[str]):
        """Add operator to workshop"""
        operator = Operator(operator_id=operator_id, skills=skills)
        self.resources.add_operator(operator)
    
    def submit_order(self, order: Order):
        """Submit order to workshop queue"""
        self.orders[order.order_id] = order
        self.env.process(self._process_order(order))
        self._log_event("ORDER_SUBMITTED", order.order_id, order.arrival_time)
    
    def _process_order(self, order: Order):
        """Process order through workshop stages (generator)"""
        order.start_time = self.env.now
        
        # Wait for order to arrive at workshop
        if self.env.now < order.arrival_time:
            yield self.env.timeout(order.arrival_time - self.env.now)
        
        self._log_event("ORDER_ARRIVED", order.order_id, self.env.now)
        
        # Process through each required operation
        for operation in order.required_operations:
            # Find available machine
            machine = self.resources.get_machine_by_station(operation)
            if machine is None:
                continue
            
            # Wait for machine availability
            resource = self.machine_resources.get(operation)
            if resource:
                with resource.request() as req:
                    yield req
                    
                    # Process at machine
                    process_time = self._generate_process_time(machine)
                    self._log_event("OPERATION_START", order.order_id, 
                                  self.env.now, {"operation": operation})
                    
                    yield self.env.timeout(process_time)
                    order.record_operation_time(operation, process_time)
                    machine.utilization_time += process_time
                    
                    self._log_event("OPERATION_COMPLETE", order.order_id, 
                                  self.env.now, {"operation": operation})
        
        # Order completion
        order.completion_time = self.env.now
        self.completed_orders.append(order)
        self.total_orders_processed += 1
        
        if order.is_late():
            self.total_late_orders += 1
        
        self._log_event("ORDER_COMPLETED", order.order_id, self.env.now,
                       {"lateness": order.get_lateness()})
    
    def _generate_process_time(self, machine: Machine) -> float:
        """Generate processing time based on machine distribution"""
        if machine.process_time_distribution == "normal":
            return abs(random.gauss(machine.process_time_mean, machine.process_time_std))
        elif machine.process_time_distribution == "exponential":
            return random.expovariate(1.0 / machine.process_time_mean)
        else:
            return machine.process_time_mean
    
    def _log_event(self, event_type: str, order_id: str, timestamp: float, details: Dict = None):
        """Log simulation event"""
        self.events_log.append({
            "timestamp": timestamp,
            "event_type": event_type,
            "order_id": order_id,
            "details": details or {}
        })
    
    def get_performance_metrics(self) -> Dict:
        """Calculate workshop performance metrics"""
        if not self.completed_orders:
            return {}
        
        lead_times = [o.get_lead_time() for o in self.completed_orders]
        lateness_values = [o.get_lateness() for o in self.completed_orders]
        
        avg_lead_time = sum(lead_times) / len(lead_times)
        avg_lateness = sum(lateness_values) / len(lateness_values)
        on_time_rate = (1 - self.total_late_orders / self.total_orders_processed) * 100
        
        return {
            "total_orders": self.total_orders_processed,
            "completed_orders": len(self.completed_orders),
            "late_orders": self.total_late_orders,
            "average_lead_time": avg_lead_time,
            "average_lateness": avg_lateness,
            "on_time_delivery_rate": on_time_rate,
            "min_lead_time": min(lead_times),
            "max_lead_time": max(lead_times),
        }
    
    def get_resource_utilization(self) -> Dict[str, float]:
        """Calculate resource utilization rates"""
        utilization = {}
        for machine_id, machine in self.resources.machines.items():
            total_time = self.env.now
            if total_time > 0:
                utilization[machine_id] = (machine.utilization_time / total_time) * 100
        return utilization
    
    def print_summary(self):
        """Print simulation summary"""
        metrics = self.get_performance_metrics()
        print(f"\n{'='*60}")
        print(f"Workshop '{self.workshop_id}' Simulation Summary")
        print(f"{'='*60}")
        print(f"Total Orders Processed: {metrics.get('total_orders', 0)}")
        print(f"On-Time Delivery Rate: {metrics.get('on_time_delivery_rate', 0):.2f}%")
        print(f"Average Lead Time: {metrics.get('average_lead_time', 0):.2f} hours")
        print(f"Average Lateness: {metrics.get('average_lateness', 0):.2f} hours")
        print(f"{'='*60}\n")
