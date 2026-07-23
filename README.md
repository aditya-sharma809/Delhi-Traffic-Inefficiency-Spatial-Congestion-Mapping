# 🚦 Delhi Traffic Inefficiency & Spatial Congestion Mapping

[![Python 3.10+](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![SciPy](https://img.shields.io/badge/SciPy-Hypothesis%20Testing-8CAAE6?style=for-the-badge&logo=scipy&logoColor=white)](https://scipy.org/)
[![Looker Studio](https://img.shields.io/badge/Looker_Studio-Dashboard-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://lookerstudio.google.com/)

An end-to-end Data Analytics Engineering pipeline analyzing urban vehicular movement, peak-hour bottlenecks, and spatial congestion inefficiencies across primary arterial corridors in Delhi.

---

## 📊 Executive Looker Studio Dashboard

We built and deployed an interactive **Looker Studio (Google Data Studio)** dashboard connected directly to our processed analytical data mart. 

![Looker Studio Dashboard]
<img width="365" height="272" alt="Screenshot of dashboard" src="https://github.com/user-attachments/assets/11ba967d-251d-4155-b27c-a4b943b89294" />


Live Dashboard

https://datastudio.google.com/reporting/a881f4e7-eb5b-4eb4-9244-95a425b8a4e1

---

## 🏗️ Project Architecture & Pipeline Flow (Google Data Analytics Lifecycle)

This project strictly follows the **Ask ➔ Prepare ➔ Process ➔ Analyze ➔ Share ➔ Act** framework:

text
Raw CSV / Database ➔ ETL Engine ➔ SQL Quality Audit ➔ Data Cleaning ➔ Feature Engineering
                                                                             │
Looker Studio Mart  Executive Reports  Policy Insights  Statistical Tests (SciPy)

🔍 Visual Analytics & Key Findings
1. Temporal Bottlenecks & Hourly TrendsThe data highlights severe capacity throttling during specific rush windows. The Evening Rush (16:00 – 19:00) experiences the highest strain, peaking at a PCU score of ~246, significantly above the daily baseline.
2. Vehicle Fleet DistributionPrivate cars dominate the arterial corridors, causing high Single-Occupancy Vehicle (SOV) congestion. Heavy commercial trucks and buses also occupy substantial spatial footprints, contributing disproportionately to road queuing.
3. Day Part Capacity DemandTraffic volume and congestion severity vary significantly across distinct day parts. The Congestion Index hits 1.20x during the Evening and 1.18x in the Morning, while dropping drastically to 0.58x during the Night Window.Average Congestion Index:Congestion Index Spread (Variance):
4. Traffic Attribute CorrelationsHeavy freight trucks (Truck_Count) show a strong inverse correlation (r = -0.628) with passenger cars (Car_Count), proving that daytime commercial truck movement significantly degrades passenger vehicle speed and road capacity. Conversely, buses show a high positive correlation (r = 0.871) with overall PCU scores due to curb-side stopping dynamics.

🧪 Statistical Hypothesis Testing & Validation
To ensure all analytical findings are mathematically sound and not artifacts of random noise, rigorous parametric tests were performed using SciPy:

<img width="857" height="108" alt="Screenshot 2026-07-23 215705" src="https://github.com/user-attachments/assets/e4808e95-c900-4d16-b86b-004a6aab1273" />

🚀 Actionable Policy & Engineering Recommendations

Based on quantitative evidence, the following 3-tier implementation roadmap is proposed to urban transit authorities:
Short-Term (0–3 Months) | Dynamic Signal Optimization: Replace static timer signals with adaptive signal controllers programmed to extend green light timing by 25–30% during the Evening Peak window (16:00–19:00).
Medium-Term (3–12 Months) | Priority Transit Corridors: Demarcate dedicated Bus Rapid Transit (BRT) lanes to isolate frequent stopping patterns (r=0.871) from high-speed passenger traffic, and introduce HOV-2+ lanes for cars.
Long-Term (12–24 Months) | Night Logistics Mandate: Restrict heavy multi-axle truck entry during peak daylight hours. Shift commercial freight logistics exclusively to the Night Window (22:00–05:00), leveraging the vastly underutilized road capacity (Congestion Index = 0.58).
