"""
Simple Surface Treatment Example
Basic simulation scenario for digital twin
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
from src.visualization.dashboards import PerformanceDashboard, AnalyticsGenerator


def setup_workshop(env: simpy.Environment) -> SurfaceTreatmentWorkshop:
    """Setup workshop with machines and operators"""
    workshop = SurfaceTreatmentWorkshop(env, workshop_id="WORKSHOP_ALBI_01")
    
    # Add machines (station_name, machine_id, capacity, mean_time, std_dev)
    workshop.add_machine("CLEANING", "MACH_CLEAN_01", 1, 1.5, 0.3)
    workshop.add_machine("COATING", "MACH_COAT_01", 1, 3.0, 0.5)
    workshop.add_machine("DRYING", "MACH_DRY_01", 2, 2.0, 0.4)
    workshop.add_machine("INSPECTION", "MACH_INSP_01", 1, 1.0, 0.2)
    
    # Add operators
    workshop.add_operator("OP_001", ["CLEANING", "COATING"])
    workshop.add_operator("OP_002", ["DRYING", "INSPECTION"])
    workshop.add_operator("OP_003", ["CLEANING", "COATING", "DRYING"])
    
    return workshop


def generate_orders(num_orders: int = 20) -> list:
    """Generate sample orders"""
    orders = []
    product_types = ["COATING_A", "COATING_B", "COATING_C"]
    
    for i in range(num_orders):
        arrival_time = i * 2.0  # One order every 2 hours
        
        order = Order(
            order_id=f"ORD_{i+1:04d}",
            customer_id=f"CUST_{random.randint(1, 10):02d}",
            arrival_time=arrival_time,
            promised_due_date=arrival_time + random.uniform(12, 48),  # 12-48 hours lead time
            product_type=random.choice(product_types),
            batch_size=random.randint(5, 20)
        )
        orders.append(order)
    
    return orders


def run_simulation():
    """Run simple surface treatment simulation"""
    print("\n" + "="*60)
    print("DIGITAL TWIN - SURFACE TREATMENT WORKSHOP")
    print("Simple DES Example with Optimization")
    print("="*60 + "\n")
    
    # Setup simulation environment
    env = simpy.Environment()
    workshop = setup_workshop(env)
    
    # Generate orders
    orders = generate_orders(num_orders=20)
    
    print(f"Generated {len(orders)} orders\n")
    
    # Demonstrate Batch Optimization
    print("-" * 60)
    print("BATCH GROUPING OPTIMIZATION")
    print("-" * 60)
    
    batch_optimizer = BatchGroupingOptimizer()
    batches = batch_optimizer.optimize_batch_composition(orders, max_batch_size=30)
    
    print(f"Optimized into {len(batches)} batches\n")
    
    report = AnalyticsGenerator.generate_batch_report(batches)
    print(report)
    
    # Demonstrate Scheduling
    print("\n" + "-" * 60)
    print("FINITE CAPACITY SCHEDULING")
    print("-" * 60)
    
    scheduler = FiniteCapacityScheduler()
    schedule_info = scheduler.create_schedule(
        orders,
        available_capacity=8,  # 8 hours per day
        machine_hours_per_order=3.0
    )
    
    schedule_metrics = scheduler.calculate_schedule_metrics(schedule_info, orders)
    feasible, issues = scheduler.check_feasibility(schedule_info)
    
    print(f"\nSchedule Feasibility: {'✓ Feasible' if feasible else '✗ Not Feasible'}")
    if issues:
        for issue in issues[:3]:
            print(f"  - {issue}")
    
    print(f"\nSchedule Metrics:")
    print(f"  - Makespan: {schedule_info.get('total_makespan', 0):.1f} hours " +
          f"({schedule_info.get('schedule_horizon_days', 0):.1f} days)")
    print(f"  - On-Time Rate: {schedule_metrics.get('on_time_delivery_rate', 0):.1f}%")
    print(f"  - Efficiency: {schedule_metrics.get('schedule_efficiency', 0):.1f}%")
    
    # Run Discrete Event Simulation
    print("\n" + "-" * 60)
    print("DISCRETE EVENT SIMULATION")
    print("-" * 60)
    
    print(f"\nRunning simulation...")
    
    # Submit orders to simulation
    for order in orders:
        workshop.submit_order(order)
    
    # Run simulation
    env.run()
    
    print(f"Simulation completed at time {env.now:.1f} hours\n")
    
    # Print results
    workshop.print_summary()
    
    metrics = workshop.get_performance_metrics()
    print(f"\nDetailed Metrics:")
    for key, value in metrics.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")
    
    # Generate analytics report
    print("\n" + "-" * 60)
    print("ORDER PROCESSING ANALYTICS")
    print("-" * 60)
    
    report = AnalyticsGenerator.generate_order_report(orders)
    print(report)
    
    # Visualizations (optional, comment out if matplotlib not available)
    print("\n" + "-" * 60)
    print("GENERATING VISUALIZATIONS")
    print("-" * 60)
    
    try:
        # Plot timeline
        fig1 = PerformanceDashboard.plot_order_timeline(orders)
        fig1.savefig('order_timeline.png', dpi=100, bbox_inches='tight')
        print("✓ Saved: order_timeline.png")
        
        # Plot metrics
        fig2 = PerformanceDashboard.plot_performance_metrics(metrics)
        fig2.savefig('performance_metrics.png', dpi=100, bbox_inches='tight')
        print("✓ Saved: performance_metrics.png")
        
        # Plot schedule
        fig3 = PerformanceDashboard.plot_schedule(schedule_info)
        fig3.savefig('production_schedule.png', dpi=100, bbox_inches='tight')
        print("✓ Saved: production_schedule.png")
        
        print("\nVisualizations saved in project root directory")
        
    except Exception as e:
        print(f"Note: Could not generate visualizations - {e}")
    
    print("\n" + "="*60)
    print("SIMULATION COMPLETE")
    print("="*60 + "\n")
    
    return workshop, orders, batches, schedule_info


if __name__ == "__main__":
    workshop, orders, batches, schedule = run_simulation()
