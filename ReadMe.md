# ✅ TASK 1 — backup_manager.py (the manager)

### 🎯 Goal

This script controls the backup system.

It:

* adds schedules
* shows schedules
* deletes schedules
* starts the service
* stops the service
* shows backup files

It also writes logs in:

```
./logs/backup_manager.log
```

Every action must use `try / except`.

---

## 1) Logging rule

Every action must be written in the log file.

Example:

```
[29/01/2026 16:07] New schedule added: test;16:07;backup_test
[29/01/2026 16:07] Error: malformed schedule: test;
```

---

## 2) Commands

You run the script like this:

```
python3 backup_manager.py <command> [argument]
```

---

### ▶️ start

Start backup_service.py in background.

Logs:

* backup_service started
* Error: can't start backup_service
* Error: backup_service already running

---

### ⏹️ stop

Stop backup_service.py.

Logs:

* backup_service stopped
* Error: can't stop backup_service
* Error: backup_service not running

---

### ➕ create "schedule"

Add a schedule to `backup_schedules.txt`.

Format:

```
folder;hh:mm;backup_name
```

Example:

```
test;16:07;backup_test
```

Logs:

* New schedule added: ...
* Error: malformed schedule: ...

---

### 📋 list

Show all schedules with index.

Example output:

```
0: test;16:07;backup_test
1: test1;16:07;personal_data
```

Logs:

* Show schedules list
* Error: can't find backup_schedules.txt

---

### ❌ delete index

Delete schedule at index.

Example:

```
python3 backup_manager.py delete 1
```

Logs:

* Schedule at index 1 deleted
* Error: can't find schedule at index 1
* Error: can't find backup_schedules.txt

---

### 📦 backups

Show files in `./backups`.

Logs:

* Show backups list
* Error: can't find backups directory

---

# ✅ TASK 2 — backup_service.py (the service)

### 🎯 Goal

This script runs forever and makes backups at the right time.

It writes logs in:

```
./logs/backup_service.log
```

---

## 1) How it works (loop)

The service does this again and again:

1. Read `backup_schedules.txt`
2. For each schedule:

   * folder;time;backup_name
3. Get current time (hh:mm)
4. If current time == schedule time:

   * create a .tar backup of the folder
   * save it in ./backups
   * write log
5. Sleep 45 seconds
6. Repeat forever

---

## 2) Backup example

Schedule:

```
test;16:07;backup_test
```

Result:

```
./backups/backup_test.tar
```

Log:

```
[29/01/2026 16:07] Backup done for test in backups/backup_test.tar
```

---

## 3) Error handling

Use try / except for everything.

Examples:

* schedule file not found
* folder not found
* tar error

Log example:

```
[29/01/2026 16:07] Error: can't read backup_schedules.txt
```

---

# 🧠 Simple idea

* backup_manager.py = controller 🎮
* backup_service.py = worker 🤖
* backup_schedules.txt = plan 📅
* backups/ = results 📦
* logs/ = history 📝
