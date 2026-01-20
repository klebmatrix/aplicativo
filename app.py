import os
import secrets
import psycopg2
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- CONFIGURAÇÃO DE SEGURANÇA ---
# Se não houver variável no Render, o padrão será 190126
ADMIN_KEY = os.environ.get('ADMIN_KEY', '190126')

def get_db_connection():
    url = os.environ.get('DATABASE_URL')
    if url and url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return psycopg2.connect(url, sslmode='require')

# --- CRIAÇÃO DA TABELA (AUTO-REPARO) ---
def init_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
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
        cur.close()
        conn.close()
    except Exception as e:
        print(f"ERRO CRÍTICO BANCO: {e}")

init_db()

# --- PÁGINA INICIAL (AZUL) ---
HTML_INDEX = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8"><title>KLEBMATRIX | Vault</title>
    <style>
        body { background: #0b1120; color: #38bdf8; font-family: 'Segoe UI', sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .card { background: #1e293b; padding: 40px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); text-align: center; width: 350px; border: 1px solid #334155; }
        input { background: #0f172a; border: 1px solid #334155; color: #fff; padding: 15px; border-radius: 8px; width: 90%; margin-bottom: 20px; text-align: center; font-size: 1.2rem; }
        button { background: #0284c7; color: white; border: none; padding: 15px; border-radius: 8px; width: 100%; cursor: pointer; font-weight: bold; transition: 0.3s; }
        button:hover { background: #0ea5e9; }
        #res { margin-top: 25px; font-family: monospace; font-size: 0.9rem; min-height: 50px; }
    </style>
</head>
<body>
    <div class="card">
        <h2 style="color:white; margin-bottom:30px;">KLEBMATRIX</h2>
        <input type="password" id="pin" placeholder="DIGITE SEU PIN">
        <button onclick="entrar()">AUTENTICAR</button>
        <div id="res"></div>
    </div>
    <script>
        async function entrar() {
            const p = document.getElementById('pin').value.trim();
            const r = document.getElementById('res');
            r.innerHTML = "Verificando...";
            try {
                const response = await fetch('/v1/quantum-key', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ pin: p })
                });
                const d = await response.json();
                if(response.ok) {
                    r.style.color = "#22c55e";
                    r.innerHTML = "<b>ACESSO LIBERADO:</b> " + d.empresa + "<br><br><small>" + d.key + "</small>";
                } else {
                    r.style.color = "#ef4444";
                    r.innerHTML = "ACESSO NEGADO";
                }
            } catch(e) { r.innerHTML = "Erro de conexão com servidor"; }
        }
    </script>
</body>
</html>
"""

# --- PÁGINA ADMIN (PAINEL) ---
HTML_ADMIN = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8"><title>ADMIN | KlebMatrix</title>
    <style>
        body { background: #0f172a; color: white; font-family: sans-serif; padding: 30px; }
        .container { max-width: 900px; margin: auto; background: #1e293b; padding: 25px; border-radius: 12px; }
        input { background: #0f172a; border: 1px solid #334155; color: #22c55e; padding: 10px; margin: 5px; border-radius: 5px; }
        button { padding: 10px 20px; border-radius: 5px; cursor: pointer; border: none; font-weight: bold; }
        .btn-add { background: #22c55e; color: #064e3b; }
        .btn-list { background: #38bdf8; color: #0c4a6e; }
        table { width: 100%; margin-top: 25px; border-collapse: collapse; }
        th, td { padding: 12px; border-bottom: 1px solid #334155; text-align: left; }
        tr:hover { background: #334155; }
    </style>
</head>
<body>
    <div class="container">
        <h3>CONTROLE DE ACESSOS</h3>
        <input type="password" id="mestre" placeholder="Chave Mestre">
        <hr style="border: 0; border-top: 1px solid #334155; margin: 20px 0;">
        <input type="text" id="nome" placeholder="Nome do Cliente">
        <input type="text" id="pin_cli" placeholder="PIN de 6 dígitos">
        <button class="btn-add" onclick="cadastrar()">ATIVAR NOVO</button>
        <button class="btn-list" onclick="listar()">LISTAR / ATUALIZAR</button>

        <table id="tabela">
            <thead>
                <tr><th>Cliente</th><th>PIN</th><th>Último IP</th><th>Visto em</th></tr>
            </thead>
            <tbody id="lista"></tbody>
        </table>
    </div>

    <script>
        async function cadastrar() {
            const m = document.getElementById('mestre').value;
            const n = document.getElementById('nome').value;
            const p = document.getElementById('pin_cli').value;
            const res = await fetch('/admin/cadastrar', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ admin_key: m, nome: n, pin: p })
            });
            const d = await res.json();
            alert(d.msg || d.erro);
            if(res.ok) listar();
        }

        async function listar() {
            const m = document.getElementById('mestre').value;
            const res = await fetch('/admin/listar?key=' + m);
            const dados = await res.json();
            const lista = document.getElementById('lista');
            lista.innerHTML = "";
            
            if(dados.length === 0) {
                lista.innerHTML = "<tr><td colspan='4'>Nenhum cliente ou chave incorreta</td></tr>";
                return;
            }
            
            dados.forEach(c => {
                lista.innerHTML += `<tr>
                    <td>${c.nome}</td>
                    <td>${c.pin}</td>
                    <td>${c.ip || '---'}</td>
                    <td>${c.data || 'Nunca'}</td>
                </tr>`;
            });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home(): return render_template_string(HTML_INDEX)

@app.route('/painel-secreto-kleber')
def admin(): return render_template_string(HTML_ADMIN)

@app.route('/v1/quantum-key', methods=['POST'])
def login():
    pin = request.json.get('pin', '').strip()
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT nome_empresa FROM clientes WHERE pin_hash = %s', (pin,))
        c = cur.fetchone()
        if c:
            ip = request.headers.get('X-Forwarded-For', request.remote_addr)
            cur.execute('UPDATE clientes SET ultimo_acesso=%s, ultimo_ip=%s WHERE pin_hash=%s', (datetime.now(), ip, pin))
            conn.commit()
            return jsonify({"status": "success", "empresa": c[0], "key": secrets.token_hex(16).upper()})
    except: pass
    return jsonify({"status": "error"}), 401

@app.route('/admin/cadastrar', methods=['POST'])
def add():
    d = request.json
    if d.get('admin_key') != ADMIN_KEY: return jsonify({"erro": "Chave Mestre Errada"}), 403
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO clientes (nome_empresa, pin_hash) VALUES (%s, %s)', (d.get('nome').strip(), d.get('pin').strip()))
        conn.commit()
        cur.close(); conn.close()
        return jsonify({"msg": "Sucesso! Cliente cadastrado."})
    except Exception as e: return jsonify({"erro": f"Erro: {str(e)}"}), 400

@app.route('/admin/listar')
def list_all():
    if request.args.get('key') != ADMIN_KEY: return jsonify([])
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT nome_empresa, pin_hash, ultimo_ip, ultimo_acesso FROM clientes')
        rows = cur.fetchall()
        cur.close(); conn.close()
        return jsonify([{"nome": r[0], "pin": r[1], "ip": r[2], "data": r[3].strftime("%d/%m %H:%M") if r[3] else None} for r in rows])
    except: return jsonify([])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))