import os, secrets, string, psycopg2
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# AGORA BUSCA OBRIGATORIAMENTE DAS VARIÁVEIS DO RENDER
# Se não estiver configurado lá, o valor padrão será None e ninguém acessa.
ADMIN_KEY = os.environ.get('ADMIN_KEY')

def get_db_connection():
    # Busca a URL do banco direto das variáveis do Render
    url = os.environ.get('DATABASE_URL')
    if not url:
        return None
    
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    
    try:
        # Conexão forçada com SSL para o Render
        return psycopg2.connect(url, sslmode='require', connect_timeout=10)
    except:
        return None

# Função de inicialização automática do banco
def init_db():
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                id SERIAL PRIMARY KEY,
                nome_empresa TEXT,
                pin_hash TEXT UNIQUE,
                limite INTEGER DEFAULT 0,
                acessos INTEGER DEFAULT 0,
                historico_chaves TEXT[] DEFAULT '{}',
                ativo BOOLEAN DEFAULT TRUE
            )
        """)
        # Garante que a coluna 'ativo' exista
        cur.execute("DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='clientes' AND column_name='ativo') THEN ALTER TABLE clientes ADD COLUMN ativo BOOLEAN DEFAULT TRUE; END IF; END $$;")
        conn.commit()
        cur.close()
        conn.close()

init_db()

# --- INTERFACE (O código HTML permanece o mesmo que enviamos antes) ---
# ... (Vou omitir o HTML longo aqui para focar na lógica da senha) ...