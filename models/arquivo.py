import sqlite3

DB_PATH = 'instance/usuarios.db'

def criar_tabela_arquivos():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS arquivos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            conteudo BLOB,
            mimetype TEXT
        )
    """)
    conn.commit()
    conn.close()

def salvar_arquivo(nome, conteudo, mimetype):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO arquivos (nome, conteudo, mimetype) VALUES (?, ?, ?)",
        (nome, conteudo, mimetype)
    )
    conn.commit()
    conn.close()

def buscar_arquivo_por_nome(nome):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT conteudo, mimetype FROM arquivos WHERE nome = ? ORDER BY id DESC LIMIT 1",
        (nome,)
    )
    row = cursor.fetchone()
    conn.close()
    return row if row else (None, None)