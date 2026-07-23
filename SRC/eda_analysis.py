import os
import sqlite3
import pandas as pd
import numpy as np
from logger import setup_logger

logger = setup_logger()

def run_eda_analysis(project_root):
    db_path = os.path.join(project_root, "data", "delhi_traffic.db")
    output_report_path = os.path.join(project_root, "reports", "eda_statistical_summary.csv")

    logger.info("=========================================================")
    logger.info("📈 STARTING PHASE 11: EXPLORATORY DATA ANALYSIS (EDA)")
    logger.info("=========================================================")

    conn = sqlite3.connect(db_path)
    df = pd.read_sql("SELECT * FROM fact_traffic_ml_features;", conn)
    conn.close()

    # -------------------------------------------------------------------------
    # 1. NUMERICAL DISTRIBUTION & DESCRIPTIVE STATS (NumPy + Pandas)
    # -------------------------------------------------------------------------
    logger.info("\n1️⃣ STATISTICAL DISTRIBUTIONS & QUANTILES:")
    
    num_cols = ['Car_Count', 'Bike_Count', 'Bus_Count', 'Truck_Count', 'Total_Vehicles', 'PCU_Score', 'Congestion_Index']
    
    # Calculate Skewness, Kurtosis, and Percentiles using NumPy & Pandas
    stats_df = df[num_cols].describe().T
    stats_df['median'] = df[num_cols].median()
    stats_df['iqr'] = df[num_cols].apply(lambda x: np.percentile(x, 75) - np.percentile(x, 25))
    stats_df['skewness'] = df[num_cols].skew()
    stats_df['kurtosis'] = df[num_cols].kurtosis()

    print(stats_df[['mean', 'std', 'median', 'iqr', 'skewness', 'min', 'max']].round(2).to_string())

    # -------------------------------------------------------------------------
    # 2. VEHICLE TYPE SHARE & COMPOSITION ANALYSIS
    # -------------------------------------------------------------------------
    logger.info("\n2️⃣ TOTAL VEHICLE VOLUME SHARE & COMPOSITION:")
    
    total_cars = np.sum(df['Car_Count'])
    total_bikes = np.sum(df['Bike_Count'])
    total_buses = np.sum(df['Bus_Count'])
    total_trucks = np.sum(df['Truck_Count'])
    overall_total = np.sum(df['Total_Vehicles'])

    vehicle_share = pd.DataFrame({
        'Vehicle_Type': ['Cars', 'Bikes', 'Buses', 'Trucks'],
        'Total_Count': [total_cars, total_bikes, total_buses, total_trucks],
        'Share_Percentage': [
            np.round((total_cars / overall_total) * 100, 2),
            np.round((total_bikes / overall_total) * 100, 2),
            np.round((total_buses / overall_total) * 100, 2),
            np.round((total_trucks / overall_total) * 100, 2)
        ]
    })
    print(vehicle_share.to_string(index=False))

    # -------------------------------------------------------------------------
    # 3. HOURLY CONGESTION PATTERNS (DAY PART AGGREGATIONS)
    # -------------------------------------------------------------------------
    logger.info("\n3️⃣ CONGESTION METRICS BY DAY PART:")
    
    day_part_summary = df.groupby('Day_Part').agg(
        Avg_PCU=('PCU_Score', 'mean'),
        Max_PCU=('PCU_Score', 'max'),
        Avg_Vehicles=('Total_Vehicles', 'mean'),
        Avg_Congestion_Index=('Congestion_Index', 'mean'),
        Sample_Count=('PCU_Score', 'count')
    ).round(2).sort_values(by='Avg_PCU', ascending=False)

    print(day_part_summary.to_string())

    # -------------------------------------------------------------------------
    # 4. CORRELATION ANALYSIS MATRIX (PANDAS + NUMPY)
    # -------------------------------------------------------------------------
    logger.info("\n4️⃣ FEATURE CORRELATION MATRIX (Top Signals with PCU_Score):")
    
    corr_matrix = df[num_cols + ['Heavy_Vehicle_Ratio', 'Car_Ratio', 'Is_Peak_Hour']].corr()
    pcu_correlations = corr_matrix['PCU_Score'].sort_values(ascending=False).round(3)
    
    corr_df = pd.DataFrame({'Feature': pcu_correlations.index, 'Correlation_With_PCU': pcu_correlations.values})
    print(corr_df.to_string(index=False))

    # Export Report
    os.makedirs(os.path.dirname(output_report_path), exist_ok=True)
    stats_df.to_csv(output_report_path)
    logger.info(f"\n📊 Exported EDA Statistical Report -> {output_report_path}")

    logger.info("\n=========================================================")
    logger.info("🎉 EXPLORATORY DATA ANALYSIS (EDA) COMPLETED SUCCESSFULLY!")
    logger.info("=========================================================")

if __name__ == "__main__":
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
    run_eda_analysis(PROJECT_ROOT)