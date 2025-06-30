import os
import time
import logging

# === Configuration ===
WATCHED_DIR = "your_directory_here"
POLL_INTERVAL = 1  # seconds

ALLOWED_EXTENSIONS = {".txt", ".py", ".md"}  # Only watch these file types
EXCLUDED_DIRS = {"__pycache__", "venv", ".git"}  # Skip these subdirectories

# === Setup Logging ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# === Event Handlers ===
def on_created(path):
    logging.info(f"Created:  {path}")

def on_deleted(path):
    logging.info(f"Deleted:  {path}")

def on_modified(path):
    logging.info(f"Modified: {path}")

# === Utility Functions ===
def should_watch(path):
    ext = os.path.splitext(path)[1]
    return ext in ALLOWED_EXTENSIONS

def get_snapshot(directory):
    snapshot = {}
    for root, dirs, files in os.walk(directory):
        # Exclude certain subdirectories
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]

        for filename in files:
            path = os.path.join(root, filename)
            if should_watch(path):
                try:
                    mtime = os.path.getmtime(path)
                    snapshot[path] = mtime
                except FileNotFoundError:
                    pass  # File may have been removed during the scan
    return snapshot

# === Main Loop ===
def main():
    logging.info(f"Watching directory: {WATCHED_DIR}")
    previous_snapshot = get_snapshot(WATCHED_DIR)

    while True:
        time.sleep(POLL_INTERVAL)
        current_snapshot = get_snapshot(WATCHED_DIR)

        prev_paths = set(previous_snapshot)
        curr_paths = set(current_snapshot)

        added = curr_paths - prev_paths
        removed = prev_paths - curr_paths
        common = curr_paths & prev_paths

        for path in added:
            on_created(path)
        for path in removed:
            on_deleted(path)
        for path in common:
            if previous_snapshot[path] != current_snapshot[path]:
                on_modified(path)

        previous_snapshot = current_snapshot

if __name__ == "__main__":
    main()
