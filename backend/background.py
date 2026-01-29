import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from backend.indexing import create_index, save_index
import configparser

class IndexingEventHandler(FileSystemEventHandler):
    def __init__(self, folder, provider, api_key, model_path):
        self.folder = folder
        self.provider = provider
        self.api_key = api_key
        self.model_path = model_path

    def on_modified(self, event):
        self.update_index()

    def on_created(self, event):
        self.update_index()

    def on_deleted(self, event):
        self.update_index()

    def update_index(self):
        print("Change detected, updating index...")
        res = create_index(self.folder, self.provider, self.api_key, self.model_path)
        index, docs, tags, idx_sum, clus_sum, clus_map, bm25 = res
        if index:
            save_index(index, docs, tags, 'index.faiss', idx_sum, clus_sum, clus_map, bm25)
            print("Index updated.")

def start_background_indexing():
    config = configparser.ConfigParser()
    config.read('config.ini')

    if config.has_section('General') and config.getboolean('General', 'auto_index', fallback=False):
        folder = config.get('General', 'folder')
        provider = config.get('LocalLLM', 'provider', fallback='openai')
        api_key = config.get('APIKeys', 'openai_api_key', fallback=None)
        model_path = config.get('LocalLLM', 'model_path', fallback=None)

        event_handler = IndexingEventHandler(folder, provider, api_key, model_path)
        event_handler.update_index()
        observer = Observer()
        observer.schedule(event_handler, folder, recursive=True)
        observer.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

if __name__ == "__main__":
    start_background_indexing()
