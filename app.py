import os
import secrets
import psycopg2
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- SEGURANÇA MÁXIMA ---
# O código agora busca OBRIGATORIAMENTE do Render. 
# Se não estiver lá, ele usa um valor vazio para ninguém conseguir adivinhar.
ADMIN_KEY = os.environ.get('ADMIN_KEY')

def get_db_connection():
    url = os.environ.get('DATABASE_URL')
    if url and url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return psycopg2.connect(url, sslmode='require')

def init_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # Garante que a estrutura do banco suporte a contabilização
        cur.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                id SERIAL PRIMARY KEY, 
                nome_empresa TEXT, 
                pin_hash TEXT UNIQUE, 
                acessos INTEGER DEFAULT 0, 
                ultimo_acesso TIMESTAMP
            )
        """)
        conn.commit()
        cur.close(); conn.close()
    except Exception as e:
        print(f"Erro ao iniciar banco: {e}")

init_db()

# --- HTML E INTERFACE ---
HTML_SISTEMA = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>KLEBMATRIX | Controle Total</title>
    <style>
        body { background: #0b1120; color: white; font-family: sans-serif; display: flex; justify-content: center; padding-top: 30px; margin: 0; }
        .container { background: #1e293b; padding: 25px; border-radius: 15px; width: 650px; border: 1px solid #334155; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        input { width: 80%; padding: 12px; margin: 5px 0; background: #0f172a; border: 1px solid #334155; color: white; border-radius: 8px; font-size: 1rem; }
        button { padding: 12px 25px; background: #0284c7; border: none; color: white; font-weight: bold; cursor: pointer; border-radius: 8px; margin-top: 10px; transition: 0.3s; }
        button:hover { background: #0ea5e9; }
        table { width: 100%; margin-top: 25px; border-collapse: collapse; font-size: 14px; }
        th, td { border: 1px solid #334155; padding: 12px; text-align: left; }
        th { background: #0f172a; color: #38bdf8; }
        .badge { background: #064e3b; color: #22c55e; padding: 3px 8px; border-radius: 5px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        {% if tipo == 'admin' %}
            <h2 style="color: #38bdf8;">📊 RELATÓRIO DE GESTÃO</h2>
            <div style="margin-bottom: 20px;">
                <input type="password" id="mestre" placeholder="Chave Mestre do Render">
                <button onclick="listar()" style="background: #38bdf8; color: #082f49;">VERIFICAR ACESSOS</button>
            </div>
            
            <div style="background:#0f172a; padding:15px; border-radius:10px; border: 1px solid #1e293b;">
                <h4 style="margin-top:0">Novo Cliente</h4>
                <input type="text" id="nome" placeholder="Nome da Empresa">
                <input type="text" id="pin" placeholder="PIN (6 dígitos)">
                <button onclick="cadastrar()" style="background:#22c55e">ATIVAR CLIENTE</button>
            </div>

            <table>
                <thead>
                    <tr><th>Empresa</th><th>PIN</th><th>Acessos</th><th>Último Uso</th></tr>
                </thead>
                <tbody id="lista"></tbody>
            </table>
        {% else %}
            <div style="width:350px; margin:auto; text-align:center;">
                <h1 style="color: #38bdf8; margin-bottom:40px;">KLEBMATRIX</h1>
                <input type="password" id="pin_acesso" placeholder="DIGITE SEU PIN">
                <button onclick="acessar()" style="width:100%">GERAR CHAVE</button>
                <div id="status" style="margin-top:30px; font-weight:bold;"></div>
            </div>
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
            if (res.status === 403) { alert("Chave Mestre Inválida!"); return; }
            const dados = await res.json();
            const corpo = document.getElementById('lista');
            corpo.innerHTML = "";
            dados.forEach(c => {
                corpo.innerHTML += `<tr>
                    <td>${c.n}</td>
                    <td><code>${c.p}</code></td>
                    <td><span class="badge">${c.qtd}</span></td>
                    <td>${c.data || '---'}</td>
                </tr>`;
            });
        }

        async function acessar() {
            const p = document.getElementById('pin_acesso').value;
            const s = document.getElementById('status');
            s.innerHTML = "Validando...";
            const res = await fetch('/v1/quantum-key', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ pin: p })
            });
            const d = await res.json();
            if(res.ok) {
                s.style.color = "#22c55e";
                s.innerHTML = "CHAVE GERADA COM SUCESSO!<br><br><span style='background:#fff; color:#000; padding:10px; border-radius:5px'>" + d.key + "</span>";
            } else {
                s.style.color = "#ef4444";
                s.innerHTML = "PIN INCORRETO OU EXPIRADO";
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home(): return render_template_string(HTML_SISTEMA, tipo='login')

@app.route('/painel-secreto-kleber')
def admin_page(): return render_template_string(HTML_SISTEMA, tipo='admin')

@app.route('/admin/cadastrar', methods=['POST'])
def add():
    d = request.json
    # Comparação direta com a variável do Render
    if not ADMIN_KEY or d.get('key') != ADMIN_KEY: 
        return jsonify({"erro": "Acesso negado. Configure ADMIN_KEY no Render."}), 403
    try:
        conn = get_db_connection(); cur = conn.cursor()
        cur.execute("INSERT INTO clientes (nome_empresa, pin_hash, acessos) VALUES (%s, %s, 0)", (d['n'], d['p']))
        conn.commit(); cur.close(); conn.close()
        return jsonify({"msg": "Cliente cadastrado com sucesso!"})
    except: return jsonify({"erro": "Este PIN já está em uso por outra empresa."}), 400

@app.route('/admin/listar')
def list_all():
    if not ADMIN_KEY or request.args.get('key') != ADMIN_KEY: 
        return jsonify([]), 403
    try:
        conn = get_db_connection(); cur = conn.cursor()
        cur.execute("SELECT nome_empresa, pin_hash, acessos, ultimo_acesso FROM clientes ORDER BY ultimo_acesso DESC NULLS LAST")
        rows = cur.fetchall()
        cur.close(); conn.close()
        return jsonify([{"n": r[0], "p": r[1], "qtd": r[2], "data": r[3].strftime("%d/%m %H:%M") if r[3] else None} for r in rows])
    except: return jsonify([])

@app.route('/v1/quantum-key', methods=['POST'])
def login():
    p = request.json.get('pin', '').strip()
    try:
        conn = get_db_connection(); cur = conn.cursor()
        cur.execute("UPDATE clientes SET acessos = acessos + 1, ultimo_acesso = %s WHERE pin_hash = %s RETURNING nome_empresa", (datetime.now(), p))
        c = cur.fetchone()
        conn.commit(); cur.close(); conn.close()
        if c:
            return jsonify({"status": "success", "key": secrets.token_hex(16).upper()})
    except: pass
    return jsonify({"status": "error"}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))