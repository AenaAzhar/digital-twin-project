"""
Batch Grouping Optimization
Groups orders into efficient batches for surface treatment
"""
from typing import List, Dict
from ..simulation.order import Order


class BatchGroupingOptimizer:
    """Optimize order batching for surface treatment"""
    
    def __init__(self):
        self.batch_counter = 0
    
    def group_by_product_type(self, orders: List[Order], max_batch_size: int = None) -> Dict[str, List[Order]]:
        """Group orders by product type"""
        grouped = {}
        for order in orders:
            if order.product_type not in grouped:
                grouped[order.product_type] = []
            grouped[order.product_type].append(order)
        
        # Apply max batch size limit if specified
        if max_batch_size:
            grouped = self._split_large_batches(grouped, max_batch_size)
        
        return grouped
    
    def group_by_similar_operations(self, orders: List[Order]) -> Dict[tuple, List[Order]]:
        """Group orders with similar operation sequences"""
        grouped = {}
        for order in orders:
            operations_key = tuple(sorted(order.required_operations))
            if operations_key not in grouped:
                grouped[operations_key] = []
            grouped[operations_key].append(order)
        return grouped
    
    def optimize_batch_composition(self, orders: List[Order], 
                                 max_batch_size: int = 50,
                                 batch_timeout: int = 8) -> List[Dict]:
        """
        Optimize batch composition considering:
        - Product similarity (reduce setup times)
        - Batch sizes (efficiency)
        - Order urgency (lead time)
        
        Args:
            orders: List of orders to batch
            max_batch_size: Maximum parts per batch
            batch_timeout: Hours to wait before forcing batch release
        
        Returns:
            List of optimized batches
        """
        if not orders:
            return []
        
        # Sort by due date (shortest job first - SJF with due date priority)
        sorted_orders = sorted(orders, key=lambda o: o.promised_due_date)
        
        # Group by product type first
        product_groups = self.group_by_product_type(sorted_orders)
        
        batches = []
        for product_type, product_orders in product_groups.items():
            # Create batches within each product type
            for i in range(0, len(product_orders), max_batch_size):
                batch_orders = product_orders[i:i + max_batch_size]
                batch_id = f"BATCH_{self.batch_counter:04d}"
                self.batch_counter += 1
                
                batches.append({
                    "batch_id": batch_id,
                    "product_type": product_type,
                    "order_ids": [o.order_id for o in batch_orders],
                    "total_quantity": sum(o.batch_size for o in batch_orders),
                    "orders": batch_orders,
                    "urgency_score": self._calculate_batch_urgency(batch_orders)
                })
        
        # Sort batches by urgency
        batches.sort(key=lambda b: b["urgency_score"], reverse=True)
        
        return batches
    
    def _split_large_batches(self, grouped: Dict[str, List[Order]], 
                            max_batch_size: int) -> Dict[str, List[Order]]:
        """Split large groups into smaller batches"""
        result = {}
        for key, orders in grouped.items():
            if len(orders) > max_batch_size:
                # Keep as list of smaller batches
                for i in range(0, len(orders), max_batch_size):
                    batch_key = f"{key}_batch_{i//max_batch_size}"
                    result[batch_key] = orders[i:i + max_batch_size]
            else:
                result[key] = orders
        return result
    
    def _calculate_batch_urgency(self, orders: List[Order]) -> float:
        """Calculate urgency score for batch (0-1, higher = more urgent)"""
        if not orders:
            return 0.0
        
        # Calculate average slack time
        current_time = orders[0].arrival_time  # Approximate
        slack_times = [max(0, o.promised_due_date - current_time) for o in orders]
        
        if not slack_times:
            return 0.0
        
        avg_slack = sum(slack_times) / len(slack_times)
        # Normalize to 0-1 scale (assuming 168 hours = 1 week)
        urgency = max(0, min(1, 1 - (avg_slack / 168)))
        return urgency


class SchedulingOptimizer:
    """Optimize order scheduling for finite capacity"""
    
    def earliest_due_date(self, orders: List[Order]) -> List[Order]:
        """Schedule orders by earliest due date (EDD rule)"""
        return sorted(orders, key=lambda o: o.promised_due_date)
    
    def shortest_processing_time(self, orders: List[Order]) -> List[Order]:
        """Schedule orders by shortest processing time (SPT rule)"""
        # For this, we estimate based on number of operations
        return sorted(orders, key=lambda o: len(o.required_operations))
    
    def weighted_shortest_job_first(self, orders: List[Order], 
                                   weight_factor: float = 0.5) -> List[Order]:
        """
        Schedule using weighted shortest job first
        w = due_date_urgency * weight_factor + spt_priority * (1 - weight_factor)
        """
        def priority_score(order):
            due_date_urgency = 1 / (order.promised_due_date - order.arrival_time + 1)
            spt_priority = 1 / (len(order.required_operations) + 1)
            return (due_date_urgency * weight_factor + spt_priority * (1 - weight_factor))
        
        return sorted(orders, key=priority_score, reverse=True)
    
    def estimate_completion_time(self, order: Order, 
                                 avg_operation_time: float = 2.0) -> float:
        """Estimate order completion time"""
        # Simple estimate: sum of operation times
        estimated_time = len(order.required_operations) * avg_operation_time
        return order.arrival_time + estimated_time
