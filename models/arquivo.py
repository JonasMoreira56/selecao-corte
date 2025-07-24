import os
import psycopg2

# A URL do banco de dados é fornecida pelo Heroku na variável de ambiente DATABASE_URL
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    """Cria e retorna uma nova conexão com o banco de dados PostgreSQL."""
    # O sslmode='require' é geralmente necessário para conexões com o Heroku Postgres
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    return conn

def criar_tabela_arquivos():
    """Cria a tabela 'arquivos' no banco de dados PostgreSQL se ela não existir."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Sintaxe SQL ajustada para PostgreSQL:
            # - SERIAL PRIMARY KEY para auto-incremento
            # - BYTEA para dados binários (substitui BLOB)
            # - Adicionado um campo de timestamp para rastreamento
            cur.execute("""
                CREATE TABLE IF NOT EXISTS arquivos (
                    id SERIAL PRIMARY KEY,
                    nome TEXT NOT NULL,
                    conteudo BYTEA NOT NULL,
                    mimetype TEXT NOT NULL,
                    data_upload TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        conn.commit()
    finally:
        conn.close()

def salvar_arquivo(nome, conteudo, mimetype):
    """Salva um novo arquivo no banco de dados."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Placeholders no psycopg2 são '%s' em vez de '?'
            cur.execute(
                "INSERT INTO arquivos (nome, conteudo, mimetype) VALUES (%s, %s, %s)",
                (nome, conteudo, mimetype)
            )
        conn.commit()
    finally:
        conn.close()

def buscar_arquivo_por_nome(nome):
    """Busca o arquivo mais recente com o nome fornecido."""
    conn = get_db_connection()
    row = None
    try:
        with conn.cursor() as cur:
            # Placeholders no psycopg2 são '%s' em vez de '?'
            cur.execute(
                "SELECT conteudo, mimetype FROM arquivos WHERE nome = %s ORDER BY id DESC LIMIT 1",
                (nome,)
            )
            row = cur.fetchone()
    finally:
        conn.close()
    return row if row else (None, None)