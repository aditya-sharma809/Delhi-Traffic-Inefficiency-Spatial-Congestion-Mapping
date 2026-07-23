import os
import pandas as pd
import numpy as np
import sqlite3
from sqlalchemy import create_engine
from logger import setup_logger  # Importing central logger

# Initialize Logger
logger = setup_logger()

class TrafficETLPipeline:
    def __init__(self, raw_csv_path):
        self.raw_csv_path = raw_csv_path
        self.df = None
        self.processed_df = None

    def extract(self):
        logger.info("📥 [ETL - EXTRACT] Starting extraction from raw traffic dataset...")
        if os.path.exists(self.raw_csv_path):
            self.df = pd.read_csv(self.raw_csv_path)
            logger.info(f"✅ Extracted {len(self.df):,} rows successfully from {self.raw_csv_path}")
        else:
            logger.error(f"❌ Source file not found at: {self.raw_csv_path}")
            raise FileNotFoundError(f"Source file not found at: {self.raw_csv_path}")
        return self

    def transform(self):
        logger.info("⚙️ [ETL - TRANSFORM] Executing data cleaning, formatting & feature engineering...")
        df_trans = self.df.copy()

        # Clean Strings
        df_trans['Day_Of_Week'] = df_trans['Day of the week'].str.strip()
        df_trans['Traffic_Situation'] = df_trans['Traffic Situation'].str.strip().str.lower()
        df_trans.drop(columns=['Day of the week', 'Traffic Situation'], inplace=True)

        # Time Parsing
        time_dt = pd.to_datetime(df_trans['Time'], format='%I:%M:%S %p')
        df_trans['Time_24Hr'] = time_dt.dt.strftime('%H:%M:%S')
        df_trans['Hour'] = time_dt.dt.hour

        # Column Standardizing
        df_trans.rename(columns={
            'CarCount': 'Car_Count', 'BikeCount': 'Bike_Count',
            'BusCount': 'Bus_Count', 'TruckCount': 'Truck_Count',
            'Total': 'Total_Vehicles'
        }, inplace=True)

        # Domain Feature Engineering
        df_trans['PCU_Score'] = (
            (df_trans['Car_Count'] * 1.0) + (df_trans['Bike_Count'] * 0.5) + 
            (df_trans['Bus_Count'] * 3.0) + (df_trans['Truck_Count'] * 3.0)
        )
        df_trans['Heavy_Vehicle_Ratio'] = np.round((df_trans['Bus_Count'] + df_trans['Truck_Count']) / df_trans['Total_Vehicles'], 4)
        df_trans['Car_Ratio'] = np.round(df_trans['Car_Count'] / df_trans['Total_Vehicles'], 4)
        df_trans['Is_Peak_Hour'] = df_trans['Hour'].apply(lambda h: 1 if h in [6, 7, 8, 16, 17, 18] else 0)
        df_trans['Is_Weekend'] = df_trans['Day_Of_Week'].apply(lambda d: 1 if d in ['Saturday', 'Sunday'] else 0)

        self.processed_df = df_trans
        logger.info(f"✅ Transformation Complete: {len(self.processed_df.columns)} attributes engineered.")
        return self

    def load(self, project_root):
        logger.info("📤 [ETL - LOAD] Ingesting transformed dataset into storage layers...")
        
        # 1. Processed CSV
        processed_csv_path = os.path.join(project_root, "data", "processed", "cleaned_traffic_features.csv")
        os.makedirs(os.path.dirname(processed_csv_path), exist_ok=True)
        self.processed_df.to_csv(processed_csv_path, index=False)
        logger.info(f"✅ [Load 1/3] Processed CSV saved to: {processed_csv_path}")

        # 2. SQLite Database
        sqlite_db_path = os.path.join(project_root, "data", "delhi_traffic.db")
        conn_sqlite = sqlite3.connect(sqlite_db_path)
        self.processed_df.to_sql("fact_traffic_monitoring", conn_sqlite, if_exists="replace", index=False)
        conn_sqlite.close()
        logger.info(f"✅ [Load 2/3] Ingested into SQLite Database: {sqlite_db_path}")

        # 3. MySQL Database
        mysql_user, mysql_pass, mysql_host, mysql_db = "root", "your_password", "localhost", "delhi_traffic_db"
        try:
            mysql_engine = create_engine(f"mysql+pymysql://{mysql_user}:{mysql_pass}@{mysql_host}:3306/{mysql_db}")
            self.processed_df.to_sql("fact_traffic_monitoring", mysql_engine, if_exists="replace", index=False)
            logger.info(f"✅ [Load 3/3] Ingested into MySQL Database: {mysql_db}")
        except Exception as e:
            logger.warning(f"⚠️ [Load 3/3] MySQL Load Skipped: {e}")

        return self

if __name__ == "__main__":
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
    
    raw_path = os.path.join(PROJECT_ROOT, "data", "raw", "Traffic_project.csv")
    if not os.path.exists(raw_path):
        raw_path = os.path.join(PROJECT_ROOT, "Traffic_project.csv")

    logger.info("=========================================================")
    logger.info("🚀 STARTING ETL PIPELINE WITH PRODUCTION LOGGING")
    logger.info("=========================================================")

    pipeline = TrafficETLPipeline(raw_path)
    pipeline.extract().transform().load(PROJECT_ROOT)

    logger.info("=========================================================")
    logger.info("🎉 ETL PIPELINE EXECUTED WITH FULL LOG TRAIL!")
    logger.info("=========================================================")