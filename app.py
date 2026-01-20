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

# --- REPARO E ATUALIZAÇÃO DO BANCO ---
def repair_db():
    try:
        conn = get_db_connection(); cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                id SERIAL PRIMARY KEY, 
                nome_empresa TEXT, 
                pin_hash TEXT UNIQUE, 
                acessos INTEGER DEFAULT 0, 
                limite INTEGER DEFAULT 10,
                historico_chaves TEXT[] DEFAULT '{}'
            )
        """)
        conn.commit(); cur.close(); conn.close()
    except: pass

repair_db()

HTML_SISTEMA = """
<!DOCTYPE html>
<html lang="pt-br">
<head><meta charset="UTF-8"><title>KLEBMATRIX | Controle</title>
<style>
    body { background: #0b1120; color: white; font-family: sans-serif; display: flex; justify-content: center; padding-top: 20px; }
    .container { background: #1e293b; padding: 25px; border-radius: 15px; width: 800px; border: 1px solid #334155; }
    input, select { padding: 10px; margin: 5px; background: #0f172a; border: 1px solid #334155; color: white; border-radius: 5px; }
    button { padding: 10px 20px; background: #0284c7; border: none; color: white; font-weight: bold; cursor: pointer; border-radius: 5px; }
    .card { background: #0f172a; padding: 15px; border-radius: 10px; margin-top: 10px; border-left: 5px solid #38bdf8; }
    table { width: 100%; margin-top: 20px; border-collapse: collapse; font-size: 13px; }
    th, td { border: 1px solid #334155; padding: 10px; text-align: left; }
    .critico { color: #ef4444; }
    .sucesso { color: #22c55e; }
</style></head>
<body>
    <div class="container">
        {% if tipo == 'admin' %}
            <h2>🛠 GESTÃO DE CRÉDITOS</h2>
            <input type="password" id="mestre" placeholder="Chave Mestre">
            <button onclick="listar()">LISTAR CLIENTES</button>
            <hr style="border-color:#334155">
            <div style="background:#0f172a; padding:15px; border-radius:10px;">
                <input type="text" id="n" placeholder="Empresa">
                <input type="text" id="p" placeholder="PIN">
                <input type="number" id="l" placeholder="Qtd Chaves" value="10" style="width:80px">
                <button onclick="cadastrar()" style="background:#22c55e">CADASTRAR</button>
            </div>
            <table>
                <thead><tr><th>Empresa</th><th>PIN</th><th>Uso/Limite</th><th>Ação</th></tr></thead>
                <tbody id="lista"></tbody>
            </table>
        {% else %}
            <div style="max-width:400px; margin:auto; text-align:center;">
                <h1 style="color: #38bdf8;">KLEBMATRIX</h1>
                <input type="password" id="pin_acesso" placeholder="DIGITE SEU PIN" style="width:90%; font-size:1.2rem;">
                <button onclick="acessar()" style="width:98%; margin-top:15px;">ENTRAR NO PAINEL</button>
                <div id="status"></div>
            </div>
        {% endif %}
    </div>
    <script>
        async function cadastrar() {
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
            const dados = await res.json();
            const corpo = document.getElementById('lista');
            corpo.innerHTML = "";
            dados.forEach(c => {
                corpo.innerHTML += `<tr><td>${c.n}</td><td>${c.p}</td><td>${c.qtd}/${c.limite}</td><td><button style="background:#ef4444" onclick="apagar('${c.p}')">DEL</button></td></tr>`;
            });
        }
        async function apagar(pin) {
            if(!confirm("Excluir?")) return;
            await fetch('/admin/deletar', {method: 'DELETE', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({key: document.getElementById('mestre').value, pin: pin})});
            listar();
        }
        async function acessar() {
            const pin = document.getElementById('pin_acesso').value;
            const res = await fetch('/v1/quantum-key', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ pin: pin })
            });
            const d = await res.json();
            const s = document.getElementById('status');
            if(res.ok) {
                let hist = d.historico.map(h => `<div style="font-family:monospace; font-size:11px; margin-bottom:5px;">${h}</div>`).join("");
                s.innerHTML = `
                    <div class="card">
                        <h3 class="sucesso">Olá, ${d.empresa}!</h3>
                        <p>Você usou <b>${d.usadas}</b> de <b>${d.limite}</b> chaves.</p>
                        <p>Restantes: <b class="${d.restantes < 3 ? 'critico' : 'sucesso'}">${d.restantes}</b></p>
                        <hr style="border-color:#334155">
                        <h4>SUA CHAVE ATUAL:</h4>
                        <div style="background:#fff; color:#000; padding:10px; font-weight:bold; border-radius:5px;">${d.key}</div>
                        <h4 style="margin-top:20px;">HISTÓRICO RECENTE:</h4>
                        ${hist}
                    </div>`;
            } else {
                s.innerHTML = `<p class="critico">PIN INVÁLIDO OU LIMITE ATINGIDO!</p>`;
            }
        }
    </script>
</body></html>
"""

@app.route('/')
def home(): return render_template_string(HTML_SISTEMA, tipo='login')

@app.route('/painel-secreto-kleber')
def admin_page(): return render_template_string(HTML_SISTEMA, tipo='admin')

@app.route('/admin/cadastrar', methods=['POST'])
def add():
    d = request.json
    if not ADMIN_KEY or d.get('key') != ADMIN_KEY: return jsonify({"erro": "Erro"}), 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("INSERT INTO clientes (nome_empresa, pin_hash, limite) VALUES (%s, %s, %s)", (d['n'], d['p'], d['l']))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"msg": "OK"})

@app.route('/admin/listar')
def list_all():
    if not ADMIN_KEY or request.args.get('key') != ADMIN_KEY: return jsonify([]), 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT nome_empresa, pin_hash, acessos, limite FROM clientes")
    rows = cur.fetchall()
    cur.close(); conn.close()
    return jsonify([{"n": r[0], "p": r[1], "qtd": r[2], "limite": r[3]} for r in rows])

@app.route('/admin/deletar', methods=['DELETE'])
def delete_cli():
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
        # Verifica se ainda tem limite
        cur.execute("SELECT nome_empresa, acessos, limite, historico_chaves FROM clientes WHERE pin_hash = %s", (p,))
        cli = cur.fetchone()
        
        if cli and cli[1] < cli[2]:
            nova_chave = secrets.token_hex(8).upper()
            # Atualiza acessos e guarda a chave no histórico (array do Postgres)
            cur.execute("""
                UPDATE clientes 
                SET acessos = acessos + 1, 
                    historico_chaves = array_append(historico_chaves, %s) 
                WHERE pin_hash = %s 
                RETURNING nome_empresa, acessos, limite, historico_chaves
            """, (f"{datetime.now().strftime('%d/%m %H:%M')} - {nova_chave}", p))
            res = cur.fetchone()
            conn.commit(); cur.close(); conn.close()
            
            # Pega as últimas 5 chaves do histórico para mostrar ao cliente
            historico = res[3][-5:] if res[3] else []
            historico.reverse()
            
            return jsonify({
                "empresa": res[0],
                "usadas": res[1],
                "limite": res[2],
                "restantes": res[2] - res[1],
                "key": nova_chave,
                "historico": historico
            })
        cur.close(); conn.close()
    except: pass
    return jsonify({"status": "error"}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))