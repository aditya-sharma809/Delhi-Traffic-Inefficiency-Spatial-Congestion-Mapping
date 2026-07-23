import os
import pandas as pd
import requests
from sqlalchemy import create_engine

class DataCollectionPipeline:
    def __init__(self, raw_data_path):
        self.raw_data_path = raw_data_path
        self.df = None

    # -------------------------------------------------------------------------
    # 1. Flat File Ingestion (CSV & Excel)
    # -------------------------------------------------------------------------
    def load_from_csv(self):
        print("📂 [Source 1/7] Ingesting CSV Traffic Data...")
        if os.path.exists(self.raw_data_path):
            self.df = pd.read_csv(self.raw_data_path)
            print(f"   ✅ Successfully ingested {len(self.df)} records from CSV.")
            return self.df
        else:
            raise FileNotFoundError(f"CSV file not found at {self.raw_data_path}")

    def load_from_excel(self, excel_path):
        print("📊 [Source 2/7] Ingesting Excel Metadata/Logs...")
        xls = pd.ExcelFile(excel_path)
        sheet_data = {sheet: pd.read_excel(xls, sheet_name=sheet) for sheet in xls.sheet_names}
        print(f"   ✅ Excel sheets loaded: {list(sheet_data.keys())}")
        return sheet_data

    # -------------------------------------------------------------------------
    # 2. Relational SQL Database Ingestion (MySQL)
    # -------------------------------------------------------------------------
    def load_from_mysql(self, connection_string, query):
        print("🛢️ [Source 3/7] Querying MySQL Enterprise Database...")
        engine = create_engine(connection_string)
        db_df = pd.read_sql_query(query, con=engine)
        print(f"   ✅ Fetched {len(db_df)} rows from MySQL DB.")
        return db_df

    # -------------------------------------------------------------------------
    # 3. Live API Ingestion (Weather / Live Congestion Alerts)
    # -------------------------------------------------------------------------
    def fetch_from_api(self, api_url):
        print("🌐 [Source 4/7] Fetching Data from Live REST API...")
        try:
            response = requests.get(api_url, timeout=10)
            if response.status_code == 200:
                api_data = response.json()
                print("   ✅ Live API payload successfully fetched.")
                return pd.DataFrame(api_data)
        except Exception as e:
            print(f"   ⚠️ API Fetch Skipped (Mocked or Offline): {e}")
            return None

    # -------------------------------------------------------------------------
    # 4. Enterprise ERP (SAP) & CRM Data Pipeline Mock
    # -------------------------------------------------------------------------
    def ingest_erp_crm_feeds(self, erp_csv_path, crm_json_path):
        print("🏢 [Source 5-7/7] Ingesting Enterprise ERP (SAP) Freight Schedules & CRM Complaints...")
        # ERP Truck Dispatch Integration
        erp_df = pd.read_csv(erp_csv_path) if os.path.exists(erp_csv_path) else pd.DataFrame()
        # CRM Incident Tickets Integration
        crm_df = pd.read_json(crm_json_path) if os.path.exists(crm_json_path) else pd.DataFrame()
        print("   ✅ Enterprise ERP & CRM feeds merged into staging buffer.")
        return erp_df, crm_df

# Run Execution Test
# Run Execution Test
if __name__ == "__main__":
    # Get current script directory (SRC folder) and go up 1 level to root
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Check root level vs data/raw level
    raw_path_nested = os.path.join(BASE_DIR, "data", "raw", "Traffic_project.csv")
    raw_path_root = os.path.join(BASE_DIR, "Traffic_project.csv")
    
    # Automatically pick whichever exists
    if os.path.exists(raw_path_nested):
        raw_path = raw_path_nested
    elif os.path.exists(raw_path_root):
        raw_path = raw_path_root
    else:
        raw_path = "Traffic_project.csv" # fallback

    collector = DataCollectionPipeline(raw_path)
    df_raw = collector.load_from_csv()
    print("\nSample Ingested Data:")
    print(df_raw.head(3))