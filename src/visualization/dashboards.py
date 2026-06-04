"""
Visualization and Analysis Dashboards
Performance metrics and timeline visualization
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from typing import List, Dict
from ..simulation.order import Order


class PerformanceDashboard:
    """Generate performance metrics and visualizations"""
    
    @staticmethod
    def plot_order_timeline(orders: List[Order], title: str = "Order Processing Timeline"):
        """Plot Gantt-like timeline of order processing"""
        fig, ax = plt.subplots(figsize=(14, 6))
        
        # Sort orders by completion time
        sorted_orders = sorted([o for o in orders if o.completion_time], 
                             key=lambda o: o.completion_time)
        
        for idx, order in enumerate(sorted_orders):
            # Color based on lateness
            color = 'red' if order.is_late() else 'green'
            
            # Plot order processing bar
            duration = order.get_lead_time()
            ax.barh(idx, duration, left=order.arrival_time, height=0.6, 
                   color=color, alpha=0.7, label=order.order_id if idx < 5 else "")
            
            # Mark due date
            ax.plot([order.promised_due_date, order.promised_due_date], 
                   [idx-0.3, idx+0.3], 'b--', linewidth=2)
        
        ax.set_xlabel('Time (hours)')
        ax.set_ylabel('Order')
        ax.set_title(title)
        ax.legend(loc='upper right', fontsize=8)
        plt.tight_layout()
        return fig
    
    @staticmethod
    def plot_performance_metrics(metrics: Dict):
        """Plot performance metrics"""
        if not metrics:
            print("No metrics to plot")
            return None
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        
        # On-time delivery rate
        axes[0, 0].bar(['On-Time', 'Late'], 
                      [metrics.get('on_time_delivery_rate', 0), 
                       100 - metrics.get('on_time_delivery_rate', 0)])
        axes[0, 0].set_title('Delivery Performance')
        axes[0, 0].set_ylabel('Percentage (%)')
        axes[0, 0].set_ylim(0, 100)
        
        # Lead time distribution
        axes[0, 1].text(0.5, 0.5, 
                       f"Avg Lead Time:\n{metrics.get('average_lead_time', 0):.2f} hrs\n" +
                       f"Range: {metrics.get('min_lead_time', 0):.2f} - {metrics.get('max_lead_time', 0):.2f} hrs",
                       ha='center', va='center', fontsize=11, transform=axes[0, 1].transAxes)
        axes[0, 1].set_title('Lead Time Statistics')
        axes[0, 1].axis('off')
        
        # Lateness analysis
        axes[1, 0].text(0.5, 0.5,
                       f"Average Lateness:\n{metrics.get('average_lateness', 0):.2f} hrs\n" +
                       f"Late Orders: {metrics.get('late_orders', 0)}",
                       ha='center', va='center', fontsize=11, transform=axes[1, 0].transAxes)
        axes[1, 0].set_title('Lateness Analysis')
        axes[1, 0].axis('off')
        
        # Summary
        axes[1, 1].text(0.5, 0.5,
                       f"Total Orders: {metrics.get('total_orders', 0)}\n" +
                       f"Completed: {metrics.get('completed_orders', 0)}",
                       ha='center', va='center', fontsize=11, transform=axes[1, 1].transAxes)
        axes[1, 1].set_title('Summary')
        axes[1, 1].axis('off')
        
        plt.tight_layout()
        return fig
    
    @staticmethod
    def plot_resource_utilization(utilization: Dict):
        """Plot resource utilization"""
        if not utilization:
            return None
        
        fig, ax = plt.subplots(figsize=(10, 5))
        
        resources = list(utilization.keys())
        util_rates = list(utilization.values())
        
        colors = ['green' if u > 70 else 'orange' if u > 50 else 'red' for u in util_rates]
        ax.bar(resources, util_rates, color=colors, alpha=0.7)
        ax.set_ylabel('Utilization Rate (%)')
        ax.set_title('Resource Utilization')
        ax.set_ylim(0, 100)
        ax.axhline(y=70, color='g', linestyle='--', alpha=0.3, label='Target (70%)')
        ax.legend()
        
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        return fig
    
    @staticmethod
    def plot_schedule(schedule_info: Dict):
        """Plot production schedule"""
        if not schedule_info.get('schedule'):
            return None
        
        fig, ax = plt.subplots(figsize=(14, 6))
        
        schedule = schedule_info['schedule']
        colors = ['green' if s['slack_time'] >= 0 else 'red' for s in schedule]
        
        for idx, item in enumerate(schedule):
            ax.barh(idx, item['duration'], left=item['start_time'], 
                   color=colors[idx], alpha=0.7)
            
            # Mark due date
            ax.plot([item['due_date'], item['due_date']], 
                   [idx-0.3, idx+0.3], 'b--', linewidth=1.5)
        
        ax.set_xlabel('Time (hours)')
        ax.set_ylabel('Order')
        ax.set_title('Production Schedule (Green=On-Time, Red=Late)')
        
        # Legend
        green_patch = mpatches.Patch(color='green', alpha=0.7, label='On-Time')
        red_patch = mpatches.Patch(color='red', alpha=0.7, label='Late')
        ax.legend(handles=[green_patch, red_patch])
        
        plt.tight_layout()
        return fig


class AnalyticsGenerator:
    """Generate analytical reports"""
    
    @staticmethod
    def generate_order_report(orders: List[Order]) -> str:
        """Generate detailed order analysis report"""
        completed = [o for o in orders if o.completion_time]
        
        if not completed:
            return "No completed orders to report"
        
        late_orders = [o for o in completed if o.is_late()]
        
        report = f"""
╔════════════════════════════════════════════════════╗
║           ORDER PROCESSING REPORT                  ║
╚════════════════════════════════════════════════════╝

Total Orders:           {len(orders)}
Completed Orders:       {len(completed)}
Late Orders:            {len(late_orders)}
On-Time Delivery Rate:  {(1 - len(late_orders)/len(completed))*100:.1f}%

Lead Time Statistics:
  - Average:            {sum(o.get_lead_time() for o in completed)/len(completed):.2f} hours
  - Min:                {min(o.get_lead_time() for o in completed):.2f} hours
  - Max:                {max(o.get_lead_time() for o in completed):.2f} hours

Lateness Statistics:
  - Average Lateness:   {sum(o.get_lateness() for o in completed)/len(completed):.2f} hours
  - Max Lateness:       {max(o.get_lateness() for o in completed):.2f} hours

Late Orders:
"""
        for order in late_orders[:5]:  # Show first 5
            report += f"  - {order.order_id}: {order.get_lateness():.2f} hours late\n"
        
        if len(late_orders) > 5:
            report += f"  ... and {len(late_orders)-5} more\n"
        
        return report
    
    @staticmethod
    def generate_batch_report(batches: List[Dict]) -> str:
        """Generate batch composition report"""
        report = f"""
╔════════════════════════════════════════════════════╗
║         BATCH COMPOSITION REPORT                   ║
╚════════════════════════════════════════════════════╝

Total Batches:          {len(batches)}

Batch Details:
"""
        for batch in batches:
            report += f"\n  {batch['batch_id']}:\n"
            report += f"    - Product Type:    {batch['product_type']}\n"
            report += f"    - Orders:          {len(batch['order_ids'])}\n"
            report += f"    - Total Quantity:  {batch['total_quantity']}\n"
            report += f"    - Urgency Score:   {batch.get('urgency_score', 0):.2f}\n"
        
        return report
