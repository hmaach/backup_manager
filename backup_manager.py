#!/usr/bin/env python3

import os
import sys
import subprocess
from datetime import datetime

LOGS_DIR = "logs"
LOG_FILE = "logs/backup_manager.log"
SERVICE_SCRIPT = "backup_service.py"
SCHEDULE_FILE = "backup_schedules.txt"


def get_time_now():
    return datetime.now().strftime("%d/%m/%Y %H:%M")


def write_log(text):
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
        write_log("Tried to start service but it was already running")
        return

    try:
        subprocess.Popen(
            [sys.executable, SERVICE_SCRIPT],
            start_new_session=True
        )
        print("backup_service started")
        write_log("backup_service started")
    except:
        print("Error: can't start backup_service")
        write_log("Failed to start backup_service")


def stop_service():
    if not service_is_running():
        print("Error: backup_service not running")
        write_log("Tried to stop service but it wasn't running")
        return

    try:
        ps = subprocess.run(["ps", "-A", "-f"], capture_output=True, text=True)

        for line in ps.stdout.split("\n"):
            if SERVICE_SCRIPT in line and "python" in line:
                parts = line.split()
                pid = int(parts[1])

                os.kill(pid, 9)

                print("backup_service stopped")
                write_log("backup_service stopped")
                return

        print("Error: could not find process to kill")
        write_log("Couldn't find backup_service process")
    except:
        print("Error: can't stop backup_service")
        write_log("Failed to stop backup_service")

def create_schedule(schedule):
    # schedule should look like: folder;time;name
    try:
        stuff = schedule.split(";")

        if len(stuff) != 3:
            print("Error: malformed schedule:", schedule)
            write_log("Bad schedule format: " + schedule)
            return

        folder = stuff[0].strip()
        time_str = stuff[1].strip()
        backup_name = stuff[2].strip()

        if folder == "" or time_str == "" or backup_name == "":
            print("Error: malformed schedule:", schedule)
            write_log("Empty parts in schedule: " + schedule)
            return

        f = open(SCHEDULE_FILE, "a")
        f.write(folder + ";" + time_str + ";" + backup_name + "\n")
        f.close()

        print("New schedule added:", folder + ";" + time_str + ";" + backup_name)
        write_log("Added schedule: " + folder + ";" + time_str + ";" + backup_name)

    except:
        print("Error: can't create schedule")
        write_log("Failed to create schedule")


def list_schedules():
    try:
        print("Show schedules list")
        write_log("Listing schedules")

        if not os.path.exists(SCHEDULE_FILE):
            print("Error: can't find backup_schedules.txt")
            write_log("Schedule file missing")
            return

        f = open(SCHEDULE_FILE, "r")
        lines = f.readlines()
        f.close()

        i = 0
        for line in lines:
            line = line.strip()
            if line != "":
                print(str(i) + ":", line)
            i += 1

    except:
        print("Error: can't read schedules")
        write_log("Failed to read schedules")


def delete_schedule(index_str):
    try:
        index = int(index_str)

        if not os.path.exists(SCHEDULE_FILE):
            print("Error: can't find backup_schedules.txt")
            write_log("Schedule file missing")
            return

        f = open(SCHEDULE_FILE, "r")
        lines = f.readlines()
        f.close()

        if index < 0 or index >= len(lines):
            print("Error: can't find schedule at index", index)
            write_log("Invalid schedule index: " + str(index))
            return

        # remove the line
        lines.pop(index)

        f = open(SCHEDULE_FILE, "w")
        for line in lines:
            f.write(line)
        f.close()

        print("Schedule at index", index, "deleted")
        write_log("Deleted schedule at index " + str(index))

    except ValueError:
        print("Error: invalid index", index_str)
        write_log("Invalid index: " + index_str)
    except:
        print("Error: can't delete schedule")
        write_log("Failed to delete schedule")


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 backup_manager.py <command> [arguments]")
        print("Commands:")
        print("  start              - Start backup_service.py in background")
        print("  stop               - Stop backup_service.py")
        print("  create <schedule>  - Add a new backup schedule")
        print("  list               - List all scheduled backups")
        print("  delete <index>     - Delete schedule at index")
        print("  backups            - List backup files")
        return

    command = sys.argv[1]

    if command == "start":
        start_service()
    elif command == "stop":
        stop_service()
    elif command == "create":
        if len(sys.argv) < 3:
            print("Error: missing schedule argument")
            print("Usage: python3 backup_manager.py create <schedule>")
            print("Format: folder;hh:mm;backup_name")
            return
        create_schedule(sys.argv[2])
    elif command == "list":
        list_schedules()
    elif command == "delete":
        if len(sys.argv) < 3:
            print("Error: missing index argument")
            print("Usage: python3 backup_manager.py delete <index>")
            return
        delete_schedule(sys.argv[2])
    # elif command == "backups":
    #     list_backups()
    else:
        print(f"Error: unknown command '{command}'")
        print("Available commands: start, stop, create, list, delete, backups")


if __name__ == "__main__":
    main()
