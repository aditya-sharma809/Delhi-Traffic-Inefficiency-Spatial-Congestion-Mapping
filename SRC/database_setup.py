import os
import sqlite3
from logger import setup_logger

logger = setup_logger()

def setup_sqlite_schema(project_root):
    """
    Deploys relational schema with PKs, FKs, Constraints, and Indexes in SQLite.
    """
    db_path = os.path.join(project_root, "data", "delhi_traffic.db")
    logger.info(f"🛢️ Initializing Database Schema in SQLite -> {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Enable Foreign Keys in SQLite
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Table Creation DDL with PK, Constraints & Indexes
    ddl_query = """
    CREATE TABLE IF NOT EXISTS fact_traffic_monitoring_v2 (
        Traffic_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Date INTEGER NOT NULL,
        Time TEXT NOT NULL,
        Time_24Hr TEXT NOT NULL,
        Hour INTEGER NOT NULL CHECK(Hour BETWEEN 0 AND 23),
        Day_Of_Week TEXT NOT NULL,
        Is_Weekend INTEGER NOT NULL CHECK(Is_Weekend IN (0,1)),
        Is_Peak_Hour INTEGER NOT NULL CHECK(Is_Peak_Hour IN (0,1)),
        Car_Count INTEGER NOT NULL CHECK(Car_Count >= 0),
        Bike_Count INTEGER NOT NULL CHECK(Bike_Count >= 0),
        Bus_Count INTEGER NOT NULL CHECK(Bus_Count >= 0),
        Truck_Count INTEGER NOT NULL CHECK(Truck_Count >= 0),
        Total_Vehicles INTEGER NOT NULL CHECK(Total_Vehicles >= 0),
        PCU_Score REAL NOT NULL,
        Heavy_Vehicle_Ratio REAL NOT NULL,
        Car_Ratio REAL NOT NULL,
        Traffic_Situation TEXT NOT NULL CHECK(Traffic_Situation IN ('low', 'normal', 'high', 'heavy'))
    );

    CREATE INDEX IF NOT EXISTS idx_hour_peak ON fact_traffic_monitoring_v2(Hour, Is_Peak_Hour);
    CREATE INDEX IF NOT EXISTS idx_traffic_sit ON fact_traffic_monitoring_v2(Traffic_Situation);
    """

    cursor.executescript(ddl_query)
    conn.commit()
    conn.close()
    logger.info("✅ Database Schema, Constraints, Primary Keys & Indexes Deployed Successfully!")

if __name__ == "__main__":
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
    setup_sqlite_schema(PROJECT_ROOT)