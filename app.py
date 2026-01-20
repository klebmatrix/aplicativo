import os
import hashlib
import psycopg2
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DATABASE_URL = os.environ.get('DATABASE_URL')
ADMIN_KEY = os.environ.get('ADMIN_KEY', 'mudar-depois')

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

# Inicializa o banco com suporte a textos longos
with get_db_connection() as conn:
    with conn.cursor() as cur:
        cur.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id SERIAL PRIMARY KEY,
                nome_empresa TEXT NOT NULL,
                pin_hash TEXT UNIQUE NOT NULL
            )
        ''')
    conn.commit()

# DASHBOARD DO CLIENTE (Aceita PIN ou Chave Quântica)
HTML_DASHBOARD = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8"><title>KLEBMATRIX | Quantum Vault</title>
    <style>
        body { background: #0b0f19; color: #38bdf8; font-family: 'Segoe UI', sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .card { background: #161e2d; padding: 40px; border-radius: 15px; border: 1px solid #1e293b; box-shadow: 0 10px 25px rgba(0,0,0,0.5); text-align: center; width: 450px; }
        h1 { font-size: 1.5rem; letter-spacing: 2px; margin-bottom: 5px; color: #fff; }
        input { background: #0b0f19; border: 1px solid #334155; color: #fff; padding: 12px; border-radius: 5px; width: 90%; margin: 20px 0; text-align: center; font-size: 1rem; }
        button { background: #0284c7; color: #fff; border: none; padding: 12px; border-radius: 5px; cursor: pointer; width: 95%; font-weight: bold; transition: 0.3s; }
        button:hover { background: #0ea5e9; }
        #output { margin-top: 25px; word-break: break-all; font-family: monospace; color: #22c55e; font-size: 0.85rem; background: #0b0f19; padding: 10px; border-radius: 5px; min-height: 50px;}
    </style>
</head>
<body>
    <div class="card">
        <h1>KLEBMATRIX</h1>
        <div style="color: #64748b; font-size: 0.8rem; margin-bottom: 20px;">INTERFACE DE SEGURANÇA QUÂNTICA</div>
        <input type="password" id="pinInput" placeholder="Insira seu PIN ou Chave Quântica">
        <button onclick="requestKey()">AUTENTICAR E GERAR CHAVE</button>
        <div id="output">Aguardando autenticação...</div>
    </div>
    <script>
        async function requestKey() {
            const pin = document.getElementById('pinInput').value;
            const out = document.getElementById('output');
            out.innerText = "Consultando Entropia Quântica...";
            try {
                const res = await fetch('/v1/quantum-key', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ pin: pin })
                });
                const data = await res.json();
                if(data.status === "success") {
                    out.innerHTML = "<span style='color: #64748b'>ACESSO:</span> " + data.empresa + "<br><br><span style='color: #38bdf8'>NOVA CHAVE GERADA:</span><br>" + data.key;
                } else {
                    out.innerText = "ERRO: ACESSO NEGADO";
                    out.style.color = "#ef4444";
                }
            } catch (e) { out.innerText = "Erro de conexão"; }
        }
    </script>
</body>
</html>
"""

# PAINEL DO ADMINISTRADOR (Sem limite de caracteres)
HTML_ADMIN = """
<!DOCTYPE html>
<html>
<head>
    <title>KLEBMATRIX | Admin</title>
    <style>
        body { background: #000; color: #fff; font-family: sans-serif; padding: 50px; display: flex; justify-content: center; }
        .box { border: 1px solid #22c55e; padding: 30px; width: 500px; background: #0a0a0a; border-radius: 10px; }
        input { width: 95%; padding: 12px; margin: 15px 0; background: #111; border: 1px solid #333; color: #22c55e; }
        button { background: #22c55e; color: #000; padding: 12px; width: 100%; cursor: pointer; border: none; font-weight: bold; }
        #msg { margin-top: 20px; color: #38bdf8; }
    </style>
</head>
<body>
    <div class="box">
        <h2 style="color: #22c55e">KLEBMATRIX - Gestão de Clientes</h2>
        <input type="password" id="adm" placeholder="Sua Chave Mestre (ADMIN_KEY)">
        <input type="text" id="emp" placeholder="Nome da Empresa Cliente">
        <input type="text" id="pin" placeholder="PIN ou Chave Quântica do Cliente">
        <button onclick="salvar()">ATIVAR ACESSO</button>
        <p id="msg"></p>
    </div>
    <script>
        async function salvar() {
            const res = await fetch('/admin/cadastrar', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    admin_key: document.getElementById('adm').value,
                    nome_empresa: document.getElementById('emp').value,
                    pin: document.getElementById('pin').value
                })
            });
            const data = await res.json();
            document.getElementById('msg').innerText = data.status === "sucesso" ? "ACESSO ATIVADO COM SUCESSO!" : "ERRO: " + data.erro;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_DASHBOARD)

@app.route('/painel-secreto-kleber')
def admin_page():
    return render_template_string(HTML_ADMIN)

@app.route('/v1/quantum-key', methods=['POST'])
def get_key():
    pin = request.json.get('pin')
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT nome_empresa FROM clientes WHERE pin_hash = %s', (pin,))
                cliente = cur.fetchone()
        if cliente:
            chave = hashlib.sha256(os.urandom(32)).hexdigest().upper()
            return jsonify({"status": "success", "empresa": cliente[0], "key": chave})
    except: pass
    return jsonify({"status": "error"}), 401

@app.route('/admin/cadastrar', methods=['POST'])
def cadastrar():
    data = request.json
    if data.get('admin_key') != ADMIN_KEY:
        return jsonify({"erro": "Chave Mestre Inválida"}), 403
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute('INSERT INTO clientes (nome_empresa, pin_hash) VALUES (%s, %s)', 
                           (data.get('nome_empresa'), data.get('pin')))
            conn.commit()
        return jsonify({"status": "sucesso"})
    except Exception as e:
        return jsonify({"erro": "PIN/Chave já em uso ou erro no banco"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))