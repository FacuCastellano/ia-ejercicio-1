import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from utils.chunker import chunk_file
from utils.database import delete_chunks_by_filename


# --- INICIO DE LA CONFIGURACIÓN ---
# Directorio a monitorear
WATCH_DIRECTORY = "collections"
# --- FIN DE LA CONFIGURACIÓN ---

class ChangeHandler(FileSystemEventHandler):
    """
    Clase que maneja los eventos del sistema de archivos.
    Hereda de FileSystemEventHandler para poder sobreescribir los métodos
    que detectan los cambios.
    """

    def on_created(self, event):
        """Se llama cuando un archivo o directorio es creado."""
        if not event.is_directory:
            print(f"✅ [CREADO] Archivo detectado: {event.src_path}")
            chunk_file(file_path=event.src_path, chunk_size_kb= 100)
    def on_modified(self, event):
        """Se llama cuando un archivo o directorio es modificado."""
        if not event.is_directory:
            print(f"🔄 [MODIFICADO] Archivo detectado: {event.src_path}")
            chunk_file(file_path=event.src_path, chunk_size_kb= 100)
    def on_deleted(self, event):
        """Se llama cuando un archivo o directorio es eliminado."""
        if not event.is_directory:
            file_name = os.path.basename(event.src_path)
            delete_chunks_by_filename(file_name=file_name)
            print(f"❌ [ELIMINADO] Archivo detectado: {file_name}")

def start_monitoring(path):
    """
    Inicia el monitoreo del directorio especificado.
    """
    # Asegurarse de que el directorio a vigilar exista
    if not os.path.isdir(path):
        print(f"Error: El directorio '{path}' no existe. Creándolo...")
        os.makedirs(path)
        print(f"Directorio '{path}' creado.")

    event_handler = ChangeHandler()
    observer = Observer()
    # "schedule" configura el observador.
    # event_handler: El objeto que manejará los eventos.
    # path: El directorio a observar.
    # recursive=True: También observa subdirectorios.
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