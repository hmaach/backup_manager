#!/usr/bin/env python3
import os
import tarfile
from datetime import datetime

LOGS_DIR = "logs"
LOG_FILE = os.path.join(LOGS_DIR, "backup_service.log")
SCHEDULE_FILE = "backup_schedules.txt"
BACKUPS_DIR = "backups"


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


def read_schedules() -> list[tuple[str, str, str]]:
    schedules: list[tuple[str, str, str]] = []
    try:
        with open(SCHEDULE_FILE, "r", encoding="utf-8") as schedule_file:
            for raw_line in schedule_file:
                line = raw_line.strip()
                if not line:
                    continue
                parts = line.split(";")
                if len(parts) != 3:
                    write_log(f"Error: malformed schedule: {line}")
                    continue
                folder, time_str, backup_name = [p.strip() for p in parts]
                schedules.append((folder, time_str, backup_name))
    except Exception:
        write_log("Error: can't read backup_schedules.txt")
    return schedules


def create_backup(folder: str, backup_name: str) -> str | None:
    if not os.path.isdir(folder):
        write_log(f"Error: can't find folder {folder}")
        return None

    try:
        os.makedirs(BACKUPS_DIR, exist_ok=True)
        tar_path = os.path.join(BACKUPS_DIR, f"{backup_name}.tar")
        with tarfile.open(tar_path, "w") as tar:
            tar.add(folder, arcname=os.path.basename(folder))
        return tar_path
    except Exception:
        write_log(f"Error: tar failed for {folder}")
        return None


if __name__ == "__main__":
    write_log("backup_service starting")
