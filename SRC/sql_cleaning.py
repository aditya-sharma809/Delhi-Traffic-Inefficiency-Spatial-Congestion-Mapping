import os
import sqlite3
from logger import setup_logger

logger = setup_logger()

def execute_sql_cleaning(project_root):
    db_path = os.path.join(project_root, "data", "delhi_traffic.db")
    logger.info("=========================================================")
    logger.info("🧹 STARTING PHASE 7: SQL DATA CLEANING ENGINE")
    logger.info("=========================================================")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. TRIM & LOWER: Cleaning Whitespaces & Standardizing Categories
    logger.info("1️⃣ Executing TRIM & LOWER String Standardizations...")
    cursor.execute("""
        UPDATE fact_traffic_monitoring_v2 
        SET Day_Of_Week = TRIM(Day_Of_Week), 
            Traffic_Situation = LOWER(TRIM(Traffic_Situation));
    """)

    # 2. DELETE Outliers / Invalid Negative Values
    logger.info("2️⃣ Running Safety DELETE for Boundary Violations...")
    cursor.execute("""
        DELETE FROM fact_traffic_monitoring_v2 
        WHERE Total_Vehicles < 0 OR Car_Count < 0;
    """)

    # 3. DISTINCT Audit Check
    cursor.execute("SELECT COUNT(DISTINCT Traffic_ID) FROM fact_traffic_monitoring_v2;")
    distinct_count = cursor.fetchone()[0]
    logger.info(f"3️⃣ Deduplication Audit Check: Confirmed {distinct_count:,} DISTINCT unique records.")

    # 4. CASE STATEMENT & CAST / COALESCE Verification
    logger.info("4️⃣ Testing CASE Statement Congestion Banding & CAST/COALESCE...")
    cursor.execute("""
        SELECT 
            Traffic_ID,
            Total_Vehicles,
            PCU_Score,
            CAST(COALESCE(Car_Count, 0) AS INTEGER) AS Clean_Cars,
            CASE 
                WHEN PCU_Score >= 300 THEN 'Severe Bottleneck'
                WHEN PCU_Score BETWEEN 200 AND 299 THEN 'Moderate Congestion'
                WHEN PCU_Score BETWEEN 100 AND 199 THEN 'Standard Flow'
                ELSE 'Free Flow'
            END AS Congestion_Band
        FROM fact_traffic_monitoring_v2
        LIMIT 5;
    """)
    rows = cursor.fetchall()
    for r in rows:
        logger.info(f"   • ID {r[0]}: Total={r[1]}, PCU={r[2]}, CleanCars={r[3]} -> Band: {r[4]}")

    conn.commit()
    conn.close()

    logger.info("=========================================================")
    logger.info("🎉 SQL DATA CLEANING ENGINE EXECUTED SUCCESSFULLY!")
    logger.info("=========================================================")

if __name__ == "__main__":
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
    execute_sql_cleaning(PROJECT_ROOT)