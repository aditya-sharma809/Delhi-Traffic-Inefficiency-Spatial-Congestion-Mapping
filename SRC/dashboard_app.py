import os
import sqlite3
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# Page Configuration
st.set_page_config(
    page_title="Delhi Traffic Analytics Dashboard",
    page_icon="🚦",
    layout="wide"
)

# Load Data Function
@st.cache_data
def load_data():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(project_root, "data", "delhi_traffic.db")
    conn = sqlite3.connect(db_path)
    df = pd.read_sql("SELECT * FROM fact_traffic_ml_features;", conn)
    conn.close()
    return df

df = load_data()

# Header
st.title("🚦 Delhi Traffic Congestion & Spatial Inefficiency Dashboard")
st.markdown("**Author:** Aditya Sharma | **Project:** Urban Traffic Analytics Engine")
st.markdown("---")

# -----------------------------------------------------------------------------
# SIDEBAR FILTERS
# -----------------------------------------------------------------------------
st.sidebar.header("🔍 Filter Options")

selected_day_part = st.sidebar.multiselect(
    "Select Day Part:",
    options=df['Day_Part'].unique(),
    default=df['Day_Part'].unique()
)

selected_peak = st.sidebar.radio(
    "Peak Hour Filter:",
    options=["All Traffic", "Peak Hours Only", "Off-Peak Only"]
)

# Apply Filters
filtered_df = df[df['Day_Part'].isin(selected_day_part)]

if selected_peak == "Peak Hours Only":
    filtered_df = filtered_df[filtered_df['Is_Peak_Hour'] == 1]
elif selected_peak == "Off-Peak Only":
    filtered_df = filtered_df[filtered_df['Is_Peak_Hour'] == 0]

# -----------------------------------------------------------------------------
# TOP KPI METRICS CARDS
# -----------------------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

total_vehicles = filtered_df['Total_Vehicles'].sum()
avg_pcu = filtered_df['PCU_Score'].mean()
car_share = (filtered_df['Car_Count'].sum() / filtered_df['Total_Vehicles'].sum()) * 100
max_pcu = filtered_df['PCU_Score'].max()

col1.metric("Total Vehicles Monitored", f"{total_vehicles:,}")
col2.metric("Average PCU Score", f"{avg_pcu:.1f}")
col3.metric("Private Car Volume Share", f"{car_share:.1f}%")
col4.metric("Peak Bottleneck PCU", f"{max_pcu:.1f}")

st.markdown("---")

# -----------------------------------------------------------------------------
# VISUALIZATIONS SECTION
# -----------------------------------------------------------------------------
row1_col1, row1_col2 = st.columns(2)

# Chart 1: Hourly PCU Trend
with row1_col1:
    st.subheader("📈 Hourly PCU Congestion Trend")
    hourly_avg = filtered_df.groupby('Hour')['PCU_Score'].mean().reset_index()
    
    fig1, ax1 = plt.subplots(figsize=(7, 4))
    ax1.plot(hourly_avg['Hour'], hourly_avg['PCU_Score'], marker='o', color='#1f77b4', linewidth=2)
    ax1.axvspan(7, 10, color='#ff7f0e', alpha=0.2, label='Morning Rush')
    ax1.axvspan(16, 19, color='#d62728', alpha=0.2, label='Evening Rush')
    ax1.set_xlabel('Hour of Day (0 - 23)')
    ax1.set_ylabel('Avg PCU Score')
    ax1.grid(True, linestyle='--', alpha=0.5)
    ax1.legend()
    st.pyplot(fig1)

# Chart 2: Vehicle Composition Donut
with row1_col2:
    st.subheader("🍩 Vehicle Fleet Composition")
    vehicle_totals = [
        filtered_df['Car_Count'].sum(),
        filtered_df['Bike_Count'].sum(),
        filtered_df['Bus_Count'].sum(),
        filtered_df['Truck_Count'].sum()
    ]
    labels = ['Cars', 'Bikes', 'Buses', 'Trucks']
    colors = ['#2ca02c', '#1f77b4', '#ff7f0e', '#d62728']

    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.pie(vehicle_totals, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors,
            wedgeprops=dict(width=0.4, edgecolor='w', linewidth=2))
    st.pyplot(fig2)

st.markdown("---")

# -----------------------------------------------------------------------------
# DETAILED DATA TABLE VIEW
# -----------------------------------------------------------------------------
st.subheader("📋 Granular Traffic Monitoring Data Mart")
st.dataframe(filtered_df[['Date', 'Time_24Hr', 'Hour', 'Day_Part', 'Car_Count', 'Bike_Count', 'Bus_Count', 'Truck_Count', 'Total_Vehicles', 'PCU_Score', 'Congestion_Index']].head(100), use_container_width=True)