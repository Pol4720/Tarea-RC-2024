import os
import time 
import shutil 
import bluetooth 
from watchdog.observers import Observer 
from watchdog.events import FileSystemEventHandler 



class SyncHandler(FileSystemEventHandler):
    def __init__(self, target_folder, remote_device):
        self.target_folder = target_folder
        self.remote_device = remote_device

    def on_created(self, event):
        if not event.is_directory:
            print(f"Archivo creado: {event.src_path}")

        self.sync_file(event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            print(f"Archivo modificado: {event.src_path}")
    
        self.sync_file(event.src_path)

    def on_deleted(self, event):
        if not event.is_directory:
            print(f"Archivo eliminado: {event.src_path}")
    
        self.delete_file(event.src_path)
    
    def sync_file(self, file_path):
        target_file = os.path.join(self.target_folder, os.path)

