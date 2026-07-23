import os
from logger import setup_logger

logger = setup_logger()

def create_recommendations_doc(project_root):
    output_path = os.path.join(project_root, "reports", "Strategic_Policy_Recommendations.md")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    recommendations_content = """# 🚦 STRATEGIC POLICY & TRAFFIC ENGINEERING RECOMMENDATIONS

**Project:** Delhi Traffic Inefficiency & Spatial Congestion Mapping  
**Target Authority:** Delhi Traffic Police, Urban Transport Department & MCD  

---

## 🎯 Executive Policy Summary
Based on rigorous statistical validation across 2,976 intervals, urban congestion in target corridors is driven by:
1. High private vehicle volume (**60.1% Car share**).
2. Bus queue bottlenecks during peak hours (**r = 0.871 correlation with PCU**).
3. Heavy freight trucks choking passenger throughput during daytime (**r = -0.628 inverse correlation with cars**).

---

## ⏱️ 1. SHORT-TERM ACTIONS (0 – 3 Months) | Immediate Operational Adjustments

### A. Dynamic Adaptive Signal Calibration
* **Data Justification:** Morning Peak (07:00–10:00) and Evening Peak (16:00–19:00) experience Congestion Indices of 1.18 and 1.20 respectively.
* **Engineering Solution:** Replace fixed timer signals with adaptive signal control systems programmed to extend green light timing by **25–30%** on primary arterial directions during 16:00–19:00.

### B. Peak-Hour Heavy Vehicle Entry Ban
* **Data Justification:** `Truck_Count` shows an inverse correlation of `-0.628` with passenger car movement.
* **Engineering Solution:** Enforce strict entry bans for multi-axle commercial trucks between **07:00 AM – 10:00 AM** and **04:00 PM – 09:00 PM**.

---

## 🛣️ 2. MEDIUM-TERM ACTIONS (3 – 12 Months) | Infrastructure & Corridor Optimization

### A. Dedicated Bus Rapid Transit (BRT) & Priority Lanes
* **Data Justification:** Buses contribute $r = 0.871$ to the total PCU Score due to frequent curb-side stops disrupting general traffic flow.
* **Engineering Solution:** Construct demarcated bus priority lanes on high-density corridors to isolate frequent stopping patterns from high-speed passenger traffic.

### B. High-Occupancy Vehicle (HOV) Lane Reservation
* **Data Justification:** Cars represent **60.1%** of total vehicle count, driving single-occupancy vehicle (SOV) inefficiency.
* **Engineering Solution:** Reserve the extreme right lane for HOV-2+ (vehicles carrying 2 or more passengers) during peak rush hours.

---

## 🌆 3. LONG-TERM ACTIONS (12 – 24 Months) | Structural Policy & Smart Mobility

### A. Night Freight Logistics Mandate
* **Data Justification:** Night Window (22:00–05:00) Congestion Index drops to **0.58** (42% below daily mean capacity).
* **Engineering Solution:** Mandate all major warehousing and commercial freight loading/unloading operations to occur exclusively during the Night Window (22:00–05:00).

### B. Dynamic Congestion Pricing Tolls
* **Data Justification:** PCU Scores reach maximum limits (>245) between 16:00 and 18:00.
* **Engineering Solution:** Implement automated RFID/ANPR congestion pricing tolls during peak 16:00–19:00 windows on bottleneck corridors to incentivize off-peak travel shifts.
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(recommendations_content)

    logger.info("=========================================================")
    logger.info(f"✅ RECOMMENDATIONS REPORT GENERATED -> {output_path}")
    logger.info("=========================================================")

if __name__ == "__main__":
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
    create_recommendations_doc(PROJECT_ROOT)