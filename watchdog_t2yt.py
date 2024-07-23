from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
import time
import subprocess

class ChangeHandler(FileSystemEventHandler):
    def __init__(self, script_path, env_path):
        self.script_path = script_path
        self.env_path = env_path

    def on_modified(self, event):
        if event.src_path in [self.script_path, self.env_path]:
            print(f"Change detected in {event.src_path}. Restarting server...")
            subprocess.run(["sudo", "supervisorctl", "restart", "flask_app"])

if __name__ == "__main__":
    script_path = "/home/t2ytuser/automation/python/t2yt/t2yt.py"
    env_path = "/home/t2ytuser/automation/python/t2yt/.env"
    event_handler = ChangeHandler(script_path, env_path)
    observer = Observer()
    observer.schedule(event_handler, path=os.path.dirname(script_path), recursive=False)
    observer.schedule(event_handler, path=os.path.dirname(env_path), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
