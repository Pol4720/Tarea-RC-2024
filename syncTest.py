import os
import time
import shutil
import asyncio
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from bleak import BleakClient, BleakScanner

class SyncHandler(FileSystemEventHandler):
    def __init__(self, target_folder, remote_device_name):
        self.target_folder = target_folder
        self.remote_device_name = remote_device_name
        self.client = None

    def on_created(self, event):
        if event.is_directory:
            print(f"Carpeta creada: {event.src_path}")
            asyncio.run(self.sync_folder(event.src_path))
        else:
            print(f"Archivo creado: {event.src_path}")
            asyncio.run(self.sync_file(event.src_path))

    def on_modified(self, event):
        if event.is_directory:
            print(f"Carpeta modificada: {event.src_path}")
            asyncio.run(self.sync_folder(event.src_path))
        else:
            print(f"Archivo modificado: {event.src_path}")
            asyncio.run(self.sync_file(event.src_path))

    def on_deleted(self, event):
        if event.is_directory:
            print(f"Carpeta eliminada: {event.src_path}")
            self.delete_folder(event.src_path)
        else:
            print(f"Archivo eliminado: {event.src_path}")
            self.delete_file(event.src_path)

    def delete_file(self, file_path):
        """Elimina un archivo en la carpeta de destino."""
        target_file = os.path.join(self.target_folder, os.path.basename(file_path))
        if os.path.exists(target_file):
            os.remove(target_file)
            print(f"Archivo eliminado en destino: {target_file}")

    def delete_folder(self, folder_path):
        """Elimina una carpeta en la carpeta de destino."""
        target_folder = os.path.join(self.target_folder, os.path.basename(folder_path))
        if os.path.exists(target_folder):
            shutil.rmtree(target_folder)
            print(f"Carpeta eliminada en destino: {target_folder}")

    async def sync_file(self, file_path):
        """Sincroniza un archivo nuevo o modificado."""
        target_file = os.path.join(self.target_folder, os.path.basename(file_path))
        shutil.copy2(file_path, target_file)
        print(f"Sincronizando archivo: {file_path} a {target_file}")
        await self.send_file_via_bluetooth(target_file)

    async def sync_folder(self, folder_path):
        """Sincroniza una carpeta nueva o modificada."""
        target_folder = os.path.join(self.target_folder, os.path.basename(folder_path))
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                target_file_path = os.path.join(target_folder, os.path.relpath(file_path, folder_path))
                target_file_dir = os.path.dirname(target_file_path)
                if not os.path.exists(target_file_dir):
                    os.makedirs(target_file_dir)
                shutil.copy2(file_path, target_file_path)
                print(f"Sincronizando archivo: {file_path} a {target_file_path}")
                await self.send_file_via_bluetooth(target_file_path)

    async def send_file_via_bluetooth(self, file_path):
        """Envía un archivo a través de Bluetooth."""
        try:
            device = await BleakScanner.find_device_by_filter(lambda d, ad: d.name == self.remote_device_name)
            if not device:
                print(f"Dispositivo {self.remote_device_name} no encontrado.")
                return

            async with BleakClient(device) as client:
                self.client = client
                with open(file_path, "rb") as file:
                    data = file.read()
                    chunk_size = 512
                    for i in range(0, len(data), chunk_size):
                        chunk = data[i:i + chunk_size]
                        await client.write_gatt_char("characteristic-uuid", chunk)
                print(f"Archivo enviado: {file_path}")
        except Exception as e:
            print(f"Error al enviar el archivo: {e}")

def monitor_folder(folder_to_monitor, target_folder, remote_device_name):
    event_handler = SyncHandler(target_folder, remote_device_name)
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
    remote_device_name = input("Ingrese el nombre del dispositivo Bluetooth: ")

    monitor_folder(folder_to_monitor, target_folder, remote_device_name)