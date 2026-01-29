#!/usr/bin/env python3

import os
import sys
import subprocess
from datetime import datetime

LOGS_DIR = "logs"
LOG_FILE = "logs/backup_manager.log"
SERVICE_SCRIPT = "backup_service.py"


def get_time_now():
    return datetime.now().strftime("%d/%m/%Y %H:%M")


def log_stuff(text):
    try:
        if not os.path.exists(LOGS_DIR):
            os.mkdir(LOGS_DIR)

        f = open(LOG_FILE, "a")
        f.write("[" + get_time_now() + "] " + text + "\n")
        f.close()
    except:
        pass


def service_is_running():
    try:
        ps = subprocess.run(["ps", "-A", "-f"], capture_output=True, text=True)
        if SERVICE_SCRIPT in ps.stdout:
            return True
        return False
    except:
        return False


def start_service():
    if service_is_running():
        print("Error: backup_service already running")
        log_stuff("Tried to start service but it was already running")
        return

    try:
        subprocess.Popen(
            [sys.executable, SERVICE_SCRIPT],
            start_new_session=True
        )
        print("backup_service started")
        log_stuff("backup_service started")
    except:
        print("Error: can't start backup_service")
        log_stuff("Failed to start backup_service")


def stop_service():
    if not service_is_running():
        print("Error: backup_service not running")
        log_stuff("Tried to stop service but it wasn't running")
        return

    try:
        ps = subprocess.run(["ps", "-A", "-f"], capture_output=True, text=True)

        for line in ps.stdout.split("\n"):
            if SERVICE_SCRIPT in line and "python" in line:
                parts = line.split()
                pid = int(parts[1])

                os.kill(pid, 9)

                print("backup_service stopped")
                log_stuff("backup_service stopped")
                return

        print("Error: could not find process to kill")
        log_stuff("Couldn't find backup_service process")
    except:
        print("Error: can't stop backup_service")
        log_stuff("Failed to stop backup_service")


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 backup_manager.py <command>")
        print("Commands: start, stop")
        return

    cmd = sys.argv[1]

    if cmd == "start":
        start_service()
    elif cmd == "stop":
        stop_service()
    else:
        print("Unknown command:", cmd)
        print("Try: start or stop")


main()
