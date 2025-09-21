import os
from pypdf import PdfReader 
from .database import save_chunk_to_db 


def chunk_file(file_path: str, chunk_size_kb: int):
       
    if not os.path.isfile(file_path):
        print(f"❌ Error: El archivo '{file_path}' no fue encontrado.")
        return []

    if chunk_size_kb <= 0:
        print("❌ Error: El tamaño del chunk debe ser mayor que cero.")
        return []

 
    chunk_size_bytes = chunk_size_kb * 1024
    directory, filename = os.path.split(file_path)
    base_name, extension = os.path.splitext(filename)
    created_files = []
    chunk_counter = 0

    print(f"🚀 Empezando a chunckear el archivo: '{filename}' en chunks de {chunk_size_kb} KB...")

    try:
       
        if extension.lower() == '.pdf':
            print("📄 Archivo PDF detectado. Extrayendo texto legible...")
            try:
                reader = PdfReader(file_path)
                full_text = ""
                for page in reader.pages:
                   
                    page_text = page.extract_text()
                    if page_text:
                        full_text += page_text
                
                
                for i in range(0, len(full_text), chunk_size_bytes):
                    chunk_text = full_text[i:i + chunk_size_bytes]
                    chunk_counter += 1
                    print(f"  -> Guardando chunk {chunk_counter} de '{filename}'...")
                    save_chunk_to_db(filename, chunk_counter, chunk_text)
                    
                 
                    

            except Exception as e:
                print(f"❌ Error al procesar el archivo PDF: {e}")
                return []
        
        else: 
            print("📝 Archivo de texto detectado. Procediendo con la lectura de bytes...")
            with open(file_path, 'rb') as source_file:
                while True:
                    chunk_data = source_file.read(chunk_size_bytes)
                    if not chunk_data:
                        break
                    
           
                    chunk_text = chunk_data.decode('utf-8', errors='ignore')
                    chunk_counter += 1
                    print(f"  -> Guardando chunk {chunk_counter} de '{filename}'...")
                    save_chunk_to_db(filename, chunk_counter, chunk_text)

                    
        
        
        print(f"\n🎉 Proceso completado. Se procesaron {chunk_counter} chunks.")
   
        return []

    except Exception as e:
        print(f"❌ Ocurrió un error inesperado: {e}")
        return []