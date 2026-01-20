import os
import secrets
import psycopg2
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

ADMIN_KEY = os.environ.get('ADMIN_KEY')

def get_db_connection():
    url = os.environ.get('DATABASE_URL')
    if url and url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return psycopg2.connect(url, sslmode='require')

def force_repair():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # Cria a tabela base se não existir
        cur.execute("CREATE TABLE IF NOT EXISTS clientes (id SERIAL PRIMARY KEY, nome_empresa TEXT, pin_hash TEXT UNIQUE)")
        
        # Adiciona cada coluna nova individualmente para não dar erro se já existir
        colunas = [
            "ALTER TABLE clientes ADD COLUMN IF NOT EXISTS acessos INTEGER DEFAULT 0",
            "ALTER TABLE clientes ADD COLUMN IF NOT EXISTS limite INTEGER DEFAULT 10",
            "ALTER TABLE clientes ADD COLUMN IF NOT EXISTS ultimo_acesso TIMESTAMP",
            "ALTER TABLE clientes ADD COLUMN IF NOT EXISTS historico_chaves TEXT[] DEFAULT '{}'"
        ]
        
        for col in colunas:
            try:
                cur.execute(col)
                conn.commit()
            except:
                conn.rollback()
        
        cur.close(); conn.close()
        print("BANCO DESTRAVADO E ATUALIZADO!")
    except Exception as e:
        print(f"Erro crítico no reset: {e}")

# Executa o conserto ao iniciar
force_repair()

HTML_SISTEMA = """
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>KLEBMATRIX | GESTÃO</title>
<style>
    body { background: #0b1120; color: white; font-family: sans-serif; text-align: center; padding: 20px; }
    .container { background: #1e293b; padding: 20px; border-radius: 10px; display: inline-block; width: 90%; max-width: 700px; border: 1px solid #334155; }
    input { padding: 10px; margin: 5px; background: #0f172a; border: 1px solid #334155; color: white; border-radius: 5px; }
    button { padding: 10px 20px; background: #0284c7; border: none; color: white; cursor: pointer; border-radius: 5px; font-weight: bold; }
    table { width: 100%; margin-top: 20px; border-collapse: collapse; }
    th, td { border: 1px solid #334155; padding: 8px; font-size: 13px; }
</style>
</head>
<body>
    <div class="container">
        {% if tipo == 'admin' %}
            <h2>🛠 PAINEL MASTER</h2>
            <input type="password" id="mestre" placeholder="Chave Mestre">
            <button onclick="listar()">LISTAR / ATUALIZAR</button>
            <hr>
            <input type="text" id="n" placeholder="Cliente">
            <input type="text" id="p" placeholder="PIN">
            <input type="number" id="l" placeholder="Créditos" value="10" style="width:60px">
            <button onclick="add()" style="background:#22c55e">CADASTRAR</button>
            <table>
                <thead><tr><th>Cliente</th><th>PIN</th><th>Uso/Total</th><th>Ação</th></tr></thead>
                <tbody id="lista"></tbody>
            </table>
        {% else %}
            <h1>KLEBMATRIX</h1>
            <input type="password" id="pin_acesso" placeholder="DIGITE SEU PIN">
            <button onclick="entrar()">GERAR CHAVE</button>
            <div id="res" style="margin-top:20px;"></div>
        {% endif %}
    </div>

    <script>
    async function add() {
        const res = await fetch('/admin/cadastrar', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({key: document.getElementById('mestre').value, n: document.getElementById('n').value, p: document.getElementById('p').value, l: document.getElementById('l').value})
        });
        const d = await res.json(); alert(d.msg || d.erro); listar();
    }
    async function listar() {
        const k = document.getElementById('mestre').value;
        const res = await fetch('/admin/listar?key=' + k);
        if(!res.ok) { alert("Chave incorreta ou erro no servidor"); return; }
        const dados = await res.json();
        const l = document.getElementById('lista');
        l.innerHTML = "";
        dados.forEach(c => {
            l.innerHTML += `<tr><td>${c.n}</td><td>${c.p}</td><td>${c.u}/${c.l}</td><td><button onclick="del('${c.p}')" style="background:red; padding:3px 7px;">X</button></td></tr>`;
        });
    }
    async function del(p) {
        if(!confirm("Remover?")) return;
        await fetch('/admin/deletar', {method: 'DELETE', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({key: document.getElementById('mestre').value, pin: p})});
        listar();
    }
    async function entrar() {
        const r = document.getElementById('res');
        r.innerHTML = "Verificando...";
        const res = await fetch('/v1/quantum-key', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ pin: document.getElementById('pin_acesso').value })
        });
        const d = await res.json();
        if(res.ok) {
            r.innerHTML = `<div style="background:#0f172a; padding:15px; border-radius:10px; border-left:5px solid #22c55e">
                <h3>Olá, ${d.empresa}!</h3>
                <p>Créditos: ${d.usadas}/${d.limite}</p>
                <div style="background:#fff; color:#000; padding:10px; font-weight:bold; font-size:1.2rem;">${d.key}</div>
                <p style="font-size:10px; margin-top:10px;">HISTÓRICO: ${d.hist.join(' | ')}</p>
            </div>`;
        } else { r.innerHTML = "<b style='color:red'>ACESSO NEGADO</b>"; }
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
    if not ADMIN_KEY or d.get('key') != ADMIN_KEY: return jsonify({"erro": "Chave Errada"}), 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("INSERT INTO clientes (nome_empresa, pin_hash, limite) VALUES (%s, %s, %s)", (d['n'], d['p'], d['l']))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"msg": "OK"})

@app.route('/admin/listar')
def list_all():
    if not ADMIN_KEY or request.args.get('key') != ADMIN_KEY: return jsonify([]), 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT nome_empresa, pin_hash, COALESCE(acessos,0), COALESCE(limite,0) FROM clientes")
    r = cur.fetchall()
    cur.close(); conn.close()
    return jsonify([{"n": x[0], "p": x[1], "u": x[2], "l": x[3]} for x in r])

@app.route('/admin/deletar', methods=['DELETE'])
def deletar():
    d = request.json
    if d.get('key') != ADMIN_KEY: return jsonify({"erro": "Erro"}), 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("DELETE FROM clientes WHERE pin_hash = %s", (d.get('pin'),))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"msg": "Removido"})

@app.route('/v1/quantum-key', methods=['POST'])
def login():
    p = request.json.get('pin', '').strip()
    try:
        conn = get_db_connection(); cur = conn.cursor()
        cur.execute("SELECT nome_empresa, acessos, limite, historico_chaves FROM clientes WHERE pin_hash = %s", (p,))
        c = cur.fetchone()
        if c and c[1] < c[2]:
            nk = secrets.token_hex(8).upper()
            cur.execute("UPDATE clientes SET acessos=acessos+1, historico_chaves=array_append(historico_chaves, %s) WHERE pin_hash=%s RETURNING historico_chaves", (nk, p))
            h = cur.fetchone()[0]
            conn.commit(); cur.close(); conn.close()
            return jsonify({"empresa":c[0], "usadas":c[1]+1, "limite":c[2], "key":nk, "hist":h[-3:]})
        cur.close(); conn.close()
    except: pass
    return jsonify({"status": "error"}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))