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

# Criar a tabela no banco de dados se não existir
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

HTML_DASHBOARD = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8"><title>KLEBMATRIX | Quantum Vault</title>
    <style>
        body { background: #0b0f19; color: #38bdf8; font-family: 'Segoe UI', sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .card { background: #161e2d; padding: 40px; border-radius: 15px; border: 1px solid #1e293b; box-shadow: 0 10px 25px rgba(0,0,0,0.5); text-align: center; width: 320px; }
        h1 { font-size: 1.5rem; letter-spacing: 2px; margin-bottom: 5px; color: #fff; }
        input { background: #0b0f19; border: 1px solid #334155; color: #fff; padding: 12px; border-radius: 5px; width: 100%; margin: 20px 0; text-align: center; font-size: 1.2rem; }
        button { background: #0284c7; color: #fff; border: none; padding: 12px; border-radius: 5px; cursor: pointer; width: 100%; font-weight: bold; transition: 0.3s; }
        button:hover { background: #0ea5e9; }
        #output { margin-top: 25px; word-break: break-all; font-family: monospace; color: #22c55e; font-size: 0.85rem; }
    </style>
</head>
<body>
    <div class="card">
        <h1>KLEBMATRIX</h1>
        <div style="color: #64748b; font-size: 0.8rem; margin-bottom: 20px;">QUANTUM SECURITY INTERFACE</div>
        <input type="password" id="pinInput" placeholder="PIN de 6 dígitos" maxlength="6">
        <button onclick="requestKey()">GERAR CHAVE ATÔMICA</button>
        <div id="output"></div>
    </div>
    <script>
        async function requestKey() {
            const pin = document.getElementById('pinInput').value;
            const out = document.getElementById('output');
            out.innerText = "Processando via Qiskit...";
            try {
                const res = await fetch('/v1/quantum-key', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ pin: pin })
                });
                const data = await res.json();
                if(data.status === "success") {
                    out.innerHTML = "VALIDADO: " + data.empresa + "<br><br>CHAVE:<br>" + data.key;
                } else {
                    out.innerText = "ACESSO NEGADO";
                }
            } catch (e) { out.innerText = "Erro de conexão"; }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_DASHBOARD)

@app.route('/v1/quantum-key', methods=['POST'])
def get_key():
    pin = request.json.get('pin')
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT nome_empresa FROM clientes WHERE pin_hash = %s', (pin,))
                cliente = cur.fetchone()
        if cliente:
            # Simulando Entropia Quântica para a chave
            chave = hashlib.sha256(os.urandom(32)).hexdigest().upper()
            return jsonify({"status": "success", "empresa": cliente[0], "key": chave})
    except: pass
    return jsonify({"status": "error"}), 401

@app.route('/admin/cadastrar', methods=['POST'])
def cadastrar():
    data = request.json
    if data.get('admin_key') != ADMIN_KEY:
        return jsonify({"erro": "Unauthorized"}), 403
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute('INSERT INTO clientes (nome_empresa, pin_hash) VALUES (%s, %s)', 
                           (data.get('nome_empresa'), data.get('pin')))
            conn.commit()
        return jsonify({"status": "sucesso"})
    except:
        return jsonify({"erro": "Erro ou PIN duplicado"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))