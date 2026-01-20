import os
import secrets
import psycopg2
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Chave vinda do ambiente ou padrão
ADMIN_KEY = os.environ.get('ADMIN_KEY', 'admin')

def get_db_connection():
    url = os.environ.get('DATABASE_URL')
    if url and url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return psycopg2.connect(url, sslmode='require')

# HTML UNIFICADO E CORRIGIDO
HTML_MASTER = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>KLEBMATRIX SYSTEM</title>
    <style>
        body { background: #0f172a; color: white; font-family: sans-serif; display: flex; flex-direction: column; align-items: center; padding: 50px; }
        .box { background: #1e293b; padding: 30px; border-radius: 12px; width: 350px; text-align: center; border: 1px solid #334155; }
        input { width: 90%; padding: 12px; margin: 10px 0; background: #0f172a; border: 1px solid #334155; color: white; border-radius: 5px; text-align: center; }
        button { width: 95%; padding: 12px; background: #0284c7; border: none; color: white; font-weight: bold; cursor: pointer; border-radius: 5px; margin-top: 10px; }
        table { width: 100%; margin-top: 20px; border-collapse: collapse; background: #0f172a; }
        th, td { border: 1px solid #334155; padding: 10px; font-size: 14px; }
        #status { margin-top: 20px; font-family: monospace; }
    </style>
</head>
<body>

    {% if tipo == 'admin' %}
    <div class="box" style="width: 600px;">
        <h2>PAINEL ADMINISTRATIVO</h2>
        <input type="password" id="mestre" placeholder="Chave Mestre">
        <hr style="border: 0; border-top: 1px solid #334155; margin: 20px 0;">
        <input type="text" id="nome_cli" placeholder="Nome da Empresa">
        <input type="text" id="pin_cli" placeholder="PIN de 6 dígitos">
        <button onclick="cadastrar()" style="background: #22c55e;">CADASTRAR CLIENTE</button>
        <button onclick="listar()" style="background: #38bdf8;">ATUALIZAR LISTA</button>
        <table>
            <thead><tr><th>Empresa</th><th>PIN</th><th>Acesso</th></tr></thead>
            <tbody id="lista_corpo"></tbody>
        </table>
    </div>
    {% else %}
    <div class="box">
        <h1 style="color: #38bdf8;">KLEBMATRIX</h1>
        <input type="password" id="pin_acesso" placeholder="DIGITE SEU PIN">
        <button onclick="acessar()">OBTER CHAVE</button>
        <div id="status"></div>
    </div>
    {% endif %}

    <script>
        async function cadastrar() {
            const m = document.getElementById('mestre').value;
            const n = document.getElementById('nome_cli').value;
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
            const corpo = document.getElementById('lista_corpo');
            corpo.innerHTML = "";
            if(dados.length === 0) { corpo.innerHTML = "<tr><td colspan='3'>Vazio ou Chave Errada</td></tr>"; return; }
            dados.forEach(c => {
                const tr = document.createElement('tr');
                tr.innerHTML = `<td>${c.nome}</td><td>${c.pin}</td><td>${c.data || '---'}</td>`;
                corpo.appendChild(tr);
            });
        }

        async function acessar() {
            const p = document.getElementById('pin_acesso').value;
            const s = document.getElementById('status');
            s.innerHTML = "Processando...";
            const res = await fetch('/v1/quantum-key', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ pin: p })
            });
            const d = await res.json();
            if(res.ok) {
                s.style.color = "#22c55e";
                s.innerHTML = "LIBERADO!<br>" + d.key;
            } else {
                s.style.color = "#ef4444";
                s.innerHTML = "ACESSO NEGADO";
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_MASTER, tipo='login')

@app.route('/painel-secreto-kleber')
def admin_page():
    return render_template_string(HTML_MASTER, tipo='admin')

@app.route('/v1/quantum-key', methods=['POST'])
def login_cli():
    pin = request.json.get('pin', '').strip()
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT nome_empresa FROM clientes WHERE pin_hash = %s', (pin,))
        c = cur.fetchone()
        if c:
            cur.execute('UPDATE clientes SET ultimo_acesso=%s WHERE pin_hash=%s', (datetime.now(), pin))
            conn.commit()
            cur.close(); conn.close()
            return jsonify({"status": "success", "empresa": c[0], "key": secrets.token_hex(16).upper()})
        cur.close(); conn.close()
    except: pass
    return jsonify({"status": "error"}), 401

@app.route('/admin/cadastrar', methods=['POST'])
def add_cli():
    d = request.json
    if d.get('admin_key') != ADMIN_KEY: return jsonify({"erro": "Chave Mestre Errada"}), 403
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO clientes (nome_empresa, pin_hash) VALUES (%s, %s)', (d.get('nome'), d.get('pin')))
        conn.commit()
        cur.close(); conn.close()
        return jsonify({"msg": "Sucesso!"})
    except: return jsonify({"erro": "Erro no cadastro"}), 400

@app.route('/admin/listar')
def list_cli():
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