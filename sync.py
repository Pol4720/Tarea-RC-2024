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
        """Sincroniza un archivo nuevo o modificado."""
        target_file = os.path.join(self.target_folder, os.path.basename(file_path))
        shutil.copy2(file_path, target_file)
        print(f"Sincronizando archivo: {file_path} a {target_file}")
        self.send_file_via_bluetooth(target_file)

    def delete_file(self, file_path):
        """Elimina un archivo en la carpeta de destino."""
        target_file = os.path.join(self.target_folder, os.path.basename(file_path))
        if os.path.exists(target_file):
            os.remove(target_file)
            print(f"Archivo eliminado en destino: {target_file}")

    def send_file_via_bluetooth(self, file_path):
        """Envía un archivo a través de Bluetooth."""
        try:
            with open(file_path, "rb") as file:
                data = file.read()
                sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
                sock.connect((self.remote_device, 1))  # El canal puede ser diferente
                sock.send(data)
                sock.close()
                print(f"Archivo enviado: {file_path} a {self.remote_device}")
        except Exception as e:
            print(f"Error al enviar el archivo: {e}")

def monitor_folder(folder_to_monitor, target_folder, remote_device):
    event_handler = SyncHandler(target_folder, remote_device)
    observer = Observer()
    observer.schedule(event_handler, folder_to_monitor, recursive=True)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    folder_to_monitor = input("Ingrese la ruta de la carpeta a monitorear: ")
    target_folder = input("Ingrese la ruta de la carpeta de destino: ")
    remote_device = input("Ingrese la dirección MAC del dispositivo remoto: ")

    monitor_folder(folder_to_monitor, target_folder, remote_device)


