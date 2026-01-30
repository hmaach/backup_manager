import os
import sys
import subprocess
from datetime import datetime

LOGS_DIR = "logs"
LOG_FILE = LOGS_DIR + "/backup_manager.log"
SERVICE_SCRIPT = "backup_service.py"
SCHEDULE_FILE = "backup_schedules.txt"
BACKUPS_DIR = "backups"


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
        print("Error: can't log into log file")
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
        write_log("Error: service already running")
        return

    try:
        subprocess.Popen([sys.executable, SERVICE_SCRIPT], start_new_session=True)
        write_log("backup_service started")
    except:
        write_log("Failed to start backup_service")


def stop_service():
    if not service_is_running():
        write_log("Error: can't stop backup_service")
        return

    try:
        ps = subprocess.run(["ps", "-A", "-f"], capture_output=True, text=True)

        for line in ps.stdout.split("\n"):
            if SERVICE_SCRIPT in line and "python" in line:
                parts = line.split()
                pid = int(parts[1])

                os.kill(pid, 9)

                write_log("backup_service stopped")
                return

        write_log("Couldn't find backup_service process")
    except:
        write_log("Failed to stop backup_service")


def create_schedule(schedule):
    try:
        stuff = schedule.split(";")

        if len(stuff) != 3:
            write_log("Bad schedule format: " + schedule)
            return

        folder = stuff[0].strip()
        time_str = stuff[1].strip()
        backup_name = stuff[2].strip()

        if folder == "" or time_str == "" or backup_name == "":
            write_log("Empty parts in schedule: " + schedule)
            return

        try:
            schedule_time = datetime.strptime(time_str, "%H:%M").time()
        except ValueError:
            print("Invalid time format: " + time_str)
            write_log("Invalid time format: " + time_str)
            return

        # current_time = datetime.now().time()

        # if schedule_time < current_time:
        #     write_log("Skipped schedule (time passed)")
        #     return

        f = open(SCHEDULE_FILE, "a")
        f.write(folder + ";" + time_str + ";" + backup_name + "\n")
        f.close()

        write_log("Added schedule: " + folder + ";" + time_str + ";" + backup_name)

    except:
        write_log("Failed to create schedule")


def list_schedules():
    try:
        write_log("Listing schedules")

        if not os.path.exists(SCHEDULE_FILE):
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
        write_log("Failed to read schedules")


def delete_schedule(index_str):
    try:
        index = int(index_str)

        if not os.path.exists(SCHEDULE_FILE):
            write_log("Schedule file missing")
            return

        f = open(SCHEDULE_FILE, "r")
        lines = f.readlines()
        f.close()

        if index < 0 or index >= len(lines):
            print("Invalid schedule index: " + str(index))
            return

        # remove the line
        lines.pop(index)

        f = open(SCHEDULE_FILE, "w")
        for line in lines:
            f.write(line)
        f.close()

        write_log("Deleted schedule at index " + str(index))

    except ValueError:
        write_log("Invalid index: " + index_str)
    except:
        write_log("Failed to delete schedule")


def list_backups():
    try:
        write_log("Show backups list")

        if not os.path.exists(BACKUPS_DIR):
            write_log("Backups directory does not exist")
            return

        if os.path.isdir(BACKUPS_DIR) == False:
            write_log("Backups path is not a directory")
            return

        files = os.listdir(BACKUPS_DIR)
        backups = []

        for name in files:
            if name.endswith(".tar"):
                backups.append(name)

        backups.sort()

        for b in backups:
            print(b)

    except:
        write_log("Failed to list backups")


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
    elif command == "backups":
        list_backups()
    else:
        print(f"Error: unknown command '{command}'")
        print("Available commands: start, stop, create, list, delete, backups")


if __name__ == "__main__":
    main()
