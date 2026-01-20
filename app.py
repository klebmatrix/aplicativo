import os
import secrets
import psycopg2
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

ADMIN_KEY = os.environ.get('ADMIN_KEY', 'admin')

def get_db_connection():
    url = os.environ.get('DATABASE_URL')
    if url and url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return psycopg2.connect(url, sslmode='require')

# HTML COMPLETO COM LOGIN E PAINEL
HTML_FINAL = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>KLEBMATRIX SYSTEM</title>
    <style>
        body { background: #0b1120; color: white; font-family: sans-serif; display: flex; justify-content: center; padding-top: 50px; margin: 0; }
        .container { background: #1e293b; padding: 30px; border-radius: 15px; width: 400px; text-align: center; border: 1px solid #334155; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        input { width: 85%; padding: 12px; margin: 10px 0; background: #0f172a; border: 1px solid #334155; color: white; border-radius: 8px; text-align: center; font-size: 1rem; }
        button { width: 92%; padding: 12px; background: #0284c7; border: none; color: white; font-weight: bold; cursor: pointer; border-radius: 8px; margin-top: 10px; transition: 0.3s; }
        button:hover { background: #0ea5e9; }
        .btn-admin { background: #22c55e; }
        table { width: 100%; margin-top: 20px; border-collapse: collapse; font-size: 14px; }
        th, td { border: 1px solid #334155; padding: 10px; text-align: left; }
        #status { margin-top: 20px; font-weight: bold; min-height: 40px; }
    </style>
</head>
<body>
    <div class="container">
        {% if tipo == 'admin' %}
            <h2 style="color: #22c55e;">PAINEL MASTER</h2>
            <input type="password" id="mestre" placeholder="Chave Mestre">
            <hr style="border: 0; border-top: 1px solid #334155; margin: 20px 0;">
            <input type="text" id="nome" placeholder="Nome da Empresa">
            <input type="text" id="pin" placeholder="PIN de 6 dígitos">
            <button class="btn-admin" onclick="cadastrar()">CADASTRAR</button>
            <button onclick="listar()" style="background: #38bdf8;">ATUALIZAR LISTA</button>
            <table>
                <thead><tr><th>Empresa</th><th>PIN</th></tr></thead>
                <tbody id="lista"></tbody>
            </table>
        {% else %}
            <h1 style="color: #38bdf8; margin-bottom: 30px;">KLEBMATRIX</h1>
            <input type="password" id="pin_acesso" placeholder="DIGITE SEU PIN">
            <button onclick="acessar()">OBTER CHAVE QUANTUM</button>
            <div id="status"></div>
        {% endif %}
    </div>

    <script>
        async function cadastrar() {
            const res = await fetch('/admin/cadastrar', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    key: document.getElementById('mestre').value,
                    n: document.getElementById('nome').value,
                    p: document.getElementById('pin').value
                })
            });
            const d = await res.json();
            alert(d.msg || d.erro);
            listar();
        }

        async function listar() {
            const k = document.getElementById('mestre').value;
            const res = await fetch('/admin/listar?key=' + k);
            const dados = await res.json();
            const corpo = document.getElementById('lista');
            corpo.innerHTML = "";
            if(dados.length === 0) { corpo.innerHTML = "<tr><td colspan='2'>Chave Incorreta</td></tr>"; return; }
            dados.forEach(c => {
                corpo.innerHTML += `<tr><td>${c.n}</td><td>${c.p}</td></tr>`;
            });
        }

        async function acessar() {
            const p = document.getElementById('pin_acesso').value;
            const s = document.getElementById('status');
            s.innerHTML = "Autenticando...";
            const res = await fetch('/v1/quantum-key', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ pin: p })
            });
            const d = await res.json();
            if(res.ok) {
                s.style.color = "#22c55e";
                s.innerHTML = "ACESSO LIBERADO!<br><small style='color:white'>" + d.key + "</small>";
            } else {
                s.style.color = "#ef4444";
                s.innerHTML = "PIN INVÁLIDO";
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_FINAL, tipo='login')

@app.route('/painel-secreto-kleber')
def admin_page():
    return render_template_string(HTML_FINAL, tipo='admin')

@app.route('/admin/cadastrar', methods=['POST'])
def add():
    d = request.json
    if d.get('key') != ADMIN_KEY: return jsonify({"erro": "Chave Mestre Errada"}), 403
    try:
        conn = get_db_connection(); cur = conn.cursor()
        cur.execute("INSERT INTO clientes (nome_empresa, pin_hash) VALUES (%s, %s)", (d['n'], d['p']))
        conn.commit(); cur.close(); conn.close()
        return jsonify({"msg": "Sucesso!"})
    except: return jsonify({"erro": "Erro ao salvar"}), 400

@app.route('/admin/listar')
def list_all():
    if request.args.get('key') != ADMIN_KEY: return jsonify([])
    try:
        conn = get_db_connection(); cur = conn.cursor()
        cur.execute("SELECT nome_empresa, pin_hash FROM clientes")
        rows = cur.fetchall()
        cur.close(); conn.close()
        return jsonify([{"n": r[0], "p": r[1]} for r in rows])
    except: return jsonify([])

@app.route('/v1/quantum-key', methods=['POST'])
def login():
    p = request.json.get('pin', '').strip()
    try:
        conn = get_db_connection(); cur = conn.cursor()
        cur.execute("SELECT nome_empresa FROM clientes WHERE pin_hash = %s", (p,))
        c = cur.fetchone()
        cur.close(); conn.close()
        if c:
            return jsonify({"status": "success", "key": secrets.token_hex(16).upper()})
    except: pass
    return jsonify({"status": "error"}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))