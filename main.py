import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from utils.chunker import chunk_file
from utils.database import delete_chunks_by_filename

WATCH_DIRECTORY = "collections"

class ChangeHandler(FileSystemEventHandler):
    def on_created(self, event):  
        if not event.is_directory:
            print(f"✅ [CREADO] Archivo detectado: {event.src_path}")
            chunk_file(file_path=event.src_path, chunk_size_kb= 100)
    def on_modified(self, event):
        if not event.is_directory:
            print(f"🔄 [MODIFICADO] Archivo detectado: {event.src_path}")
            chunk_file(file_path=event.src_path, chunk_size_kb= 100)
    def on_deleted(self, event):   
        if not event.is_directory:
            file_name = os.path.basename(event.src_path)
            delete_chunks_by_filename(file_name=file_name)
            print(f"❌ [ELIMINADO] Archivo detectado: {file_name}")

def start_monitoring(path):

    if not os.path.isdir(path):
        print(f"Error: El directorio '{path}' no existe. Creándolo...")
        os.makedirs(path)
        print(f"Directorio '{path}' creado.")

    event_handler = ChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    print(f"🚀 Iniciando monitoreo en el directorio: '{path}'")
    print("Presiona Ctrl+C para detener el script.")
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("🛑 Deteniendo el monitoreo...")
        observer.stop()
    observer.join()
    print("👋 Monitoreo finalizado.")

if __name__ == "__main__":
    start_monitoring(WATCH_DIRECTORY)