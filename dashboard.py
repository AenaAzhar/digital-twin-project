"""
Interactive Dashboard for Digital Twin Project
Streamlit-based web interface for visualizing simulation results
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from PIL import Image
import sys
import os
import simpy
import random

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.simulation.workshop import SurfaceTreatmentWorkshop
from src.simulation.order import Order
from src.optimization.batch_grouping import BatchGroupingOptimizer
from src.optimization.scheduler import FiniteCapacityScheduler
from src.visualization.dashboards import PerformanceDashboard, AnalyticsGenerator

# Page config
st.set_page_config(
    page_title="Digital Twin Dashboard",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional Enterprise Dashboard CSS
st.markdown("""
    <style>
    * {
        font-family: 'Segoe UI', 'Roboto', '-apple-system', sans-serif;
    }
    
    /* Color Variables */
    :root {
        --primary: #0f172a;
        --primary-light: #1e293b;
        --accent: #3b82f6;
        --accent-light: #60a5fa;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
        --border: #e2e8f0;
        --text: #1e293b;
        --text-light: #64748b;
        --bg-light: #f8fafc;
    }
    
    /* Main Header */
    .main-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 50%, #0ea5e9 100%);
        color: white;
        padding: 50px 40px;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 40px;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.25),
                    inset 0 1px 0 rgba(255, 255, 255, 0.1);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -10%;
        width: 400px;
        height: 400px;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        border-radius: 50%;
        pointer-events: none;
    }
    
    .main-header h1 {
        font-size: 3.2rem;
        margin: 0;
        font-weight: 900;
        letter-spacing: -1px;
        position: relative;
        z-index: 1;
        text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
    }
    
    .main-header p {
        font-size: 1.15rem;
        margin: 12px 0 0 0;
        opacity: 0.98;
        position: relative;
        z-index: 1;
        font-weight: 500;
        letter-spacing: 0.5px;
    }
    
    /* Metric Cards - Professional Style */
    .metric-card {
        background: white;
        padding: 28px;
        border-radius: 16px;
        margin: 12px 0;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05),
                    0 10px 30px rgba(0, 0, 0, 0.06);
        transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 6px;
        height: 100%;
        background: linear-gradient(180deg, #3b82f6 0%, #0ea5e9 100%);
        border-radius: 16px 0 0 16px;
        transform: scaleY(1);
        transform-origin: center;
        transition: all 0.35s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.12),
                    0 8px 16px rgba(0, 0, 0, 0.08);
        border-color: #3b82f6;
    }
    
    .metric-card:hover::before {
        height: 4px;
        top: auto;
        left: 0;
        right: 0;
        bottom: 0;
        width: 100%;
    }
    
    .metric-label {
        font-size: 0.85rem;
        color: #64748b;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .metric-value {
        font-size: 2.8rem;
        font-weight: 900;
        color: #0f172a;
        margin: 8px 0;
        line-height: 1;
        letter-spacing: -1px;
    }
    
    .metric-unit {
        font-size: 0.8rem;
        color: #94a3b8;
        margin-top: 8px;
        font-weight: 600;
    }
    
    /* Section Titles */
    .section-title {
        font-size: 2rem;
        font-weight: 900;
        color: #0f172a;
        margin: 35px 0 25px 0;
        padding-bottom: 18px;
        border-bottom: 3px solid #3b82f6;
        letter-spacing: -0.5px;
        position: relative;
    }
    
    .section-title::after {
        content: '';
        position: absolute;
        bottom: -3px;
        left: 0;
        width: 60px;
        height: 3px;
        background: linear-gradient(90deg, #3b82f6, #60a5fa);
    }
    
    /* Status Boxes */
    .status-success {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        color: #15803d;
        padding: 18px 24px;
        border-radius: 12px;
        font-weight: 700;
        border: 2px solid #86efac;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.1);
    }
    
    .status-warning {
        background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
        color: #92400e;
        padding: 18px 24px;
        border-radius: 12px;
        font-weight: 700;
        border: 2px solid #fcd34d;
        box-shadow: 0 4px 15px rgba(245, 158, 11, 0.1);
    }
    
    /* Info Box */
    .info-box {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        border: 2px solid #0ea5e9;
        border-left: 6px solid #0ea5e9;
        padding: 24px;
        border-radius: 12px;
        color: #0c4a6e;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(14, 165, 233, 0.1);
    }
    
    .info-box b {
        color: #0369a1;
        font-weight: 800;
    }
    
    .success-box {
        background: linear-gradient(135deg, #f0fdf4 0%, #f0f9ff 100%);
        border: 2px solid #10b981;
        border-left: 6px solid #10b981;
        padding: 24px;
        border-radius: 12px;
        color: #065f46;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.1);
    }
    
    .success-box b {
        color: #15803d;
        font-weight: 800;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
        background-color: transparent;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 0;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 12px 12px 0 0;
        padding: 16px 24px;
        font-weight: 700;
        color: #64748b;
        transition: all 0.3s ease;
        border-bottom: 3px solid transparent;
        text-transform: uppercase;
        font-size: 0.95rem;
        letter-spacing: 0.5px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: transparent;
        color: #3b82f6;
        border-bottom: 3px solid #3b82f6;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 50%, #3b82f6 100%);
        color: white;
        font-weight: 800;
        padding: 14px 32px;
        border-radius: 12px;
        border: none;
        box-shadow: 0 8px 20px rgba(15, 23, 42, 0.3);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        font-size: 1.05rem;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    
    .stButton > button:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 30px rgba(15, 23, 42, 0.4);
    }
    
    .stButton > button:active {
        transform: translateY(-1px);
        box-shadow: 0 6px 15px rgba(15, 23, 42, 0.3);
    }
    
    /* Data Frame */
    .stDataFrame {
        background-color: white;
        border-radius: 14px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        border: 1px solid #e2e8f0;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: #f8fafc;
        border-right: 2px solid #e2e8f0;
    }
    
    /* Sidebar Title */
    [data-testid="stSidebarNav"] > div:first-child {
        border-bottom: 3px solid #3b82f6;
        padding-bottom: 15px;
        margin-bottom: 20px;
    }
    
    /* Footer */
    .footer-text {
        text-align: center;
        color: #94a3b8;
        font-size: 0.9rem;
        margin-top: 50px;
        padding: 40px 0;
        border-top: 2px solid #e2e8f0;
    }
    
    .footer-text h3 {
        color: #0f172a;
        font-size: 1.3rem;
        margin-bottom: 12px;
        font-weight: 800;
    }
    
    .footer-text p {
        margin: 6px 0;
        line-height: 1.6;
    }
    
    /* Animations */
    @keyframes slideInDown {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    .main-header {
        animation: slideInDown 0.6s ease-out;
    }
    
    .section-title {
        animation: fadeIn 0.5s ease-out;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #f1f5f9 !important;
        border: 1px solid #e2e8f0;
        border-radius: 10px !important;
        font-weight: 700;
        color: #0f172a;
    }
    
    .streamlit-expanderHeader:hover {
        background-color: #e2e8f0 !important;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f5f9;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #cbd5e1;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #94a3b8;
    }
    </style>
""", unsafe_allow_html=True)

# Title with professional gradient background
st.markdown("""
<div class="main-header">
    <h1>🏭 Digital Twin Dashboard</h1>
    <p>Enterprise-Grade Production Planning & Optimization System</p>
</div>
""", unsafe_allow_html=True)

st.markdown("")  # Spacing

# Sidebar - Simulation Parameters
st.sidebar.markdown("""
<div style="background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%); color: white; padding: 20px; border-radius: 12px; margin-bottom: 20px;">
    <h2 style="margin: 0; font-size: 1.3rem; font-weight: 900;">⚙️ Configuration</h2>
    <p style="margin: 5px 0 0 0; opacity: 0.9; font-size: 0.9rem;">Setup your simulation parameters</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("")

num_orders = st.sidebar.slider(
    "📦 Number of Orders",
    min_value=5,
    max_value=50,
    value=20,
    step=5,
    help="Total orders to process in simulation"
)

machine_mean_time = st.sidebar.slider(
    "⏱️ Machine Mean Processing Time",
    min_value=1.0,
    max_value=5.0,
    value=2.0,
    step=0.5,
    help="Average processing time per machine (hours)"
)

capacity_hours = st.sidebar.slider(
    "🏭 Available Daily Capacity",
    min_value=4,
    max_value=16,
    value=8,
    step=1,
    help="Total working hours per day"
)

st.sidebar.markdown("")
st.sidebar.markdown("")

run_simulation = st.sidebar.button(
    "🚀 RUN SIMULATION",
    use_container_width=True,
    help="Execute simulation with current parameters"
)

st.sidebar.markdown("---")

st.sidebar.markdown("""
<div style="background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); padding: 15px; border-radius: 10px; border-left: 4px solid #0ea5e9; color: #0c4a6e;">
    <b style="font-size: 0.9rem;">💡 Pro Tip:</b>
    <p style="margin: 8px 0 0 0; font-size: 0.85rem;">Adjust parameters and run multiple simulations to find optimal configurations for your production planning.</p>
</div>
""", unsafe_allow_html=True)

# Main content
if run_simulation:
    with st.spinner("⏳ Running simulation..."):
        # Setup simulation
        env = simpy.Environment()
        workshop = SurfaceTreatmentWorkshop(env, workshop_id="WORKSHOP_ALBI_01")
        
        # Add machines
        workshop.add_machine("CLEANING", "MACH_CLEAN_01", 1, machine_mean_time, machine_mean_time * 0.2)
        workshop.add_machine("COATING", "MACH_COAT_01", 1, machine_mean_time * 1.5, machine_mean_time * 0.3)
        workshop.add_machine("DRYING", "MACH_DRY_01", 2, machine_mean_time * 1.2, machine_mean_time * 0.2)
        workshop.add_machine("INSPECTION", "MACH_INSP_01", 1, machine_mean_time * 0.5, machine_mean_time * 0.1)
        
        # Add operators
        workshop.add_operator("OP_001", ["CLEANING", "COATING"])
        workshop.add_operator("OP_002", ["DRYING", "INSPECTION"])
        workshop.add_operator("OP_003", ["CLEANING", "COATING", "DRYING"])
        
        # Generate orders
        orders = []
        product_types = ["COATING_A", "COATING_B", "COATING_C"]
        for i in range(num_orders):
            arrival_time = i * 2.0
            order = Order(
                order_id=f"ORD_{i+1:04d}",
                customer_id=f"CUST_{random.randint(1, 10):02d}",
                arrival_time=arrival_time,
                promised_due_date=arrival_time + random.uniform(12, 48),
                product_type=random.choice(product_types),
                batch_size=random.randint(5, 20)
            )
            orders.append(order)
        
        # Batch optimization
        batch_optimizer = BatchGroupingOptimizer()
        batches = batch_optimizer.optimize_batch_composition(orders, max_batch_size=30)
        
        # Scheduling
        scheduler = FiniteCapacityScheduler()
        schedule_info = scheduler.create_schedule(orders, available_capacity=capacity_hours, machine_hours_per_order=3.0)
        
        # Run simulation
        for order in orders:
            workshop.submit_order(order)
        
        env.run()
        
        # Get metrics
        metrics = workshop.get_performance_metrics()
        
        st.success("✅ Simulation completed successfully!")
        
        # Display results in tabs
        tab1, tab2, tab3, tab4 = st.tabs(
            ["📊 Overview", "📈 Performance Metrics", "🎯 Batching", "⏱️ Scheduling"]
        )
        
        with tab1:
            st.markdown('<div class="section-title">📊 Simulation Summary</div>', unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">📦 Total Orders</div>
                    <div class="metric-value">{metrics.get('total_orders', 0)}</div>
                    <div class="metric-unit">processed</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                on_time_rate = metrics.get('on_time_delivery_rate', 0)
                color = "#10b981" if on_time_rate >= 90 else "#f59e0b" if on_time_rate >= 70 else "#ef4444"
                st.markdown(f"""
                <div class="metric-card" style="border-left-color: {color}">
                    <div class="metric-label">✅ On-Time Rate</div>
                    <div class="metric-value" style="color: {color}">{on_time_rate:.1f}%</div>
                    <div class="metric-unit">delivery</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">⏱️ Avg Lead Time</div>
                    <div class="metric-value">{metrics.get('average_lead_time', 0):.1f}h</div>
                    <div class="metric-unit">hours</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                late_count = metrics.get('late_orders', 0)
                late_color = "#10b981" if late_count == 0 else "#ef4444"
                st.markdown(f"""
                <div class="metric-card" style="border-left-color: {late_color}">
                    <div class="metric-label">⚠️ Late Orders</div>
                    <div class="metric-value" style="color: {late_color}">{late_count}</div>
                    <div class="metric-unit">orders</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Create performance chart
            completion_data = {
                'Status': ['On-Time', 'Late'],
                'Orders': [
                    metrics.get('total_orders', 0) - metrics.get('late_orders', 0),
                    metrics.get('late_orders', 0)
                ]
            }
            
            fig_status = px.pie(
                completion_data,
                values='Orders',
                names='Status',
                color_discrete_map={'On-Time': '#10b981', 'Late': '#ef4444'},
                title="Order Completion Status",
                hole=0.4
            )
            fig_status.update_traces(
                textposition='inside',
                textinfo='percent+label',
                marker=dict(line=dict(color='white', width=3))
            )
            fig_status.update_layout(
                showlegend=True,
                height=400,
                font=dict(size=12, color='#1e3a8a'),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_status, use_container_width=True)
        
        with tab2:
            st.markdown('<div class="section-title">📈 Performance Analytics</div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Lead time distribution
                lead_times = [o.get_lead_time() for o in orders if o.completion_time]
                
                fig_lead = go.Figure()
                fig_lead.add_trace(go.Histogram(
                    x=lead_times,
                    nbinsx=10,
                    name='Lead Time',
                    marker=dict(color='#0ea5e9', line=dict(color='#1e3a8a', width=1.5))
                ))
                fig_lead.update_layout(
                    title="Lead Time Distribution",
                    xaxis_title="Hours",
                    yaxis_title="Count",
                    height=400,
                    plot_bgcolor='rgba(240,245,250,1)',
                    paper_bgcolor='white',
                    font=dict(color='#1e3a8a', size=11),
                    hovermode='x unified'
                )
                st.plotly_chart(fig_lead, use_container_width=True)
            
            with col2:
                # Order timeline
                lateness_data = [o.get_lateness() if o.get_lateness() else 0 for o in orders]
                
                fig_lateness = go.Figure()
                colors = ['#10b981' if l == 0 else '#ef4444' for l in lateness_data]
                fig_lateness.add_trace(go.Bar(
                    x=[f"ORD_{i+1:04d}" for i in range(len(orders))],
                    y=lateness_data,
                    marker=dict(color=colors, line=dict(color='white', width=1)),
                    name='Lateness'
                ))
                fig_lateness.update_layout(
                    title="Order Lateness Analysis",
                    xaxis_title="Order",
                    yaxis_title="Lateness (hours)",
                    height=400,
                    showlegend=False,
                    xaxis={'tickangle': 45},
                    plot_bgcolor='rgba(240,245,250,1)',
                    paper_bgcolor='white',
                    font=dict(color='#1e3a8a', size=11),
                    hovermode='x unified'
                )
                st.plotly_chart(fig_lateness, use_container_width=True)
            
            # Key statistics
            st.markdown("---")
            st.markdown('<div class="section-title">📊 Key Statistics</div>', unsafe_allow_html=True)
            
            stat_col1, stat_col2, stat_col3 = st.columns(3)
            
            with stat_col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">⏱️ Lead Time</div>
                    <div style="margin: 15px 0;">
                        <div style="font-size: 0.9rem; color: #475569;">Min: <span style="font-weight: 700; color: #10b981;">{metrics.get('min_lead_time', 0):.2f}h</span></div>
                        <div style="font-size: 0.9rem; color: #475569; margin: 8px 0;">Max: <span style="font-weight: 700; color: #ef4444;">{metrics.get('max_lead_time', 0):.2f}h</span></div>
                        <div style="font-size: 0.9rem; color: #475569;">Avg: <span style="font-weight: 700; color: #0ea5e9;">{metrics.get('average_lead_time', 0):.2f}h</span></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with stat_col2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">⚠️ Lateness</div>
                    <div style="margin: 15px 0;">
                        <div style="font-size: 0.9rem; color: #475569;">Avg: <span style="font-weight: 700; color: #f59e0b;">{metrics.get('average_lateness', 0):.2f}h</span></div>
                        <div style="font-size: 0.9rem; color: #475569; margin-top: 8px;">Late Orders: <span style="font-weight: 700; color: #ef4444;">{metrics.get('late_orders', 0)}</span></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with stat_col3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">✅ Efficiency</div>
                    <div style="margin: 15px 0;">
                        <div style="font-size: 0.9rem; color: #475569;">Completion: <span style="font-weight: 700; color: #10b981;">100%</span></div>
                        <div style="font-size: 0.9rem; color: #475569; margin-top: 8px;">On-Time: <span style="font-weight: 700; color: #0ea5e9;">{metrics.get('on_time_delivery_rate', 0):.1f}%</span></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        with tab3:
            st.markdown('<div class="section-title">🎯 Batch Grouping Optimization</div>', unsafe_allow_html=True)
            
            # Batch summary
            batch_data = []
            for batch in batches:
                batch_data.append({
                    'Batch ID': batch['batch_id'],
                    'Product Type': batch['product_type'],
                    'Orders': len(batch['order_ids']),
                    'Total Qty': batch['total_quantity'],
                    'Urgency': f"{batch['urgency_score']:.2f}"
                })
            
            batch_df = pd.DataFrame(batch_data)
            st.markdown("**Batch Details**")
            st.dataframe(batch_df, use_container_width=True, hide_index=True)
            
            # Batch visualization
            fig_batch = px.bar(
                batch_df,
                x='Batch ID',
                y='Total Qty',
                color='Product Type',
                title="Batch Composition by Product Type",
                labels={'Total Qty': 'Total Quantity', 'Batch ID': 'Batch'},
                color_discrete_sequence=['#0ea5e9', '#10b981', '#f59e0b']
            )
            fig_batch.update_layout(
                height=400,
                plot_bgcolor='rgba(240,245,250,1)',
                paper_bgcolor='white',
                font=dict(color='#1e3a8a', size=11),
                hovermode='x unified'
            )
            fig_batch.update_traces(marker=dict(line=dict(color='white', width=2)))
            st.plotly_chart(fig_batch, use_container_width=True)
        
        with tab4:
            st.markdown('<div class="section-title">⏱️ Finite Capacity Scheduling</div>', unsafe_allow_html=True)
            
            schedule = schedule_info.get('schedule', [])
            
            # Schedule metrics
            feasible, issues = scheduler.check_feasibility(schedule_info)
            schedule_metrics = scheduler.calculate_schedule_metrics(schedule_info, orders)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">📋 Makespan</div>
                    <div class="metric-value">{schedule_info.get('total_makespan', 0):.1f}h</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">📅 Days Required</div>
                    <div class="metric-value">{schedule_info.get('schedule_horizon_days', 0):.1f}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                efficiency = schedule_metrics.get('schedule_efficiency', 0)
                eff_color = "#10b981" if efficiency > 80 else "#f59e0b" if efficiency > 60 else "#ef4444"
                st.markdown(f"""
                <div class="metric-card" style="border-left-color: {eff_color}">
                    <div class="metric-label">⚡ Efficiency</div>
                    <div class="metric-value" style="color: {eff_color}">{efficiency:.1f}%</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Feasibility status
            if feasible:
                st.markdown('<div class="success-box">✅ <b>Schedule is Feasible</b> - All orders meet their due dates</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="status-warning">⚠️ <b>Schedule has {len(issues)} Feasibility Issues</b></div>', unsafe_allow_html=True)
                if issues:
                    with st.expander("View Issues", expanded=False):
                        for idx, issue in enumerate(issues[:10], 1):
                            st.write(f"**{idx}.** {issue}")
            
            st.markdown("---")
            
            # Schedule visualization
            schedule_df = pd.DataFrame(schedule)
            
            fig_schedule = px.bar(
                schedule_df,
                x='order_id',
                y='duration',
                color=['#10b981' if s >= 0 else '#ef4444' for s in schedule_df['slack_time']],
                title="Production Schedule",
                labels={'order_id': 'Order', 'duration': 'Duration (hours)'},
                custom_data=['slack_time']
            )
            fig_schedule.update_layout(
                height=400,
                plot_bgcolor='rgba(240,245,250,1)',
                paper_bgcolor='white',
                font=dict(color='#1e3a8a', size=11),
                hovermode='x unified',
                showlegend=False
            )
            fig_schedule.update_traces(marker=dict(line=dict(color='white', width=1.5)))
            st.plotly_chart(fig_schedule, use_container_width=True)

else:
    # Default view with professional layout
    st.markdown('<div class="info-box"><b>📋 Getting Started:</b> Configure your simulation parameters in the sidebar and click "Run Simulation" to view real-time analytics</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="section-title">📊 Dashboard Capabilities</div>', unsafe_allow_html=True)
        st.markdown("""
        ### Core Features
        - **🎯 Discrete Event Simulation** - Accurate DES model of surface treatment workshop
        - **📦 Smart Batching** - Intelligent order grouping optimization
        - **⏱️ Schedule Optimization** - Finite capacity scheduling algorithms
        - **📈 Real-time Analytics** - Live performance tracking and KPIs
        - **📊 Interactive Charts** - Professional Plotly visualizations
        - **✅ Feasibility Analysis** - Schedule constraint validation
        - **🎨 Professional UI** - Enterprise dashboard experience
        """)
    
    with col2:
        st.markdown('<div class="section-title">⚙️ Configurable Parameters</div>', unsafe_allow_html=True)
        st.markdown("""
        ### Customize Your Simulation
        - **📦 Order Volume** - 5 to 50 orders per simulation
        - **⏱️ Machine Speed** - 1-5 hour processing times
        - **🏭 Capacity** - 4-16 hours daily capacity
        - **🧮 Algorithms** - Multiple optimization strategies
        - **📊 Metrics** - Real-time KPI tracking
        
        ### What You Get
        - On-time delivery rates
        - Lead time analysis
        - Resource utilization
        - Schedule efficiency
        """)
    
    st.markdown("---")
    st.markdown('<div class="section-title">🖼️ Sample Visualizations</div>', unsafe_allow_html=True)
    
    # Professional visualization layout
    viz_col1, viz_col2, viz_col3 = st.columns(3)
    
    try:
        if os.path.exists("order_timeline.png"):
            with viz_col1:
                st.image("order_timeline.png", use_column_width=True)
                with st.expander("📋 Order Timeline"):
                    st.write("""
                    **Gantt Chart Visualization**
                    
                    Shows the processing timeline of each order through the workshop:
                    - Green bars: Orders completed on time
                    - Red bars: Late deliveries
                    - Blue dashed lines: Due dates
                    """)
    except:
        pass
    
    try:
        if os.path.exists("performance_metrics.png"):
            with viz_col2:
                st.image("performance_metrics.png", use_column_width=True)
                with st.expander("📊 Performance Dashboard"):
                    st.write("""
                    **4-Panel Analytics Dashboard**
                    
                    Comprehensive performance analysis:
                    - Delivery performance rate
                    - Lead time statistics
                    - Lateness distribution
                    - Order summary metrics
                    """)
    except:
        pass
    
    try:
        if os.path.exists("production_schedule.png"):
            with viz_col3:
                st.image("production_schedule.png", use_column_width=True)
                with st.expander("⏱️ Production Schedule"):
                    st.write("""
                    **Schedule Visualization**
                    
                    Optimal production sequencing:
                    - Resource allocation
                    - Due date constraints
                    - Schedule feasibility
                    - Makespan optimization
                    """)
    except:
        pass
    
    st.markdown("---")
    
    # Info cards at bottom
    info_col1, info_col2, info_col3 = st.columns(3)
    
    with info_col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); padding: 25px; border-radius: 12px; border: 2px solid #0ea5e9;">
            <h3 style="color: #0c4a6e; margin-top: 0;">🎯 Purpose</h3>
            <p style="color: #075985;">Digital Twin for short-term production planning in surface treatment industries with finite capacity constraints.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with info_col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); padding: 25px; border-radius: 12px; border: 2px solid #f59e0b;">
            <h3 style="color: #78350f; margin-top: 0;">🔬 Research</h3>
            <p style="color: #92400e;">PhD Thesis - IMT Mines Albi | INFINITY Project on advanced optimization techniques.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with info_col3:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #dcfce7 0%, #d1fae5 100%); padding: 25px; border-radius: 12px; border: 2px solid #10b981;">
            <h3 style="color: #065f46; margin-top: 0;">🚀 Technology</h3>
            <p style="color: #15803d;">SimPy-based DES with advanced optimization algorithms and real-time analytics.</p>
        </div>
        """, unsafe_allow_html=True)

# Footer - Professional
st.markdown("---")
st.markdown("""
<div class="footer-text">
    <h3>🏭 Digital Twin Production Planning System</h3>
    <p><b>PhD Research Project</b> | Optimization for Surface Treatment Industries</p>
    <p><b>Institution:</b> IMT Mines Albi | <b>Project:</b> INFINITY</p>
    <p style="margin-top: 15px; font-size: 0.85rem; color: #64748b;">
    Advanced discrete event simulation and finite capacity scheduling with real-time optimization
    </p>
</div>
""", unsafe_allow_html=True)
