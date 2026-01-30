import os
import sys
import subprocess
from datetime import datetime

LOGS_DIR = "logs"
LOG_FILE = LOGS_DIR + "/backup_manager.log"
SERVICE_LOG_FILE = LOGS_DIR + "/backup_service.log"
SERVICE_SCRIPT = "backup_service.py"
SCHEDULE_FILE = "backup_schedules.txt"
BACKUPS_DIR = "backups"
PID_FILE = LOGS_DIR + "/backup_service.pid"


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


def write_service_log(text):
    try:
        if not os.path.exists(LOGS_DIR):
            os.mkdir(LOGS_DIR)
        f = open(SERVICE_LOG_FILE, "a")
        f.write("[" + get_time_now() + "] " + text + "\n")
        f.close()
    except:
        pass


def _read_pid_file():
    try:
        if not os.path.exists(PID_FILE):
            return None
        with open(PID_FILE, "r") as f:
            raw = f.read().strip()
        if raw == "":
            return None
        return int(raw)
    except:
        return None


def _pid_is_running(pid):
    try:
        os.kill(pid, 0)
    except:
        return False
    return True


def _service_pids():
    pids = []
    pid = _read_pid_file()
    if pid is not None:
        if _pid_is_running(pid):
            pids.append(pid)
        else:
            try:
                os.remove(PID_FILE)
            except:
                pass
    # de-dup while preserving order
    uniq = []
    for pid in pids:
        if pid not in uniq:
            uniq.append(pid)
    return uniq


def service_is_running():
    return len(_service_pids()) > 0


def start_service():
    if service_is_running():
        print("Error: backup_service already running", flush=True)
        write_log("Error: backup_service already running")
        return

    try:
        if not os.path.exists(LOGS_DIR):
            os.mkdir(LOGS_DIR)
        proc = subprocess.Popen([sys.executable, SERVICE_SCRIPT], start_new_session=True)
        try:
            with open(PID_FILE, "w") as f:
                f.write(str(proc.pid))
        except:
            pass
        print("backup_service started", flush=True)
        write_log("backup_service started")
    except:
        print("Error: can't start backup_service", flush=True)
        write_log("Failed to start backup_service")


def stop_service():
    try:
        pids = _service_pids()
        if not pids:
            print("Error: backup_service not running", flush=True)
            write_log("Error: backup_service not running")
            return
        for pid in pids:
            os.kill(pid, 9)
        try:
            os.remove(PID_FILE)
        except:
            pass
        print("backup_service stopped", flush=True)
        write_log("backup_service stopped")
    except:
        print("Error: can't stop backup_service", flush=True)
        write_log("Failed to stop backup_service")


def create_schedule(schedule):
    try:
        stuff = schedule.split(";")

        if len(stuff) != 3:
            print("Error: malformed schedule:", schedule)
            write_log("Error: malformed schedule: " + schedule)
            return

        folder = stuff[0].strip()
        time_str = stuff[1].strip()
        backup_name = stuff[2].strip()

        if folder == "" or time_str == "" or backup_name == "":
            print("Error: malformed schedule:", schedule)
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

        print("New schedule added:", folder + ";" + time_str + ";" + backup_name)
        write_log("New schedule added: " + folder + ";" + time_str + ";" + backup_name)

    except:
        print("Error: can't create schedule")
        write_log("Failed to create schedule")


def list_schedules():
    try:
        print("Show schedules list")
        write_log("Show schedules list")

        if not os.path.exists(SCHEDULE_FILE):
            print("Error: can't find backup_schedules.txt")
            write_log("Error: can't find backup_schedules.txt")
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
            write_log("Error: can't find backup_schedules.txt")
            return

        f = open(SCHEDULE_FILE, "r")
        lines = f.readlines()
        f.close()

        if index < 0 or index >= len(lines):
            print("Error: can't find schedule at index " + str(index))
            write_log("Error: can't find schedule at index " + str(index))
            return

        # remove the line
        lines.pop(index)

        f = open(SCHEDULE_FILE, "w")
        for line in lines:
            f.write(line)
        f.close()

        write_log("Schedule at index " + str(index) + " deleted")

    except ValueError:
        print("Error: can't find schedule at index " + index_str)
        write_log("Error: can't find schedule at index " + index_str)
    except:
        write_log("Failed to delete schedule")


def list_backups():
    try:
        print("Show backups list")
        write_log("Show backups list")

        if not os.path.exists(BACKUPS_DIR):
            print("Error: can't find backups directory")
            write_log("Error: can't find backups directory")
            return

        if os.path.isdir(BACKUPS_DIR) == False:
            print("Error: backups is not a directory")
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
        print("Error: can't list backups")
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
        write_log("Error: unknown command")
        write_service_log("Error: unknown instruction")


if __name__ == "__main__":
    main()
