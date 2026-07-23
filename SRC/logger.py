import os
import logging

def setup_logger(log_filename="etl_pipeline.log"):
    """
    Configures a dual-handler enterprise logging system:
    - FileHandler: Saves detailed logs to logs/etl_pipeline.log
    - StreamHandler: Displays formatted logs on the VS Code Terminal
    """
    # 1. Resolve Project Root and Logs Directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    logs_dir = os.path.join(project_root, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    
    log_filepath = os.path.join(logs_dir, log_filename)

    # 2. Create Custom Logger instance
    logger = logging.getLogger("Traffic_Analytics_Logger")
    logger.setLevel(logging.INFO)

    # Avoid adding duplicate handlers if logger is already initialized
    if not logger.handlers:
        # Formatter: [TIMESTAMP] [LEVEL] [MODULE] - MESSAGE
        formatter = logging.Formatter(
            fmt="[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # File Handler (Writes to disk)
        file_handler = logging.FileHandler(log_filepath, mode='a', encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)

        # Terminal Stream Handler (Console output)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)

        # Attach handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger

# Instant testing when executed directly
if __name__ == "__main__":
    logger = setup_logger()
    logger.info("🟢 Logger Module Initialized Successfully!")
    logger.warning("⚠️ Testing Logger Warning Alert.")
    logger.error("🔴 Testing Logger Error Alert.")