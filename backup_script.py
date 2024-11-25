import os
import time
import logging
from git import Repo
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Настройка логирования
logging.basicConfig(
    filename='backup_script.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

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
            logging.info(f"Modified: {event.src_path}")
            self.commit_changes(f"Modified: {event.src_path}")

    def on_created(self, event):
        if not event.is_directory:
            logging.info(f"Created: {event.src_path}")
            self.commit_changes(f"Created: {event.src_path}")

    def on_deleted(self, event):
        if not event.is_directory:
            logging.info(f"Deleted: {event.src_path}")
            self.commit_changes(f"Deleted: {event.src_path}")

    def commit_changes(self, message):
        logging.info(f"Committing changes: {message}")
        self.repo.git.add(update=True)
        self.repo.index.commit(message)
        try:
            origin = self.repo.remote(name='origin')
            logging.info("Pushing changes to remote repository...")
            origin.push()
            logging.info("Changes pushed successfully.")
        except ValueError as e:
            logging.error(f"Error: {e}")
            logging.error("Remote 'origin' not found. Please add the remote repository.")
        except Exception as e:
            logging.error(f"Error: {e}")
            logging.error("Failed to push changes. Please check your Git configuration.")

def main():
    logging.info("Starting backup script...")
    repo = Repo(repo_path)
    if repo.bare:
        logging.error(f"{repo_path} is not a valid Git repository")
        return

    # Убедитесь, что удаленная ветка настроена
    try:
        origin = repo.remote(name='origin')
        origin.push()
    except ValueError:
        logging.warning("Remote 'origin' not found. Setting upstream branch...")
        repo.git.push('--set-upstream', 'origin', 'master')

    event_handler = ChangeHandler(repo)
    observer = Observer()
    observer.schedule(event_handler, path=directory_to_watch, recursive=True)
    observer.start()

    logging.info(f"Watching directory: {directory_to_watch}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    logging.info("Backup script stopped.")

if __name__ == "__main__":
    main()
