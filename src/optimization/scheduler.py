"""
Scheduling Algorithms
Finite capacity scheduling for production planning
"""
from typing import List, Dict, Tuple
from ..simulation.order import Order


class FiniteCapacityScheduler:
    """Finite capacity scheduler for surface treatment workshops"""
    
    def __init__(self):
        self.schedule: List[Tuple[str, float, float]] = []  # (order_id, start_time, end_time)
    
    def create_schedule(self, orders: List[Order], 
                       available_capacity: int = 8,  # hours per day
                       machine_hours_per_order: float = 2.0) -> Dict:
        """
        Create production schedule with finite capacity
        
        Args:
            orders: Orders to schedule
            available_capacity: Hours available per day
            machine_hours_per_order: Average hours per order
        
        Returns:
            Schedule information
        """
        sorted_orders = sorted(orders, key=lambda o: o.promised_due_date)
        
        current_time = 0.0
        daily_schedule = {}
        schedule_info = []
        
        for order in sorted_orders:
            # Calculate required machine hours
            required_hours = machine_hours_per_order * len(order.required_operations)
            
            # Check if need to move to next day
            if current_time % 24 != 0:  # Not start of day
                remaining_today = 24 - (current_time % 24)
                if required_hours > remaining_today:
                    # Move to next day
                    current_time = ((current_time // 24) + 1) * 24
            
            # Schedule order
            start_time = current_time
            end_time = current_time + required_hours
            
            schedule_info.append({
                "order_id": order.order_id,
                "start_time": start_time,
                "end_time": end_time,
                "duration": required_hours,
                "due_date": order.promised_due_date,
                "slack_time": order.promised_due_date - end_time
            })
            
            current_time = end_time
        
        return {
            "schedule": schedule_info,
            "total_makespan": current_time,
            "schedule_horizon_days": current_time / 24,
            "orders_scheduled": len(sorted_orders)
        }
    
    def check_feasibility(self, schedule_info: Dict) -> Tuple[bool, List[str]]:
        """Check schedule feasibility"""
        issues = []
        
        for item in schedule_info.get("schedule", []):
            if item["slack_time"] < 0:
                issues.append(f"Order {item['order_id']} violates due date by {abs(item['slack_time']):.2f} hours")
        
        return len(issues) == 0, issues
    
    def calculate_schedule_metrics(self, schedule_info: Dict, 
                                  orders: List[Order]) -> Dict:
        """Calculate schedule quality metrics"""
        metrics = {}
        
        # On-time rate
        late_orders = len([s for s in schedule_info.get("schedule", []) if s["slack_time"] < 0])
        on_time_rate = (1 - late_orders / len(orders)) * 100 if orders else 0
        
        metrics["on_time_delivery_rate"] = on_time_rate
        metrics["late_orders"] = late_orders
        metrics["total_makespan"] = schedule_info.get("total_makespan", 0)
        metrics["schedule_efficiency"] = self._calculate_efficiency(schedule_info)
        
        return metrics
    
    def _calculate_efficiency(self, schedule_info: Dict) -> float:
        """Calculate schedule efficiency (0-100%)"""
        if not schedule_info.get("schedule"):
            return 0.0
        
        total_duration = sum(s["duration"] for s in schedule_info["schedule"])
        makespan = schedule_info.get("total_makespan", 1)
        
        efficiency = (total_duration / makespan) * 100
        return min(efficiency, 100)  # Cap at 100%


class CapacityPlanning:
    """Capacity planning utilities"""
    
    def estimate_required_capacity(self, orders: List[Order], 
                                  avg_operation_hours: float = 2.0) -> float:
        """Estimate required production capacity"""
        total_hours = sum(len(o.required_operations) * avg_operation_hours for o in orders)
        return total_hours
    
    def calculate_capacity_utilization(self, required_capacity: float,
                                      available_capacity: float,
                                      planning_horizon_days: int = 7) -> float:
        """Calculate capacity utilization rate"""
        total_available = available_capacity * planning_horizon_days
        utilization = (required_capacity / total_available) * 100 if total_available > 0 else 0
        return min(utilization, 100)
    
    def identify_capacity_bottlenecks(self, orders: List[Order],
                                     available_capacity: int = 8) -> Dict:
        """Identify potential capacity bottlenecks"""
        total_required = len(orders) * 2.0  # Rough estimate
        hours_available = available_capacity * 7  # Per week
        
        bottlenecks = {}
        if total_required > hours_available:
            bottlenecks["production_capacity"] = {
                "required": total_required,
                "available": hours_available,
                "shortfall": total_required - hours_available,
                "severity": "high" if total_required > hours_available * 1.5 else "medium"
            }
        
        return bottlenecks
