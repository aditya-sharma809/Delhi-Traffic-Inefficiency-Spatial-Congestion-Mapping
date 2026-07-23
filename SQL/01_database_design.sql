-- =============================================================================
-- DELHI TRAFFIC ANALYTICS - PRODUCTION DATABASE DESIGN
-- Author: Aditya Sharma
-- Engine: MySQL 8.0+
-- =============================================================================

CREATE DATABASE IF NOT EXISTS delhi_traffic_db;
USE delhi_traffic_db;

-- Drop existing tables for clean deployment
DROP TABLE IF EXISTS fact_traffic_monitoring;
DROP TABLE IF EXISTS dim_date;
DROP TABLE IF EXISTS dim_time_window;

-- -----------------------------------------------------------------------------
-- 1. DIMENSION TABLE: DIM_DATE
-- -----------------------------------------------------------------------------
CREATE TABLE dim_date (
    Date_ID INT AUTO_INCREMENT PRIMARY KEY,
    Day_Of_Month INT NOT NULL CHECK (Day_Of_Month BETWEEN 1 AND 31),
    Day_Of_Week VARCHAR(15) NOT NULL,
    Is_Weekend TINYINT(1) NOT NULL DEFAULT 0,
    CONSTRAINT chk_day_of_week CHECK (Day_Of_Week IN ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------------------------------
-- 2. DIMENSION TABLE: DIM_TIME_WINDOW
-- -----------------------------------------------------------------------------
CREATE TABLE dim_time_window (
    Time_ID INT AUTO_INCREMENT PRIMARY KEY,
    Time_12Hr VARCHAR(15) NOT NULL,
    Time_24Hr TIME NOT NULL,
    Hour INT NOT NULL CHECK (Hour BETWEEN 0 AND 23),
    Is_Peak_Hour TINYINT(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------------------------------
-- 3. FACT TABLE: FACT_TRAFFIC_MONITORING
-- -----------------------------------------------------------------------------
CREATE TABLE fact_traffic_monitoring (
    Traffic_ID BIGINT AUTO_INCREMENT PRIMARY KEY,
    Date_ID INT NOT NULL,
    Time_ID INT NOT NULL,
    
    -- Vehicle Counts with Constraints
    Car_Count INT NOT NULL DEFAULT 0 CHECK (Car_Count >= 0),
    Bike_Count INT NOT NULL DEFAULT 0 CHECK (Bike_Count >= 0),
    Bus_Count INT NOT NULL DEFAULT 0 CHECK (Bus_Count >= 0),
    Truck_Count INT NOT NULL DEFAULT 0 CHECK (Truck_Count >= 0),
    Total_Vehicles INT NOT NULL CHECK (Total_Vehicles >= 0),
    
    -- Engineered Analytics Metrics
    PCU_Score DECIMAL(10,2) NOT NULL CHECK (PCU_Score >= 0),
    Heavy_Vehicle_Ratio DECIMAL(5,4) NOT NULL CHECK (Heavy_Vehicle_Ratio BETWEEN 0 AND 1),
    Car_Ratio DECIMAL(5,4) NOT NULL CHECK (Car_Ratio BETWEEN 0 AND 1),
    Traffic_Situation ENUM('low', 'normal', 'high', 'heavy') NOT NULL,
    
    -- Foreign Key Relationships
    CONSTRAINT fk_traffic_date FOREIGN KEY (Date_ID) REFERENCES dim_date(Date_ID) ON DELETE CASCADE,
    CONSTRAINT fk_traffic_time FOREIGN KEY (Time_ID) REFERENCES dim_time_window(Time_ID) ON DELETE CASCADE,
    
    -- Business Logic Check Constraint
    CONSTRAINT chk_vehicle_sum CHECK (Total_Vehicles = (Car_Count + Bike_Count + Bus_Count + Truck_Count))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------------------------------
-- 4. PERFORMANCE INDEXES (FAST ANALYTICS & DASHBOARD QUERYING)
-- -----------------------------------------------------------------------------
-- Index on Frequently Queried Dimensions
CREATE INDEX idx_traffic_situation ON fact_traffic_monitoring(Traffic_Situation);
CREATE INDEX idx_pcu_score ON fact_traffic_monitoring(PCU_Score);

-- Composite Index for Peak Hour & Date filtering
CREATE INDEX idx_date_time_composite ON fact_traffic_monitoring(Date_ID, Time_ID);