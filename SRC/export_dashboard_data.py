import os
import sqlite3
import pandas as pd
from logger import setup_logger

logger = setup_logger()

def prepare_dashboard_mart(project_root):
    db_path = os.path.join(project_root, "data", "delhi_traffic.db")
    dashboard_csv_path = os.path.join(project_root, "data", "processed", "tableau_powerbi_dashboard_mart.csv")

    logger.info("=========================================================")
    logger.info("📊 STARTING PHASE 17: DASHBOARD DATA MART EXPORT ENGINE")
    logger.info("=========================================================")

    conn = sqlite3.connect(db_path)

    # 1. Complex SQL Query to build Tableau/PowerBI Master Fact View
    logger.info("1️⃣ Executing Analytical View Query for Dashboard Export...")
    query = """
    SELECT 
        rowid AS Traffic_ID,
        Date,
        Time,
        Time_24Hr,
        Hour,
        Day_Of_Week,
        Is_Weekend,
        Is_Peak_Hour,
        Day_Part,
        Car_Count,
        Bike_Count,
        Bus_Count,
        Truck_Count,
        Total_Vehicles,
        PCU_Score,
        Congestion_Index,
        Heavy_Vehicle_Ratio,
        Bus_To_Car_Ratio,
        Traffic_Situation,
        
        -- Calculated KPI Metrics for Direct Dashboard Drag-and-Drop
        CASE 
            WHEN Is_Weekend = 1 THEN 'Weekend'
            ELSE 'Weekday'
        END AS Day_Type,

        CASE 
            WHEN Hour BETWEEN 7 AND 10 THEN 'Morning Rush (7-10 AM)'
            WHEN Hour BETWEEN 16 AND 19 THEN 'Evening Rush (4-7 PM)'
            WHEN Hour BETWEEN 20 AND 23 THEN 'Night Freight (8-11 PM)'
            ELSE 'Off-Peak Hours'
        END AS Rush_Hour_Category,

        ROUND((Bus_Count + Truck_Count) * 1.0 / (Total_Vehicles + 1e-5), 4) AS Commercial_Vehicle_Share,
        ROUND((Car_Count * 1.0) / (Total_Vehicles + 1e-5) * 100, 2) AS Car_Volume_Percentage

    FROM fact_traffic_ml_features
    ORDER BY Date, Hour;
    """

    df_dashboard = pd.read_sql(query, conn)
    conn.close()

    # 2. Export Master CSV
    os.makedirs(os.path.dirname(dashboard_csv_path), exist_ok=True)
    df_dashboard.to_csv(dashboard_csv_path, index=False)
    
    logger.info(f"2️⃣ Exported Master Dashboard Mart Dataset ({len(df_dashboard):,} rows) -> {dashboard_csv_path}")

    logger.info("\n=========================================================")
    logger.info("🎉 DASHBOARD DATASET CREATED SUCCESSFULLY!")
    logger.info("=========================================================")

if __name__ == "__main__":
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
    prepare_dashboard_mart(PROJECT_ROOT)