import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
from datetime import datetime
import random

# Page configuration
st.set_page_config(
    page_title="Battery Cell Management System",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
    }
    
    .metric-container {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #3498db;
        margin: 0.5rem 0;
    }
    
    .alert-box {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .status-normal {
        background: #d4edda;
        color: #155724;
        padding: 0.25rem 0.5rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    
    .status-high {
        background: #d1ecf1;
        color: #0c5460;
        padding: 0.25rem 0.5rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    
    .status-low {
        background: #f8d7da;
        color: #721c24;
        padding: 0.25rem 0.5rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

class BatteryCellMonitor:
    def __init__(self):
        self.cell_types = {
            "LFP": {
                "nominal_voltage": 3.2,
                "minimum_voltage": 2.8,
                "maximum_voltage": 3.6,
                "name": "Lithium Iron Phosphate"
            },
            "NMC": {
                "nominal_voltage": 3.6,
                "minimum_voltage": 3.2,
                "maximum_voltage": 4.0,
                "name": "Nickel Manganese Cobalt"
            },
            "LCO": {
                "nominal_voltage": 3.7,
                "minimum_voltage": 3.0,
                "maximum_voltage": 4.2,
                "name": "Lithium Cobalt Oxide"
            },
            "LTO": {
                "nominal_voltage": 2.4,
                "minimum_voltage": 1.5,
                "maximum_voltage": 2.8,
                "name": "Lithium Titanate Oxide"
            }
        }
    
    def generate_random_voltage(self, cell_type):
        specs = self.cell_types[cell_type]
        range_voltage = specs["maximum_voltage"] - specs["minimum_voltage"]
        return round(specs["minimum_voltage"] + (random.random() * range_voltage), 2)
    
    def generate_random_current(self):
        return round(0.5 + (random.random() * 2), 2)  # 0.5 to 2.5 A
    
    def generate_random_temperature(self):
        return round(20 + (random.random() * 25), 1)  # 20 to 45°C
    
    def calculate_soc(self, voltage, cell_type):
        specs = self.cell_types[cell_type]
        range_voltage = specs["maximum_voltage"] - specs["minimum_voltage"]
        soc = ((voltage - specs["minimum_voltage"]) / range_voltage) * 100
        return max(0, min(100, round(soc, 1)))
    
    def get_cell_status(self, voltage, cell_type):
        specs = self.cell_types[cell_type]
        if voltage <= specs["minimum_voltage"] * 1.05:
            return "LOW"
        elif voltage >= specs["maximum_voltage"] * 0.95:
            return "HIGH"
        else:
            return "NORMAL"
    
    def process_cells_data(self, cells_config):
        cells_data = []
        
        for i, config in enumerate(cells_config, 1):
            cell_type = config['type']
            voltage = config['voltage']
            current = config['current']
            
            # Calculate derived values
            power = round(voltage * current, 2)
            temperature = self.generate_random_temperature()
            soc = self.calculate_soc(voltage, cell_type)
            status = self.get_cell_status(voltage, cell_type)
            
            cells_data.append({
                'Cell_ID': f'Cell_{i}',
                'Type': cell_type,
                'Voltage_V': voltage,
                'Current_A': current,
                'Power_W': power,
                'Temperature_C': temperature,
                'SOC_%': soc,
                'Status': status,
                'Specs': self.cell_types[cell_type]
            })
        
        return cells_data

# Initialize the monitor
if 'monitor' not in st.session_state:
    st.session_state.monitor = BatteryCellMonitor()

if 'monitoring_active' not in st.session_state:
    st.session_state.monitoring_active = False

if 'cells_config' not in st.session_state:
    st.session_state.cells_config = [
        {'type': 'LFP', 'voltage': 3.2, 'current': 1.0} for _ in range(8)
    ]

# Header
st.markdown("""
<div class="main-header">
    <h1>⚡ Battery Cell Management System</h1>
    <p>Advanced monitoring and configuration for battery cell arrays</p>
</div>
""", unsafe_allow_html=True)

# Sidebar Configuration
st.sidebar.header("🔧 System Configuration")

# Bench Information
bench_name = st.sidebar.text_input("Bench Name", value="Lab Bench A")
group_number = st.sidebar.number_input("Group Number", min_value=1, value=1)

st.sidebar.subheader("🔋 Cell Configuration")

# Cell configuration inputs
for i in range(8):
    st.sidebar.write(f"**Cell {i+1}**")
    col1, col2, col3 = st.sidebar.columns(3)
    
    with col1:
        cell_type = st.selectbox(
            "Type",
            ["LFP", "NMC", "LCO", "LTO"],
            key=f"type_{i}",
            index=["LFP", "NMC", "LCO", "LTO"].index(st.session_state.cells_config[i]['type'])
        )
    
    with col2:
        voltage = st.number_input(
            "Voltage (V)",
            min_value=0.0,
            max_value=5.0,
            value=st.session_state.cells_config[i]['voltage'],
            step=0.1,
            key=f"voltage_{i}"
        )
    
    with col3:
        current = st.number_input(
            "Current (A)",
            min_value=0.0,
            max_value=10.0,
            value=st.session_state.cells_config[i]['current'],
            step=0.1,
            key=f"current_{i}"
        )
    
    st.session_state.cells_config[i] = {
        'type': cell_type,
        'voltage': voltage,
        'current': current
    }

# Control buttons
st.sidebar.markdown("---")
col1, col2 = st.sidebar.columns(2)

with col1:
    if st.button("🔄 Update Config", use_container_width=True):
        st.rerun()

with col2:
    if st.button("🎲 Randomize", use_container_width=True):
        for i in range(8):
            cell_type = st.session_state.cells_config[i]['type']
            st.session_state.cells_config[i]['voltage'] = st.session_state.monitor.generate_random_voltage(cell_type)
            st.session_state.cells_config[i]['current'] = st.session_state.monitor.generate_random_current()
        st.rerun()

# Real-time monitoring controls
st.sidebar.markdown("---")
st.sidebar.subheader("📊 Real-Time Monitoring")

if not st.session_state.monitoring_active:
    if st.sidebar.button("▶️ Start Monitoring", use_container_width=True):
        st.session_state.monitoring_active = True
        st.rerun()
else:
    if st.sidebar.button("⏹️ Stop Monitoring", use_container_width=True):
        st.session_state.monitoring_active = False
        st.rerun()

# Auto-refresh for real-time monitoring
if st.session_state.monitoring_active:
    # Simulate parameter variations
    for i in range(8):
        voltage_variation = random.uniform(-0.05, 0.05)
        current_variation = random.uniform(-0.1, 0.1)
        
        new_voltage = max(0, st.session_state.cells_config[i]['voltage'] + voltage_variation)
        new_current = max(0, st.session_state.cells_config[i]['current'] + current_variation)
        
        st.session_state.cells_config[i]['voltage'] = round(new_voltage, 2)
        st.session_state.cells_config[i]['current'] = round(new_current, 2)
    
    time.sleep(1)
    st.rerun()

# Process data
cells_data = st.session_state.monitor.process_cells_data(st.session_state.cells_config)
df = pd.DataFrame(cells_data)

# Main dashboard
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📊 Live Monitoring Dashboard")
    
    # Status indicators
    status_col1, status_col2, status_col3 = st.columns(3)
    
    with status_col1:
        monitoring_status = "🟢 Active" if st.session_state.monitoring_active else "🔴 Inactive"
        st.metric("Monitoring Status", monitoring_status)
    
    with status_col2:
        avg_voltage = df['Voltage_V'].mean()
        st.metric("Avg Voltage", f"{avg_voltage:.2f} V")
    
    with status_col3:
        total_power = df['Power_W'].sum()
        st.metric("Total Power", f"{total_power:.2f} W")

with col2:
    st.subheader("⏰ System Info")
    st.write(f"**Bench:** {bench_name}")
    st.write(f"**Group:** {group_number}")
    st.write(f"**Last Update:** {datetime.now().strftime('%H:%M:%S')}")

# Data table
st.subheader("📋 Cell Status Table")

# Format the dataframe for display
display_df = df.copy()
display_df = display_df.drop(['Specs'], axis=1)

# Apply status styling
def style_status(val):
    if val == 'LOW':
        return 'background-color: #f8d7da; color: #721c24'
    elif val == 'HIGH':
        return 'background-color: #d1ecf1; color: #0c5460'
    else:
        return 'background-color: #d4edda; color: #155724'

styled_df = display_df.style.applymap(style_status, subset=['Status'])
st.dataframe(styled_df, use_container_width=True)

# Charts section
st.subheader("📈 Data Visualizations")

# Create chart tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Voltage Distribution", "🥧 Cell Types", "⚡ Power Output", "🌡️ Temperature"])

with tab1:
    fig_voltage = px.bar(
        df, 
        x='Cell_ID', 
        y='Voltage_V',
        color='Type',
        title='Voltage Distribution Across Cells',
        labels={'Voltage_V': 'Voltage (V)', 'Cell_ID': 'Cell ID'}
    )
    fig_voltage.update_layout(height=400)
    st.plotly_chart(fig_voltage, use_container_width=True)

with tab2:
    type_counts = df['Type'].value_counts()
    fig_pie = px.pie(
        values=type_counts.values,
        names=type_counts.index,
        title='Cell Type Distribution'
    )
    fig_pie.update_layout(height=400)
    st.plotly_chart(fig_pie, use_container_width=True)

with tab3:
    fig_power = px.bar(
        df,
        x='Cell_ID',
        y='Power_W',
        color='Type',
        title='Power Output by Cell',
        labels={'Power_W': 'Power (W)', 'Cell_ID': 'Cell ID'}
    )
    fig_power.update_layout(height=400)
    st.plotly_chart(fig_power, use_container_width=True)

with tab4:
    fig_temp = px.line(
        df,
        x='Cell_ID',
        y='Temperature_C',
        title='Temperature Monitoring',
        labels={'Temperature_C': 'Temperature (°C)', 'Cell_ID': 'Cell ID'},
        markers=True
    )
    fig_temp.update_layout(height=400)
    st.plotly_chart(fig_temp, use_container_width=True)

# Alerts section
st.subheader("🚨 System Alerts")

alerts = []
for _, cell in df.iterrows():
    if cell['Status'] == 'LOW':
        alerts.append(f"⚠️ {cell['Cell_ID']}: Low voltage ({cell['Voltage_V']}V)")
    elif cell['Status'] == 'HIGH':
        alerts.append(f"⚠️ {cell['Cell_ID']}: High voltage ({cell['Voltage_V']}V)")
    
    if cell['Temperature_C'] > 40:
        alerts.append(f"🌡️ {cell['Cell_ID']}: High temperature ({cell['Temperature_C']}°C)")
    
    if cell['SOC_%'] < 20:
        alerts.append(f"🔋 {cell['Cell_ID']}: Low state of charge ({cell['SOC_%']}%)")

if alerts:
    st.markdown('<div class="alert-box">', unsafe_allow_html=True)
    st.write("**Active Alerts:**")
    for alert in alerts:
        st.write(alert)
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.success("✅ All cells operating within normal parameters")

# Summary statistics
st.subheader("📈 Summary Statistics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Avg Voltage",
        f"{df['Voltage_V'].mean():.2f} V",
        f"{df['Voltage_V'].std():.2f} σ"
    )

with col2:
    st.metric(
        "Avg Current",
        f"{df['Current_A'].mean():.2f} A",
        f"{df['Current_A'].std():.2f} σ"
    )

with col3:
    st.metric(
        "Total Power",
        f"{df['Power_W'].sum():.2f} W",
        f"{df['Power_W'].mean():.2f} avg"
    )

with col4:
    st.metric(
        "Avg Temperature",
        f"{df['Temperature_C'].mean():.1f} °C",
        f"{df['Temperature_C'].std():.1f} σ"
    )

# Advanced analytics
with st.expander("🔬 Advanced Analytics"):
    st.subheader("Cell Performance Matrix")
    
    # Create a correlation matrix
    numeric_cols = ['Voltage_V', 'Current_A', 'Power_W', 'Temperature_C', 'SOC_%']
    corr_matrix = df[numeric_cols].corr()
    
    fig_heatmap = px.imshow(
        corr_matrix,
        title="Parameter Correlation Matrix",
        color_continuous_scale="RdBu_r",
        aspect="auto"
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # Efficiency analysis
    st.subheader("Efficiency Analysis")
    df['Efficiency'] = df['Power_W'] / (df['Voltage_V'] * df['Current_A']) * 100
    
    fig_eff = px.scatter(
        df,
        x='Voltage_V',
        y='Power_W',
        size='Current_A',
        color='Type',
        title='Voltage vs Power (bubble size = Current)',
        labels={'Voltage_V': 'Voltage (V)', 'Power_W': 'Power (W)'}
    )
    st.plotly_chart(fig_eff, use_container_width=True)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "Battery Cell Management System v2.0 | "
    f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    "</div>",
    unsafe_allow_html=True
)
