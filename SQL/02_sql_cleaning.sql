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

    # 1. TRIM & LOWER CASE
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

    conn.commit()
    conn.close()

    logger.info("=========================================================")
    logger.info("🎉 SQL DATA CLEANING ENGINE EXECUTED SUCCESSFULLY!")
    logger.info("=========================================================")

if __name__ == "__main__":
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
    execute_sql_cleaning(PROJECT_ROOT)