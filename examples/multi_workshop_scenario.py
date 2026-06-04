"""
Multi-Workshop Coordination Example
Advanced scenario with multiple workshops and coordination
"""
import sys
import os
import simpy
import random

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.simulation.workshop import SurfaceTreatmentWorkshop
from src.simulation.order import Order
from src.optimization.batch_grouping import BatchGroupingOptimizer
from src.optimization.scheduler import FiniteCapacityScheduler


class ProductionNetwork:
    """Coordinates multiple workshops"""
    
    def __init__(self):
        self.workshops: dict = {}
        self.orders: list = []
        self.batch_optimizer = BatchGroupingOptimizer()
        self.scheduler = FiniteCapacityScheduler()
    
    def add_workshop(self, workshop: SurfaceTreatmentWorkshop):
        """Add workshop to network"""
        self.workshops[workshop.workshop_id] = workshop
    
    def allocate_batch_to_workshop(self, batch_id: str, workshop_id: str, orders: list):
        """Allocate batch to specific workshop"""
        workshop = self.workshops.get(workshop_id)
        if workshop:
            for order in orders:
                order.set_batch(batch_id)
                workshop.submit_order(order)


def run_multi_workshop_example():
    """Run multi-workshop coordination example"""
    print("\n" + "="*60)
    print("DIGITAL TWIN - MULTI-WORKSHOP COORDINATION")
    print("Advanced Planning Scenario")
    print("="*60 + "\n")
    
    env = simpy.Environment()
    network = ProductionNetwork()
    
    # Setup two workshops
    print("Setting up workshops...\n")
    
    # Workshop 1: Cleaning & Preparation
    workshop1 = SurfaceTreatmentWorkshop(env, "WORKSHOP_PREP")
    workshop1.add_machine("CLEANING", "CLEAN_01", 1, 1.5, 0.3)
    workshop1.add_machine("SURFACE_PREP", "PREP_01", 1, 2.0, 0.4)
    workshop1.add_operator("OP_W1_001", ["CLEANING", "SURFACE_PREP"])
    network.add_workshop(workshop1)
    print("✓ Workshop 1 (Preparation) configured")
    
    # Workshop 2: Coating & Finishing
    workshop2 = SurfaceTreatmentWorkshop(env, "WORKSHOP_COATING")
    workshop2.add_machine("COATING", "COAT_01", 1, 3.0, 0.5)
    workshop2.add_machine("DRYING", "DRY_01", 2, 2.0, 0.4)
    workshop2.add_machine("INSPECTION", "INSP_01", 1, 1.0, 0.2)
    workshop2.add_operator("OP_W2_001", ["COATING", "DRYING", "INSPECTION"])
    network.add_workshop(workshop2)
    print("✓ Workshop 2 (Coating & Finishing) configured\n")
    
    # Generate orders for different product types
    print("Generating orders...\n")
    orders = []
    product_types = ["COATING_A", "COATING_B", "COATING_C"]
    
    for i in range(15):
        order = Order(
            order_id=f"MULTI_ORD_{i+1:03d}",
            customer_id=f"CUST_{random.randint(1, 5):02d}",
            arrival_time=i * 3.0,
            promised_due_date=i * 3.0 + random.uniform(24, 72),
            product_type=random.choice(product_types),
            batch_size=random.randint(8, 15)
        )
        orders.append(order)
    
    print(f"Generated {len(orders)} orders\n")
    
    # Batch optimization across network
    print("-" * 60)
    print("BATCH OPTIMIZATION (Network-wide)")
    print("-" * 60 + "\n")
    
    batches = network.batch_optimizer.optimize_batch_composition(orders, max_batch_size=25)
    print(f"Optimized into {len(batches)} batches\n")
    
    # Allocate batches to workshops
    print("-" * 60)
    print("BATCH ALLOCATION")
    print("-" * 60 + "\n")
    
    for idx, batch in enumerate(batches):
        # Simple allocation: alternate workshops
        workshop_id = "WORKSHOP_PREP" if idx % 2 == 0 else "WORKSHOP_COATING"
        print(f"Batch {batch['batch_id']} → {workshop_id}")
        print(f"  Orders: {len(batch['order_ids'])}, Total Qty: {batch['total_quantity']}")
    
    # Allocate and run
    print(f"\nRunning simulation across {len(network.workshops)} workshops...\n")
    
    for batch in batches:
        workshop_id = "WORKSHOP_PREP" if batches.index(batch) % 2 == 0 else "WORKSHOP_COATING"
        network.allocate_batch_to_workshop(batch['batch_id'], workshop_id, batch['orders'])
    
    env.run()
    
    # Print results for each workshop
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60 + "\n")
    
    for ws_id, workshop in network.workshops.items():
        print(f"\n{ws_id}:")
        workshop.print_summary()
        
        metrics = workshop.get_performance_metrics()
        if metrics:
            print(f"  On-Time Rate: {metrics.get('on_time_delivery_rate', 0):.1f}%")


if __name__ == "__main__":
    run_multi_workshop_example()
