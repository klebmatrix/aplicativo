import os
import hashlib
import psycopg2
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configurações do Render
DATABASE_URL = os.environ.get('DATABASE_URL')
ADMIN_KEY = os.environ.get('ADMIN_KEY', 'mudar-depois')

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

# Inicializa o banco de dados
with get_db_connection() as conn:
    with conn.cursor() as cur:
        cur.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id SERIAL PRIMARY KEY,
                nome_empresa TEXT NOT NULL,
                pin_hash TEXT UNIQUE NOT NULL,
                ultimo_acesso TIMESTAMP,
                ultimo_ip TEXT
            )
        ''')
    conn.commit()

# --- INTERFACE DO CLIENTE (INDEX) ---
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

# --- PAINEL DO ADMINISTRADOR ---
HTML_ADMIN = """
<!DOCTYPE html>
<html>
<head>
    <title>KLEBMATRIX | Admin Control</title>
    <style>
        body { background: #050a14; color: #fff; font-family: sans-serif; padding: 20px; }
        .container { max-width: 900px; margin: auto; }
        .box { border: 1px solid #22c55e; padding: 20px; background: #0a0a0a; border-radius: 10px; margin-bottom: 20px; }
        input { width: 28%; padding: 10px; margin: 5px; background: #111; border: 1px solid #333; color: #22c55e; }
        button { background: #22c55e; color: #000; padding: 10px 20px; cursor: pointer; border: none; font-weight: bold; border-radius: 4px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; background: #0a0a0a; }
        th, td { border: 1px solid #1e293b; padding: 12px; text-align: left; }
        th { background: #1e293b; color: #38bdf8; }
        .btn-del { background: #ef4444; color: #fff; padding: 5px 10px; cursor: pointer; border: none; }
        .status-on { color: #22c55e; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h2 style="color: #38bdf8">KLEBMATRIX - Central de Monitoramento</h2>
        <div class="box">
            <h3>Cadastrar Novo Acesso</h3>
            <input type="password" id="adm" placeholder="Chave Mestre Admin">
            <input type="text" id="emp" placeholder="Nome da Empresa">
            <input type="text" id="pin" placeholder="PIN ou Chave Quântica">
            <button onclick="salvar()">ATIVAR</button>
        </div>
        <div class="box">
            <h3>Clientes e Localização</h3>
            <table>
                <thead>
                    <tr><th>Empresa</th><th>Último IP</th><th>Último Acesso</th><th>Ação</th></tr>
                </thead>
                <tbody id="corpoTabela"></tbody>
            </table>
            <button onclick="carregarClientes()" style="margin-top:10px; background:#38bdf8">ATUALIZAR STATUS</button>
        </div>
    </div>
    <script>
        async function salvar() {
            const adm = document.getElementById('adm').value;
            const res = await fetch('/admin/cadastrar', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    admin_key: adm,
                    nome_empresa: document.getElementById('emp').value,
                    pin: document.getElementById('pin').value
                })
            });
            const data = await res.json();
            alert(data.status === "sucesso" ? "Ativado!" : "Erro: " + data.erro);
            carregarClientes();
        }

        async function carregarClientes() {
            const adm = document.getElementById('adm').value;
            const res = await fetch('/admin/listar?admin_key=' + adm);
            const clientes = await res.json();
            const corpo = document.getElementById('corpoTabela');
            corpo.innerHTML = '';
            clientes.forEach(c => {
                corpo.innerHTML += `<tr>
                    <td>${c.nome}</td>
                    <td><code>${c.ip || '---'}</code></td>
                    <td>${c.data || 'Nunca'}</td>
                    <td><button class="btn-del" onclick="eliminar('${c.pin_ref}')">DELETAR</button></td>
                </tr>`;
            });
        }

        async function eliminar(pin_ref) {
            if(!confirm("Cortar acesso?")) return;
            const adm = document.getElementById('adm').value;
            await fetch('/admin/eliminar', {
                method: 'DELETE',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ admin_key: adm, pin: pin_ref })
            });
            carregarClientes();
        }
    </script>
</body>
</html>
"""

# --- ROTAS ---

@app.route('/')
def index():
    return render_template_string(HTML_DASHBOARD)

@app.route('/painel-secreto-kleber')
def admin_page():
    return render_template_string(HTML_ADMIN)

@app.route('/v1/quantum-key', methods=['POST'])
def get_key():
    pin = request.json.get('pin')
    ip_cliente = request.headers.get('X-Forwarded-For', request.remote_addr)
    agora = datetime.now()
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT nome_empresa FROM clientes WHERE pin_hash = %s', (pin,))
        cliente = cur.fetchone()
        if cliente:
            cur.execute('UPDATE clientes SET ultimo_acesso = %s, ultimo_ip = %s WHERE pin_hash = %s', (agora, ip_cliente, pin))
            conn.commit()
            conn.close()
            chave = hashlib.sha256(os.urandom(32)).hexdigest().upper()
            return jsonify({"status": "success", "empresa": cliente[0], "key": chave})
        conn.close()
    except: pass
    return jsonify({"status": "error"}), 401

@app.route('/admin/cadastrar', methods=['POST'])
def cadastrar():
    data = request.json
    if data.get('admin_key') != ADMIN_KEY:
        return jsonify({"erro": "Unauthorized"}), 403
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO clientes (nome_empresa, pin_hash) VALUES (%s, %s)', (data.get('nome_empresa'), data.get('pin')))
        conn.commit()
        conn.close()
        return jsonify({"status": "sucesso"})
    except: return jsonify({"erro": "PIN já existe"}), 400

@app.route('/admin/listar')
def listar_clientes():
    if request.args.get('admin_key') != ADMIN_KEY: return jsonify([])
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT nome_empresa, ultimo_ip, ultimo_acesso, pin_hash FROM clientes')
    dados = cur.fetchall()
    conn.close()
    return jsonify([{"nome": d[0], "ip": d[1], "data": d[2].strftime("%d/%m %H:%M") if d[2] else None, "pin_ref": d[3]} for d in dados])

@app.route('/admin/eliminar', methods=['DELETE'])
def eliminar_cliente():
    data = request.json
    if data.get('admin_key') != ADMIN_KEY: return jsonify({"erro": "No"}), 403
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM clientes WHERE pin_hash = %s', (data.get('pin'),))
    conn.commit()
    conn.close()
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))