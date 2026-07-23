import os
import sqlite3
import pandas as pd
import numpy as np
from scipy import stats
from logger import setup_logger

logger = setup_logger()

def run_statistical_analysis(project_root):
    db_path = os.path.join(project_root, "data", "delhi_traffic.db")
    
    logger.info("=========================================================")
    logger.info("🧪 STARTING PHASE 14: STATISTICAL HYPOTHESIS TESTING")
    logger.info("=========================================================")

    conn = sqlite3.connect(db_path)
    df = pd.read_sql("SELECT * FROM fact_traffic_ml_features;", conn)
    conn.close()

    # -------------------------------------------------------------------------
    # 1. TWO-SAMPLE INDEPENDENT T-TEST
    # H0: Mean PCU Score during Peak Hours == Mean PCU Score during Off-Peak Hours
    # H1: Mean PCU Score during Peak Hours > Mean PCU Score during Off-Peak Hours
    # -------------------------------------------------------------------------
    logger.info("\n🔹 1. INDEPENDENT TWO-SAMPLE T-TEST (Peak vs Off-Peak PCU):")
    peak_pcu = df[df['Is_Peak_Hour'] == 1]['PCU_Score']
    offpeak_pcu = df[df['Is_Peak_Hour'] == 0]['PCU_Score']

    t_stat, p_val_t = stats.ttest_ind(peak_pcu, offpeak_pcu, equal_var=False)

    print(f"   • Peak Hours Mean PCU: {peak_pcu.mean():.2f}")
    print(f"   • Off-Peak Hours Mean PCU: {offpeak_pcu.mean():.2f}")
    print(f"   • T-Statistic: {t_stat:.4f}")
    print(f"   • P-Value: {p_val_t:.4e}")

    if p_val_t < 0.05:
        logger.info("   ✅ Conclusion: Reject H0 (p < 0.05). Statistically significant difference in PCU Score between Peak and Off-Peak hours.")
    else:
        logger.info("   ❌ Conclusion: Fail to reject H0.")

    # -------------------------------------------------------------------------
    # 2. ONE-WAY ANOVA TEST
    # H0: Congestion Index means are equal across all 4 Day Parts
    # H1: At least one Day Part has a significantly different mean Congestion Index
    # -------------------------------------------------------------------------
    logger.info("\n🔹 2. ONE-WAY ANOVA TEST (Congestion Index Across Day Parts):")
    morning = df[df['Day_Part'] == 'Morning']['Congestion_Index']
    afternoon = df[df['Day_Part'] == 'Afternoon']['Congestion_Index']
    evening = df[df['Day_Part'] == 'Evening']['Congestion_Index']
    night = df[df['Day_Part'] == 'Night']['Congestion_Index']

    f_stat, p_val_anova = stats.f_oneway(morning, afternoon, evening, night)

    print(f"   • F-Statistic: {f_stat:.4f}")
    print(f"   • P-Value: {p_val_anova:.4e}")

    if p_val_anova < 0.05:
        logger.info("   ✅ Conclusion: Reject H0 (p < 0.05). Significant variance exists across Day Parts.")
    else:
        logger.info("   ❌ Conclusion: Fail to reject H0.")

    # -------------------------------------------------------------------------
    # 3. 95% CONFIDENCE INTERVALS (PARAMETRIC & BOOTSTRAP)
    # -------------------------------------------------------------------------
    logger.info("\n🔹 3. 95% CONFIDENCE INTERVAL ESTIMATION:")
    
    def calc_95_ci(series):
        mean = series.mean()
        sem = stats.sem(series) # Standard Error of Mean
        ci = stats.t.interval(0.95, len(series)-1, loc=mean, scale=sem)
        return mean, ci[0], ci[1]

    mean_pcu, ci_low_pcu, ci_high_pcu = calc_95_ci(df['PCU_Score'])
    mean_vol, ci_low_vol, ci_high_vol = calc_95_ci(df['Total_Vehicles'])

    print(f"   • Population PCU Score Mean: {mean_pcu:.2f} | 95% CI: [{ci_low_pcu:.2f}, {ci_high_pcu:.2f}]")
    print(f"   • Population Vehicle Volume Mean: {mean_vol:.2f} | 95% CI: [{ci_low_vol:.2f}, {ci_high_vol:.2f}]")

    # -------------------------------------------------------------------------
    # 4. PEARSON CORRELATION SIGNIFICANCE TESTS
    # -------------------------------------------------------------------------
    logger.info("\n🔹 4. PEARSON CORRELATION STATISTICAL SIGNIFICANCE:")
    
    r_bus, p_bus = stats.pearsonr(df['Bus_Count'], df['PCU_Score'])
    r_truck, p_truck = stats.pearsonr(df['Truck_Count'], df['Car_Count'])

    print(f"   • Bus Count vs PCU Score: r = {r_bus:.3f} (p-value = {p_bus:.4e})")
    print(f"   • Truck Count vs Car Count: r = {r_truck:.3f} (p-value = {p_truck:.4e})")

    logger.info("=========================================================")
    logger.info("🎉 STATISTICAL ANALYSIS COMPLETED SUCCESSFULLY!")
    logger.info("=========================================================")

if __name__ == "__main__":
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
    run_statistical_analysis(PROJECT_ROOT)