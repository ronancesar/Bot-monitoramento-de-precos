import sqlite3
from pathlib import Path

# Define o caminho do banco de dados
ROOT_DIR = Path(__file__).parent.parent
DB_PATH = ROOT_DIR / "monitor.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT NOT NULL,
            url TEXT NOT NULL,
            preco_alvo REAL,
            ultimo_preco REAL,
            titulo_produto TEXT,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
    print(f"✅ Banco de dados inicializado em: {DB_PATH}")

def adicionar_produto(chat_id, url, preco_alvo):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # AQUI ESTAVA O ERRO ANTES (float estava escrito errado)
        cursor.execute("""
            INSERT INTO produtos (chat_id, url, preco_alvo)
            VALUES (?, ?, ?)
        """, (str(chat_id), url, float(preco_alvo)))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ Erro ao adicionar no banco: {e}")
        return False
    finally:
        conn.close()

def buscar_todos_produtos():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, chat_id, url, preco_alvo, ultimo_preco FROM produtos")
    produtos = cursor.fetchall()
    conn.close()
    return produtos

def atualizar_preco_produto(produto_id, novo_preco, titulo=None):
    conn = get_connection()
    cursor = conn.cursor()
    if titulo:
        cursor.execute("UPDATE produtos SET ultimo_preco = ?, titulo_produto = ? WHERE id = ?", (novo_preco, titulo, produto_id))
    else:
        cursor.execute("UPDATE produtos SET ultimo_preco = ? WHERE id = ?", (novo_preco, produto_id))
    conn.commit()
    conn.close()

def remover_produto(produto_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()