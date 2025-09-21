-- Habilitar la extensión pgvector si aún no está habilitada.
CREATE EXTENSION IF NOT EXISTS vector;

-- Crear la tabla 'documents' para almacenar los fragmentos (chunks) de texto y sus vectores.
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    chunk_index INTEGER NOT NULL,
    content TEXT,

    -- ### NUEVO Y FUNDAMENTAL ###
    -- Columna para almacenar el embedding (vector) del texto contenido en 'content'.
    --
    -- IMPORTANTE: El número '1536' es la dimensionalidad del vector. DEBES cambiar
    -- este valor para que coincida EXACTAMENTE con el modelo de embedding que vayas a utilizar.
    --
    -- Dimensiones de modelos populares:
    --   - text-embedding-3-small (OpenAI): 1536
    --   - text-embedding-ada-002 (OpenAI): 1536
    --   - all-MiniLM-L6-v2 (Sentence Transformers): 384
    --   - BGE-large-en-v1.5 (BAAI): 1024
    embedding vector(1536),

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(file_name, chunk_index)
);

-- ### NUEVO Y RECOMENDADO ###
-- Crear un índice HNSW (Hierarchical Navigable Small World) en la columna 'embedding'.
-- Este tipo de índice acelera drásticamente las búsquedas de similitud (vecinos más cercanos),
-- que es la operación principal en una base de datos vectorial. Sin un índice, las búsquedas
-- serían muy lentas en tablas grandes.
-- 'vector_l2_ops' especifica que usaremos la distancia Euclidiana (L2) para la búsqueda.
CREATE INDEX IF NOT EXISTS documents_embedding_idx ON documents USING hnsw (embedding vector_l2_ops);

-- Mensaje de confirmación para los logs de Docker.
\echo '✅ Script de inicialización completado: Tabla "documents" con columna de embedding e índice HNSW creados.'