import os
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from logger import setup_logger

logger = setup_logger()

def generate_visualizations(project_root):
    db_path = os.path.join(project_root, "data", "delhi_traffic.db")
    figures_dir = os.path.join(project_root, "reports", "figures")
    os.makedirs(figures_dir, exist_ok=True)

    logger.info("=========================================================")
    logger.info("🎨 STARTING PHASE 12: DATA VISUALIZATION ENGINE")
    logger.info("=========================================================")

    conn = sqlite3.connect(db_path)
    df = pd.read_sql("SELECT * FROM fact_traffic_ml_features;", conn)
    conn.close()

    # -------------------------------------------------------------------------
    # 1. Hourly PCU Trend Plot
    # -------------------------------------------------------------------------
    logger.info("1️⃣ Generating Chart 1: Hourly PCU Progression Trend...")
    fig1, ax1 = plt.subplots(figsize=(10, 5))
    hourly_avg = df.groupby('Hour')['PCU_Score'].mean().reset_index()
    ax1.plot(hourly_avg['Hour'], hourly_avg['PCU_Score'], marker='o', color='#1f77b4', linewidth=2.5, label='Avg PCU Score')
    ax1.axvspan(7, 10, color='#ff7f0e', alpha=0.2, label='Morning Rush')
    ax1.axvspan(16, 19, color='#d62728', alpha=0.2, label='Evening Rush')
    ax1.set_title('Hourly PCU Congestion Trend & Rush Windows', fontsize=14, fontweight='bold', pad=15)
    ax1.set_xlabel('Hour of Day (0 - 23)', fontsize=11)
    ax1.set_ylabel('Average PCU Score', fontsize=11)
    ax1.set_xticks(range(0, 24))
    ax1.grid(True, linestyle='--', alpha=0.5)
    ax1.legend(loc='upper right')
    fig1.tight_layout()
    
    fig1_path = os.path.join(figures_dir, "01_hourly_pcu_trend.png")
    fig1.savefig(fig1_path, dpi=300, bbox_inches='tight')
    plt.close(fig1)
    logger.info(f"   ✅ CHART 1 SAVED: {fig1_path}")

    # -------------------------------------------------------------------------
    # 2. Vehicle Mix Share (Donut Chart)
    # -------------------------------------------------------------------------
    logger.info("2️⃣ Generating Chart 2: Vehicle Composition Donut Chart...")
    fig2, ax2 = plt.subplots(figsize=(7, 7))
    vehicle_totals = [
        df['Car_Count'].sum(),
        df['Bike_Count'].sum(),
        df['Bus_Count'].sum(),
        df['Truck_Count'].sum()
    ]
    labels = ['Cars', 'Bikes', 'Buses', 'Trucks']
    colors = ['#2ca02c', '#1f77b4', '#ff7f0e', '#d62728']
    
    ax2.pie(vehicle_totals, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors, 
            wedgeprops=dict(width=0.4, edgecolor='w', linewidth=2), textprops={'fontsize': 11, 'weight': 'bold'})
    ax2.set_title('Traffic Composition Share by Vehicle Type', fontsize=14, fontweight='bold', pad=15)
    fig2.tight_layout()

    fig2_path = os.path.join(figures_dir, "02_vehicle_composition_donut.png")
    fig2.savefig(fig2_path, dpi=300, bbox_inches='tight')
    plt.close(fig2)
    logger.info(f"   ✅ CHART 2 SAVED: {fig2_path}")

    # -------------------------------------------------------------------------
    # 3. Congestion Index Bar Chart by Day Part
    # -------------------------------------------------------------------------
    logger.info("3️⃣ Generating Chart 3: Day Part Congestion Bar Chart...")
    fig3, ax3 = plt.subplots(figsize=(8, 5))
    day_part_avg = df.groupby('Day_Part')['Congestion_Index'].mean().reindex(['Morning', 'Afternoon', 'Evening', 'Night'])
    bars = ax3.bar(day_part_avg.index, day_part_avg.values, color=['#1f77b4', '#2ca02c', '#d62728', '#9467bd'], width=0.5)
    
    for bar in bars:
        yval = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2, yval + 0.02, round(yval, 2), ha='center', va='bottom', fontweight='bold')

    ax3.set_title('Average Congestion Index Across Day Parts', fontsize=14, fontweight='bold', pad=15)
    ax3.set_xlabel('Day Part', fontsize=11)
    ax3.set_ylabel('Average Congestion Index', fontsize=11)
    ax3.grid(axis='y', linestyle='--', alpha=0.5)
    fig3.tight_layout()

    fig3_path = os.path.join(figures_dir, "03_daypart_congestion_barchart.png")
    fig3.savefig(fig3_path, dpi=300, bbox_inches='tight')
    plt.close(fig3)
    logger.info(f"   ✅ CHART 3 SAVED: {fig3_path}")

    # -------------------------------------------------------------------------
    # 4. Feature Correlation Matrix
    # -------------------------------------------------------------------------
    logger.info("4️⃣ Generating Chart 4: Correlation Matrix...")
    fig4, ax4 = plt.subplots(figsize=(8, 6))
    corr_cols = ['Car_Count', 'Bike_Count', 'Bus_Count', 'Truck_Count', 'Total_Vehicles', 'PCU_Score', 'Heavy_Vehicle_Ratio', 'Is_Peak_Hour']
    corr_matrix = df[corr_cols].corr().values

    im = ax4.imshow(corr_matrix, cmap='coolwarm', interpolation='nearest')
    fig4.colorbar(im)
    
    ax4.set_xticks(range(len(corr_cols)))
    ax4.set_xticklabels(corr_cols, rotation=45, ha='right')
    ax4.set_yticks(range(len(corr_cols)))
    ax4.set_yticklabels(corr_cols)
    
    for i in range(len(corr_cols)):
        for j in range(len(corr_cols)):
            ax4.text(j, i, f"{corr_matrix[i, j]:.2f}", ha='center', va='center', color='black', fontsize=9)

    ax4.set_title('Traffic Attribute Correlation Matrix', fontsize=14, fontweight='bold', pad=15)
    fig4.tight_layout()

    fig4_path = os.path.join(figures_dir, "04_correlation_matrix.png")
    fig4.savefig(fig4_path, dpi=300, bbox_inches='tight')
    plt.close(fig4)
    logger.info(f"   ✅ CHART 4 SAVED: {fig4_path}")

    logger.info("=========================================================")
    logger.info("🎉 ALL 4 VISUALIZATION CHARTS CREATED & SAVED LOCALLY!")
    logger.info("=========================================================")

if __name__ == "__main__":
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
    generate_visualizations(PROJECT_ROOT)