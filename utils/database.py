import psycopg2
import os
from dotenv import load_dotenv


load_dotenv()


DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")


def get_db_connection():
    
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
   
    conn = get_db_connection()
    if not conn:
        return

    try:
        with conn.cursor() as cur:
           
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            
         
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
        conn.rollback() 
    finally:
        if conn:
            conn.close()

def delete_chunks_by_filename(file_name: str):
    
    conn = get_db_connection()
    if not conn:
        return

    try:
        with conn.cursor() as cur:
            
            cur.execute(
                "DELETE FROM documents WHERE file_name = %s;",
                (file_name,) 
            )
           
            conn.commit()
            
            print(f"✅ Se eliminaron {cur.rowcount} chunks asociados al archivo '{file_name}'.")
    except psycopg2.Error as e:
        print(f"❌ Error al eliminar los chunks para el archivo '{file_name}': {e}")
        conn.rollback() 
    finally:
        if conn:
            conn.close()

