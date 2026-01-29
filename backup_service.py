#!/usr/bin/env python3
import os
from datetime import datetime

LOGS_DIR = "logs"
LOG_FILE = os.path.join(LOGS_DIR, "backup_service.log")


def now_stamp() -> str:
    return datetime.now().strftime("%d/%m/%Y %H:%M")


def write_log(message: str) -> None:
    try:
        os.makedirs(LOGS_DIR, exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as log_file:
            log_file.write(f"[{now_stamp()}] {message}\n")
    except Exception:
        # If logging itself fails, there's nowhere safe to report it.
        pass


if __name__ == "__main__":
    write_log("backup_service starting")
