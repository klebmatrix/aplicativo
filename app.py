import os, secrets, string, psycopg2, datetime
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Busca a chave (tenta minúsculo e maiúsculo para não ter erro)
admin_key_env = os.environ.get('admin_key') or os.environ.get('ADMIN_KEY')

def get_db_connection():
    # Busca a URL do banco (tenta todas as formas que o Render usa)
    url = os.environ.get('DATABASE_URL') or os.environ.get('database_url')
    if not url: 
        print("ERRO: DATABASE_URL não encontrada no Render!")
        return None
    
    # Correção para o SQLAlchemy/Psycopg2
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    
    try:
        return psycopg2.connect(url, sslmode='require')
    except Exception as e:
        print(f"ERRO DE CONEXÃO: {e}")
        return None

@app.before_request
def init_db():
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id SERIAL PRIMARY KEY,
                nome_empresa TEXT NOT NULL,
                pin_hash TEXT UNIQUE NOT NULL,
                limite INTEGER DEFAULT 100,
                acessos INTEGER DEFAULT 0,
                historico_chaves TEXT[] DEFAULT '{}'
            );
        ''')
        conn.commit()
        cur.close(); conn.close()

# ... (restante do HTML permanece o mesmo do anterior) ...