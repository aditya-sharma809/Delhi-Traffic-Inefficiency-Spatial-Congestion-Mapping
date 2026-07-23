import os
import sqlite3
import pandas as pd
from logger import setup_logger

logger = setup_logger()

class DataValidator:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.passed_tests = 0
        self.total_tests = 5

    def run_all_validations(self):
        logger.info("=========================================================")
        logger.info("🔍 STARTING PHASE 6: DATA VALIDATION & QUALITY AUDIT")
        logger.info("=========================================================")

        self.check_row_count()
        self.check_nulls_and_duplicates()
        self.check_business_logic_sum()
        self.check_range_constraints()
        self.check_time_continuity()

        logger.info("---------------------------------------------------------")
        logger.info(f"📊 AUDIT SUMMARY: Passed {self.passed_tests}/{self.total_tests} Quality Gate Checks.")
        logger.info("=========================================================")

        self.conn.close()

    # Test 1: Record Count Audit
    def check_row_count(self):
        query = "SELECT COUNT(*) FROM fact_traffic_monitoring_v2;"
        count = self.conn.execute(query).fetchone()[0]
        if count == 2976:
            logger.info(f"✅ [Test 1/5 PASSED] Row Count Verification: Found exact expected {count:,} records.")
            self.passed_tests += 1
        else:
            logger.error(f"❌ [Test 1/5 FAILED] Unexpected Row Count: Found {count} (Expected 2,976).")

    # Test 2: Null & Duplicate Audit
    def check_nulls_and_duplicates(self):
        df = pd.read_sql("SELECT * FROM fact_traffic_monitoring_v2;", self.conn)
        null_count = df.isnull().sum().sum()
        dup_count = df.duplicated(subset=['Date', 'Time']).sum()

        if null_count == 0 and dup_count == 0:
            logger.info("✅ [Test 2/5 PASSED] Data Integrity: Zero NULL values & Zero Duplicate Time-Slots.")
            self.passed_tests += 1
        else:
            logger.error(f"❌ [Test 2/5 FAILED] Found {null_count} Nulls and {dup_count} Duplicates.")

    # Test 3: Business Logic Equation Check
    def check_business_logic_sum(self):
        query = """
        SELECT COUNT(*) 
        FROM fact_traffic_monitoring_v2 
        WHERE Total_Vehicles != (Car_Count + Bike_Count + Bus_Count + Truck_Count);
        """
        mismatches = self.conn.execute(query).fetchone()[0]
        if mismatches == 0:
            logger.info("✅ [Test 3/5 PASSED] Business Logic Check: Total_Vehicles perfectly equals component sum.")
            self.passed_tests += 1
        else:
            logger.error(f"❌ [Test 3/5 FAILED] Found {mismatches} mathematical discrepancy rows.")

    # Test 4: Range & Boundary Validation
    def check_range_constraints(self):
        query = """
        SELECT COUNT(*) 
        FROM fact_traffic_monitoring_v2 
        WHERE Heavy_Vehicle_Ratio < 0 OR Heavy_Vehicle_Ratio > 1
           OR Hour < 0 OR Hour > 23
           OR Is_Peak_Hour NOT IN (0, 1);
        """
        out_of_bounds = self.conn.execute(query).fetchone()[0]
        if out_of_bounds == 0:
            logger.info("✅ [Test 4/5 PASSED] Boundary Checks: All metrics, ratios, and hours fall within valid ranges.")
            self.passed_tests += 1
        else:
            logger.error(f"❌ [Test 4/5 FAILED] Found {out_of_bounds} boundary violation records.")

    # Test 5: Time Series Continuity (4 slots per hour x 24 hours = 96 per day)
    def check_time_continuity(self):
        query = "SELECT Date, COUNT(*) as slots FROM fact_traffic_monitoring_v2 GROUP BY Date;"
        df_slots = pd.read_sql(query, self.conn)
        invalid_days = df_slots[df_slots['slots'] != 96]

        if len(invalid_days) == 0:
            logger.info("✅ [Test 5/5 PASSED] Time Continuity: All 31 Days have complete 96 15-minute time intervals.")
            self.passed_tests += 1
        else:
            logger.error(f"❌ [Test 5/5 FAILED] Found {len(invalid_days)} days with missing time slots.")

if __name__ == "__main__":
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
    db_path = os.path.join(PROJECT_ROOT, "data", "delhi_traffic.db")

    validator = DataValidator(db_path)
    validator.run_all_validations()