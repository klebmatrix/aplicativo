import os
import secrets
import psycopg2
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- CONFIGURAÇÃO DE ACESSO ---
# Agora a chave padrão é 'admin' como você solicitou
ADMIN_KEY = os.environ.get('ADMIN_KEY', 'admin')

def get_db_connection():
    url = os.environ.get('DATABASE_URL')
    if url and url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return psycopg2.connect(url, sslmode='require')

# --- INICIALIZAÇÃO DO BANCO ---
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
        print(f"ERRO AO INICIAR BANCO: {e}")

init_db()

# --- INTERFACES (HTML) ---
HTML_INDEX = """
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>KLEBMATRIX</title>
<style>
    body { background: #0b1120; color: #38bdf8; font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
    .card { background: #1e293b; padding: 40px; border-radius: 15px; text-align: center; width: 320px; border: 1px solid #334155; }
    input { background: #0f172a; border: 1px solid #334155; color: #fff; padding: 15px; border-radius: 8px; width: 90%; margin-bottom: 20px; text-align: center; }
    button { background: #0284c7; color: white; border: none; padding: 15px; border-radius: 8px; width: 100%; cursor: pointer; font-weight: bold; }
    #res { margin-top: 20px; font-family: monospace; }
</style></head>
<body>
    <div class="card">
        <h2>KLEBMATRIX</h2>
        <input type="password" id="pin" placeholder="PIN DE ACESSO">
        <button onclick="logar()">ENTRAR</button>
        <div id="res"></div>
    </div>
    <script>
        async function logar() {
            const p = document.getElementById('pin').value.trim();
            const r = document.getElementById('res');
            const res = await fetch('/v1/quantum-key', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ pin: p })
            });
            const d = await res.json();
            if(res.ok) {
                r.style.color = "#22c55e";
                r.innerHTML = "LIBERADO!<br>" + d.key;
            } else {
                r.style.color = "#ef4444";
                r.innerHTML = "ACESSO NEGADO";
            }
        }
    </script>
</body></html>
"""

HTML_ADMIN = """
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>PAINEL ADMIN</title>
<style>
    body { background: #0f172a; color: white; font-family: sans-serif; padding: 20px; }
    .box { max-width: 800px; margin: auto; background: #1e293b; padding: 20px; border-radius: 10px; }
    input { background: #0f172a; border: 1px solid #334155; color: #22c55e; padding: 10px; margin: 5px; }
    button { padding: 10px; cursor: pointer; border: none; font-weight: bold; border-radius: 5px; }
    .btn-add { background: #22c55e; }
    .btn-list { background: #38bdf8; margin-left: 10px; }
    table { width: 100%; margin-top: 20px; border-collapse: collapse; }
    th, td { border: 1px solid #334155; padding: 10px; text-align: left; }
</style></head>
<body>
    <div class="box">
        <h3>GERENCIADOR DE CLIENTES</h3>
        <input type="password" id="mestre" placeholder="Chave Mestre (admin)">
        <hr style="border:1px solid #334155">
        <input type="text" id="nome" placeholder="Nome do Cliente">
        <input type="text" id="pin_cli" placeholder="PIN (6 dígitos)">
        <button class="btn-add" onclick="salvar()">CADASTRAR</button>
        <button class="btn-list" onclick="listar()">LISTAR TODOS</button>
        <table>
            <thead><tr><th>Cliente</th><th>PIN</th><th>Acesso</th></tr></thead>
            <tbody id="lista"></tbody>
        </table>
    </div>
    <script>
        async function salvar() {
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
            listar();
        }
        async function listar() {
            const m = document.getElementById('mestre').value;
            const res = await fetch('/admin/listar?key=' + m);
            const dados = await res.json();
            const lista = document.getElementById('lista');
            lista.innerHTML = "";
            if(dados.length === 0) { lista.innerHTML = "<tr><td colspan='3'>Nada encontrado. Verifique a chave mestre.</td></tr>"; return; }
            dados.forEach(c => {
                lista.innerHTML += `<tr><td>${c.nome}</td><td>${c.pin}</td><td>${c.data || '---'}</td></tr>`;
            });
        }
    </script>
</body></html>
"""

# --- ROTAS DO SISTEMA ---

@app.route('/')
def home(): return render_template_string(HTML_INDEX)

@app.route('/painel-secreto-kleber')
def admin_page(): return render_template_string(HTML_ADMIN)

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
            cur.close(); conn.close()
            return jsonify({"status": "success", "empresa": c[0], "key": secrets.token_hex(16).upper()})
        cur.close(); conn.close()
    except: pass
    return jsonify({"status": "error"}), 401

@app.route('/admin/cadastrar', methods=['POST'])
def cadastrar():
    d = request.json
    if d.get('admin_key') != ADMIN_KEY: return jsonify({"erro": "Chave Mestre Incorreta"}), 403
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO clientes (nome_empresa, pin_hash) VALUES (%s, %s)', (d.get('nome').strip(), d.get('pin').strip()))
        conn.commit()
        cur.close(); conn.close()
        return jsonify({"msg": "Sucesso!"})
    except Exception as e: return jsonify({"erro": "Erro: PIN já existe ou falha no banco"}), 400

@app.route('/admin/listar')
def listar():
    if request.args.get('key') != ADMIN_KEY: return jsonify([])
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT nome_empresa, pin_hash, ultimo_acesso FROM clientes')
        rows = cur.fetchall()
        cur.close(); conn.close()
        return jsonify([{"nome": r[0], "pin": r[1], "data": r[2].strftime("%d/%m %H:%M") if r[2] else None} for r in rows])
    except: return jsonify([])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))