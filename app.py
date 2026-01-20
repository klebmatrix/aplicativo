import os
import hashlib
import psycopg2
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DATABASE_URL = os.environ.get('DATABASE_URL')
ADMIN_KEY = os.environ.get('ADMIN_KEY', 'mudar-depois')

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

# Inicializa o banco com campos de monitoramento
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

# --- PAINEL DO ADMINISTRADOR COM MONITORAMENTO ---
HTML_ADMIN = """
<!DOCTYPE html>
<html>
<head>
    <title>KLEBMATRIX | Admin Control</title>
    <style>
        body { background: #050a14; color: #fff; font-family: sans-serif; padding: 20px; }
        .container { max-width: 900px; margin: auto; }
        .box { border: 1px solid #22c55e; padding: 20px; background: #0a0a0a; border-radius: 10px; margin-bottom: 20px; }
        input { width: 30%; padding: 10px; margin: 5px; background: #111; border: 1px solid #333; color: #22c55e; }
        button { background: #22c55e; color: #000; padding: 10px 20px; cursor: pointer; border: none; font-weight: bold; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; background: #0a0a0a; }
        th, td { border: 1px solid #1e293b; padding: 12px; text-align: left; }
        th { background: #1e293b; color: #38bdf8; }
        .status-on { color: #22c55e; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h2 style="color: #38bdf8">KLEBMATRIX - Central de Monitoramento</h2>
        
        <div class="box">
            <h3>Cadastrar Novo Acesso</h3>
            <input type="password" id="adm" placeholder="Chave Mestre">
            <input type="text" id="emp" placeholder="Nome da Empresa">
            <input type="text" id="pin" placeholder="PIN ou Chave Quântica">
            <button onclick="salvar()">ATIVAR</button>
        </div>

        <div class="box">
            <h3>Clientes e Localização</h3>
            <table id="tabelaClientes">
                <thead>
                    <tr>
                        <th>Empresa</th>
                        <th>Último IP</th>
                        <th>Último Acesso</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody id="corpoTabela"></tbody>
            </table>
            <button onclick="carregarClientes()" style="margin-top:10px; background:#38bdf8">Atualizar Monitoramento</button>
        </div>
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
                    <td>${c.ip || '---'}</td>
                    <td>${c.data || 'Nunca'}</td>
                    <td class="status-on">ATIVO</td>
                </tr>`;
            });
        }
    </script>
</body>
</html>
"""

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
            # Registra o acesso e o IP
            cur.execute('UPDATE clientes SET ultimo_acesso = %s, ultimo_ip = %s WHERE pin_hash = %s', 
                       (agora, ip_cliente, pin))
            conn.commit()
            chave = hashlib.sha256(os.urandom(32)).hexdigest().upper()
            return jsonify({"status": "success", "empresa": cliente[0], "key": chave})
        conn.close()
    except: pass
    return jsonify({"status": "error"}), 401

@app.route('/admin/listar')
def listar_clientes():
    if request.args.get('admin_key') != ADMIN_KEY:
        return jsonify([])
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT nome_empresa, ultimo_ip, ultimo_acesso FROM clientes')
    dados = cur.fetchall()
    conn.close()
    
    return jsonify([{"nome": d[0], "ip": d[1], "data": d[2].strftime("%d/%m %H:%M") if d[2] else None} for d in dados])

# (Mantenha o restante das rotas como /admin/cadastrar e index)