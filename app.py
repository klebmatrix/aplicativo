import os
import psycopg2
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

# FUNÇÃO QUE VAI LIMPAR E CRIAR TUDO DO ZERO
def setup_banco():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # Cria a tabela se ela não existir
        cur.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id SERIAL PRIMARY KEY,
                nome_empresa TEXT NOT NULL,
                pin_hash TEXT UNIQUE NOT NULL,
                ultimo_acesso TIMESTAMP
            )
        ''')
        # Insere um cliente de teste para a gente saber se funciona
        cur.execute("INSERT INTO clientes (nome_empresa, pin_hash) VALUES ('TESTE_SISTEMA', '111111') ON CONFLICT DO NOTHING")
        conn.commit()
        cur.close(); conn.close()
        print("BANCO CONFIGURADO E CLIENTE TESTE CRIADO!")
    except Exception as e:
        print(f"ERRO NO SETUP: {e}")

setup_banco()

# O MESMO HTML QUE VOCÊ JÁ TINHA (PÁGINA ADMIN E LOGIN)
HTML_BASE = """
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>KLEBMATRIX</title>
<style>
    body { background: #0f172a; color: white; font-family: sans-serif; text-align: center; padding: 50px; }
    .box { background: #1e293b; padding: 20px; border-radius: 10px; display: inline-block; min-width: 300px; border: 1px solid #334155; }
    input { padding: 10px; margin: 10px; width: 80%; background: #0f172a; color: white; border: 1px solid #334155; }
    button { padding: 10px 20px; cursor: pointer; background: #0284c7; border: none; color: white; font-weight: bold; }
    table { width: 100%; margin-top: 20px; border-collapse: collapse; }
    td, th { border: 1px solid #334155; padding: 10px; }
</style>
</head>
<body>
    {% if admin %}
        <div class="box">
            <h2>PAINEL ADMIN</h2>
            <input type="password" id="k" placeholder="Chave Mestre">
            <hr>
            <input type="text" id="n" placeholder="Nome">
            <input type="text" id="p" placeholder="PIN">
            <button onclick="add()">CADASTRAR</button>
            <button onclick="ver()" style="background:#38bdf8">LISTAR</button>
            <table><tbody id="lista"></tbody></table>
        </div>
    {% else %}
        <div class="box">
            <h1>KLEBMATRIX</h1>
            <input type="password" id="pin" placeholder="PIN">
            <button onclick="login()">ENTRAR</button>
            <div id="msg"></div>
        </div>
    {% endif %}

    <script>
    async function add() {
        const res = await fetch('/admin/cadastrar', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({admin_key: document.getElementById('k').value, nome: document.getElementById('n').value, pin: document.getElementById('p').value})
        });
        const d = await res.json(); alert(d.msg || d.erro); ver();
    }
    async function ver() {
        const k = document.getElementById('k').value;
        const res = await fetch('/admin/listar?key=' + k);
        const dados = await res.json();
        const l = document.getElementById('lista');
        l.innerHTML = "<tr><th>Nome</th><th>PIN</th></tr>";
        dados.forEach(c => { l.innerHTML += `<tr><td>${c.nome}</td><td>${c.pin}</td></tr>`; });
    }
    async function login() {
        const res = await fetch('/v1/quantum-key', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({pin: document.getElementById('pin').value})
        });
        const d = await res.json();
        document.getElementById('msg').innerHTML = res.ok ? "LIBERADO: " + d.key : "NEGADO";
    }
    </script>
</body>
</html>
"""

@app.route('/')
def home(): return render_template_string(HTML_BASE, admin=False)

@app.route('/painel-secreto-kleber')
def admin(): return render_template_string(HTML_BASE, admin=True)

@app.route('/admin/cadastrar', methods=['POST'])
def c():
    d = request.json
    if d.get('admin_key') != ADMIN_KEY: return jsonify({"erro":"Erro"}), 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("INSERT INTO clientes (nome_empresa, pin_hash) VALUES (%s,%s)", (d['nome'], d['pin']))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"msg":"OK"})

@app.route('/admin/listar')
def l():
    if request.args.get('key') != ADMIN_KEY: return jsonify([])
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT nome_empresa, pin_hash FROM clientes")
    r = cur.fetchall()
    cur.close(); conn.close()
    return jsonify([{"nome":x[0], "pin":x[1]} for x in r])

@app.route('/v1/quantum-key', methods=['POST'])
def v():
    p = request.json.get('pin')
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT nome_empresa FROM clientes WHERE pin_hash=%s", (p,))
    f = cur.fetchone()
    cur.close(); conn.close()
    if f: return jsonify({"key":"OK", "empresa":f[0]})
    return jsonify({"erro":"!"}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))