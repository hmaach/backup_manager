#!/usr/bin/env python3
import os
import tarfile
import time
from datetime import datetime

LOGS_DIR = "logs"
LOG_FILE = os.path.join(LOGS_DIR, "backup_service.log")
SCHEDULE_FILE = "backup_schedules.txt"
BACKUPS_DIR = "backups"
SLEEP_SECONDS = 45


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


def current_time_hhmm() -> str:
    return datetime.now().strftime("%H:%M")


def run_once() -> None:
    schedules = read_schedules()
    now_time = current_time_hhmm()
    for folder, time_str, backup_name in schedules:
        if time_str != now_time:
            continue
        tar_path = create_backup(folder, backup_name)
        if tar_path:
            write_log(f"Backup done for {folder} in {tar_path}")

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
    while True:
        try:
            run_once()
        except Exception:
            write_log("Error: unexpected failure in backup_service loop")
        time.sleep(SLEEP_SECONDS)
