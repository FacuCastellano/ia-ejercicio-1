import psycopg2
import os
from dotenv import load_dotenv

# --- INICIO DE LA CONFIGURACIÓN DE LA BASE DE DATOS ---
# Cargar variables desde .env
load_dotenv()

# --- INICIO DE LA CONFIGURACIÓN DE LA BASE DE DATOS ---
DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
# --- FIN DE LA CONFIGURACIÓN DE LA BASE DE DATOS ---
print({
'dbname':DB_NAME,
'user':DB_USER,
'password':DB_PASSWORD,
'host':DB_HOST,
'port':DB_PORT
})
def get_db_connection():
    """
    Establece y devuelve una conexión a la base de datos PostgreSQL.
    """
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        print(" Conexion con la base de datos establecida")
        return conn
    except psycopg2.OperationalError as e:
        print(f"❌ Error al conectar con la base de datos: {e}")
        return None

def setup_database():
    """
    Asegura que la extensión pgvector esté habilitada y que la tabla de documentos exista.
    """
    conn = get_db_connection()
    if not conn:
        return

    try:
        with conn.cursor() as cur:
            # Habilitar la extensión pgvector si no está habilitada
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            
            # Crear la tabla para almacenar los chunks si no existe
            cur.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id SERIAL PRIMARY KEY,
                file_name VARCHAR(255) NOT NULL,
                chunk_index INTEGER NOT NULL,
                content TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(file_name, chunk_index)
            );
            """)
            conn.commit()
            print("✅ Base de datos configurada correctamente (extensión 'vector' y tabla 'documents' listas).")
    except psycopg2.Error as e:
        print(f"❌ Error durante la configuración de la base de datos: {e}")
    finally:
        if conn:
            conn.close()

def save_chunk_to_db(file_name, chunk_index, chunk_content):
    """
    Guarda un único chunk de texto en la base de datos.
    Utiliza ON CONFLICT para actualizar el contenido si el chunk ya existe.
    """
    conn = get_db_connection()
    if not conn:
        return

    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO documents (file_name, chunk_index, content)
                VALUES (%s, %s, %s)
                ON CONFLICT (file_name, chunk_index) DO UPDATE
                SET content = EXCLUDED.content;
            """, (file_name, chunk_index, chunk_content))
            conn.commit()
    except psycopg2.Error as e:
        print(f"❌ Error al guardar el chunk en la base de datos: {e}")
        conn.rollback() # Revertir la transacción en caso de error
    finally:
        if conn:
            conn.close()

def delete_chunks_by_filename(file_name: str):
    """
    Elimina de la base de datos todos los chunks asociados a un nombre de archivo.

    Args:
        file_name (str): El nombre del archivo cuyos chunks se van a eliminar.
    """
    conn = get_db_connection()
    if not conn:
        return

    try:
        with conn.cursor() as cur:
            # Ejecuta la sentencia DELETE
            cur.execute(
                "DELETE FROM documents WHERE file_name = %s;",
                (file_name,) # Se pasa como tupla para seguridad (previene inyección SQL)
            )
            # Confirma la transacción
            conn.commit()
            # rowcount nos dice cuántas filas fueron afectadas (eliminadas)
            print(f"✅ Se eliminaron {cur.rowcount} chunks asociados al archivo '{file_name}'.")
    except psycopg2.Error as e:
        print(f"❌ Error al eliminar los chunks para el archivo '{file_name}': {e}")
        conn.rollback() # Revertir la transacción en caso de error
    finally:
        if conn:
            conn.close()

