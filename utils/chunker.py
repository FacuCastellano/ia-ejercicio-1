import os
from pypdf import PdfReader # ### CAMBIO ###: Importar la librería necesaria
from .database import save_chunk_to_db # ### NUEVO ###


def chunk_file(file_path: str, chunk_size_kb: int):
    """
    Divide un archivo en múltiples chunks de un tamaño específico.
    Si es un PDF, extrae el texto y lo divide. Si es texto, divide los bytes.

    Args:
        file_path (str): La ruta al archivo que se va a dividir.
        chunk_size_kb (int): El tamaño máximo de cada chunk en kilobytes (KB).

    Returns:
        list: Una lista con las rutas de los archivos chunk creados.
              Retorna una lista vacía si ocurre un error.
    """
    # --- 1. Validación de entradas (SIN CAMBIOS) ---
    if not os.path.isfile(file_path):
        print(f"❌ Error: El archivo '{file_path}' no fue encontrado.")
        return []

    if chunk_size_kb <= 0:
        print("❌ Error: El tamaño del chunk debe ser mayor que cero.")
        return []

    # --- 2. Preparación de variables (SIN CAMBIOS) ---
    chunk_size_bytes = chunk_size_kb * 1024
    directory, filename = os.path.split(file_path)
    base_name, extension = os.path.splitext(filename)
    created_files = []
    chunk_counter = 0

    print(f"🚀 Empezando a chunckear el archivo: '{filename}' en chunks de {chunk_size_kb} KB...")

    try:
        # --- 3. Lógica de división del archivo (CON CAMBIOS) ---

        # ### CAMBIO ###: Añadimos un IF para tratar los PDFs de forma diferente
        if extension.lower() == '.pdf':
            print("📄 Archivo PDF detectado. Extrayendo texto legible...")
            try:
                reader = PdfReader(file_path)
                full_text = ""
                for page in reader.pages:
                    # Extraemos texto de cada página y lo juntamos
                    page_text = page.extract_text()
                    if page_text:
                        full_text += page_text
                
                # Ahora dividimos el TEXTO EXTRAÍDO en chunks.
                # Usamos chunk_size_bytes como el número de CARACTERES por chunk.
                for i in range(0, len(full_text), chunk_size_bytes):
                    chunk_text = full_text[i:i + chunk_size_bytes]
                    chunk_counter += 1
                    print(f"  -> Guardando chunk {chunk_counter} de '{filename}'...")
                    save_chunk_to_db(filename, chunk_counter, chunk_text)
                    
                    # (Opcional) Aquí podrías guardar este chunk_text en un archivo .txt si quisieras
                    

            except Exception as e:
                print(f"❌ Error al procesar el archivo PDF: {e}")
                return []
        
        else: # ### CAMBIO ###: Esta es tu lógica original para TXT, CSV, etc.
            print("📝 Archivo de texto detectado. Procediendo con la lectura de bytes...")
            with open(file_path, 'rb') as source_file:
                while True:
                    chunk_data = source_file.read(chunk_size_bytes)
                    if not chunk_data:
                        break
                    
                    # Decodificamos el chunk de bytes para imprimirlo como texto
                    chunk_text = chunk_data.decode('utf-8', errors='ignore')
                    chunk_counter += 1
                    print(f"  -> Guardando chunk {chunk_counter} de '{filename}'...")
                    save_chunk_to_db(filename, chunk_counter, chunk_text)

                    
        
        # ### CAMBIO ###: Corregimos el retorno para que sea consistente
        print(f"\n🎉 Proceso completado. Se procesaron {chunk_counter} chunks.")
        # La función original creaba archivos, ahora solo imprime. Retornamos una lista vacía.
        # Si reactivaras la creación de archivos, aquí retornarías 'created_files'
        return []

    except Exception as e:
        print(f"❌ Ocurrió un error inesperado: {e}")
        return []