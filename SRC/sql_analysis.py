import os
import sqlite3
import pandas as pd
from logger import setup_logger

logger = setup_logger()

def execute_sql_analysis(project_root):
    db_path = os.path.join(project_root, "data", "delhi_traffic.db")
    csv_path = os.path.join(project_root, "data", "processed", "cleaned_traffic_features.csv")
    
    logger.info("=========================================================")
    logger.info("📊 STARTING PHASE 8: ADVANCED SQL ANALYSIS ENGINE")
    logger.info("=========================================================")

    conn = sqlite3.connect(db_path)
    
    # 0. DATA POPULATION SAFEGUARD
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM fact_traffic_monitoring_v2;")
    count = cursor.fetchone()[0]
    
    if count == 0 and os.path.exists(csv_path):
        logger.info("⚡ Auto-populating fact_traffic_monitoring_v2 from processed CSV...")
        df_clean = pd.read_csv(csv_path)
        df_clean.to_sql("fact_traffic_monitoring_v2", conn, if_exists="replace", index=False)
        logger.info(f"✅ Loaded {len(df_clean):,} records into fact_traffic_monitoring_v2.")

    # -------------------------------------------------------------------------
    # 1. AGGREGATION + GROUP BY + HAVING
    # -------------------------------------------------------------------------
    logger.info("\n🔹 1. [AGGREGATION + GROUP BY + HAVING] Peak Volume Hours (>150 Vehicles Avg):")
    query_1 = """
    SELECT 
        Hour,
        COUNT(*) AS Total_Intervals,
        ROUND(AVG(Car_Count), 1) AS Avg_Cars,
        ROUND(AVG(Truck_Count), 1) AS Avg_Trucks,
        ROUND(AVG(Total_Vehicles), 1) AS Avg_Total_Vehicles,
        ROUND(AVG(PCU_Score), 1) AS Avg_PCU_Score
    FROM fact_traffic_monitoring_v2
    GROUP BY Hour
    HAVING AVG(Total_Vehicles) > 150
    ORDER BY Avg_Total_Vehicles DESC;
    """
    df_q1 = pd.read_sql(query_1, conn)
    print(df_q1.to_string(index=False))

    # -------------------------------------------------------------------------
    # 2. CTE + SUBQUERY
    # -------------------------------------------------------------------------
    logger.info("\n🔹 2. [CTE + SUBQUERY] Days Exceeding Monthly Hourly Average:")
    query_2 = """
    WITH Hourly_Summary AS (
        SELECT 
            Date,
            Day_Of_Week,
            Hour,
            SUM(Total_Vehicles) AS Daily_Hourly_Volume,
            AVG(PCU_Score) AS Daily_Hourly_PCU
        FROM fact_traffic_monitoring_v2
        GROUP BY Date, Day_Of_Week, Hour
    )
    SELECT 
        hs.Date,
        hs.Day_Of_Week,
        hs.Hour,
        hs.Daily_Hourly_Volume,
        ROUND(hs.Daily_Hourly_PCU, 2) AS Daily_Hourly_PCU
    FROM Hourly_Summary hs
    WHERE hs.Daily_Hourly_Volume > (
        SELECT AVG(Total_Vehicles) * 4 FROM fact_traffic_monitoring_v2
    )
    ORDER BY hs.Daily_Hourly_Volume DESC
    LIMIT 5;
    """
    df_q2 = pd.read_sql(query_2, conn)
    print(df_q2.to_string(index=False))

    # -------------------------------------------------------------------------
    # 3. WINDOW FUNCTIONS & RANKING (DENSE_RANK & 1-Hour Moving Average)
    # Fixed: Using rowid instead of Traffic_ID for row ordering
    # -------------------------------------------------------------------------
    logger.info("\n🔹 3. [WINDOW FUNCTIONS & RANKING] Top 3 Worst Congestion Intervals Per Day:")
    query_3 = """
    WITH Ranked_Traffic AS (
        SELECT 
            Date,
            Day_Of_Week,
            Time,
            Total_Vehicles,
            Traffic_Situation,
            PCU_Score,
            DENSE_RANK() OVER (
                PARTITION BY Date 
                ORDER BY PCU_Score DESC
            ) AS Congestion_Rank,
            ROUND(AVG(Total_Vehicles) OVER (
                PARTITION BY Date 
                ORDER BY rowid 
                ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
            ), 1) AS Rolling_1Hr_Avg_Total
        FROM fact_traffic_monitoring_v2
    )
    SELECT 
        Date,
        Day_Of_Week,
        Time,
        Total_Vehicles,
        Rolling_1Hr_Avg_Total,
        PCU_Score,
        Traffic_Situation
    FROM Ranked_Traffic
    WHERE Congestion_Rank <= 3
    ORDER BY Date ASC, PCU_Score DESC
    LIMIT 10;
    """
    df_q3 = pd.read_sql(query_3, conn)
    print(df_q3.to_string(index=False))

    conn.close()
    logger.info("\n=========================================================")
    logger.info("🎉 SQL ANALYSIS ENGINE EXECUTED SUCCESSFULLY!")
    logger.info("=========================================================")

if __name__ == "__main__":
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
    execute_sql_analysis(PROJECT_ROOT)