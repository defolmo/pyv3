import os
import time
from git import Repo
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Путь к директории, которую нужно отслеживать
directory_to_watch = os.path.join(os.path.dirname(__file__), 'new_important_files')

# Путь к локальному Git репозиторию
repo_path = os.path.dirname(__file__)

# URL удаленного репозитория на GitHub
remote_url = "https://github.com/defolmo/pyv3.git"

class ChangeHandler(FileSystemEventHandler):
    def __init__(self, repo):
        self.repo = repo

    def on_modified(self, event):
        if not event.is_directory:
            print(f"Modified: {event.src_path}")
            self.commit_changes(f"Modified: {event.src_path}")

    def on_created(self, event):
        if not event.is_directory:
            print(f"Created: {event.src_path}")
            self.commit_changes(f"Created: {event.src_path}")

    def on_deleted(self, event):
        if not event.is_directory:
            print(f"Deleted: {event.src_path}")
            self.commit_changes(f"Deleted: {event.src_path}")

    def commit_changes(self, message):
        print(f"Committing changes: {message}")
        self.repo.git.add(update=True)
        self.repo.index.commit(message)
        try:
            origin = self.repo.remote(name='origin')
            print("Pushing changes to remote repository...")
            origin.push()
            print("Changes pushed successfully.")
        except ValueError as e:
            print(f"Error: {e}")
            print("Remote 'origin' not found. Please add the remote repository.")
        except Exception as e:
            print(f"Error: {e}")
            print("Failed to push changes. Please check your Git configuration.")

def main():
    print("Starting backup script...")
    repo = Repo(repo_path)
    if repo.bare:
        print(f"{repo_path} is not a valid Git repository")
        return

    # Убедитесь, что удаленная ветка настроена
    try:
        origin = repo.remote(name='origin')
        origin.push()
    except ValueError:
        print("Remote 'origin' not found. Setting upstream branch...")
        repo.git.push('--set-upstream', 'origin', 'master')

    event_handler = ChangeHandler(repo)
    observer = Observer()
    observer.schedule(event_handler, path=directory_to_watch, recursive=True)
    observer.start()

    print(f"Watching directory: {directory_to_watch}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    print("Backup script stopped.")

if __name__ == "__main__":
    main()
