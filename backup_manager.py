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
