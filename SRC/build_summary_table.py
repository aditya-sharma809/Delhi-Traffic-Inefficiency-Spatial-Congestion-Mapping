import os
import sqlite3
import pandas as pd
from logger import setup_logger

logger = setup_logger()

def create_summary_table(project_root):
    db_path = os.path.join(project_root, "data", "delhi_traffic.db")
    processed_csv_path = os.path.join(project_root, "data", "processed", "cleaned_traffic_features.csv")
    summary_csv_path = os.path.join(project_root, "data", "processed", "summary_daily_traffic_analytics.csv")

    logger.info("=========================================================")
    logger.info("🏗️ STARTING PHASE 9: BUILDING ONE CLEANED SUMMARY TABLE")
    logger.info("=========================================================")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. SQL DDL Statement to Create the Summary Analytics Table
    logger.info("1️⃣ Executing SQL DDL to create summary_daily_traffic_analytics schema...")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS summary_daily_traffic_analytics (
        Summary_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Date INTEGER NOT NULL,
        Day_Of_Week TEXT NOT NULL,
        Is_Weekend INTEGER NOT NULL,
        Total_Daily_Vehicles INTEGER NOT NULL,
        Total_Cars INTEGER NOT NULL,
        Total_Bikes INTEGER NOT NULL,
        Total_Buses INTEGER NOT NULL,
        Total_Trucks INTEGER NOT NULL,
        Avg_Daily_PCU REAL NOT NULL,
        Max_Peak_Hour_PCU REAL NOT NULL,
        Heavy_Vehicle_Percentage REAL NOT NULL,
        Peak_Hour_Vehicle_Share REAL NOT NULL,
        Primary_Congestion_Level TEXT NOT NULL
    );
    """)

    # 2. Advanced SQL Ingestion Query: Aggregating 15-min Intervals into Daily Summary Dimensions
    logger.info("2️⃣ Running SQL Analytical Aggregation Pipeline...")
    summary_sql_query = """
    WITH Daily_Aggregates AS (
        SELECT 
            Date,
            Day_Of_Week,
            Is_Weekend,
            SUM(Total_Vehicles) AS Total_Daily_Vehicles,
            SUM(Car_Count) AS Total_Cars,
            SUM(Bike_Count) AS Total_Bikes,
            SUM(Bus_Count) AS Total_Buses,
            SUM(Truck_Count) AS Total_Trucks,
            ROUND(AVG(PCU_Score), 2) AS Avg_Daily_PCU,
            ROUND(MAX(PCU_Score), 2) AS Max_Peak_Hour_PCU,
            ROUND(SUM(Bus_Count + Truck_Count) * 100.0 / SUM(Total_Vehicles), 2) AS Heavy_Vehicle_Percentage,
            ROUND(SUM(CASE WHEN Is_Peak_Hour = 1 THEN Total_Vehicles ELSE 0 END) * 100.0 / SUM(Total_Vehicles), 2) AS Peak_Hour_Vehicle_Share
        FROM fact_traffic_monitoring_v2
        GROUP BY Date, Day_Of_Week, Is_Weekend
    )
    SELECT 
        Date,
        Day_Of_Week,
        Is_Weekend,
        Total_Daily_Vehicles,
        Total_Cars,
        Total_Bikes,
        Total_Buses,
        Total_Trucks,
        Avg_Daily_PCU,
        Max_Peak_Hour_PCU,
        Heavy_Vehicle_Percentage,
        Peak_Hour_Vehicle_Share,
        CASE 
            WHEN Avg_Daily_PCU >= 200 THEN 'Critical Congestion Corridor'
            WHEN Avg_Daily_PCU BETWEEN 150 AND 199.99 THEN 'Heavy Traffic Bottleneck'
            WHEN Avg_Daily_PCU BETWEEN 100 AND 149.99 THEN 'Moderate Regular Flow'
            ELSE 'Low Traffic Flow'
        END AS Primary_Congestion_Level
    FROM Daily_Aggregates
    ORDER BY Date ASC;
    """

    df_summary = pd.read_sql(summary_sql_query, conn)

    # 3. Save Summary Table to SQLite DB
    logger.info("3️⃣ Ingesting Summary Table into SQLite Database...")
    df_summary.to_sql("summary_daily_traffic_analytics", conn, if_exists="replace", index=False)

    # 4. Export Summary Table to Processed CSV for Tableau / PowerBI / Reporting
    os.makedirs(os.path.dirname(summary_csv_path), exist_ok=True)
    df_summary.to_csv(summary_csv_path, index=False)
    logger.info(f"4️⃣ Exported Cleaned Summary Table -> {summary_csv_path}")

    conn.close()

    logger.info("\n📊 SUMMARY TABLE AUDIT PREVIEW (Top 5 Days):")
    print(df_summary.head(5).to_string(index=False))

    logger.info("\n=========================================================")
    logger.info("🎉 ONE CLEANED SUMMARY TABLE CREATED & LOADED SUCCESSFULLY!")
    logger.info("=========================================================")

if __name__ == "__main__":
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
    create_summary_table(PROJECT_ROOT)