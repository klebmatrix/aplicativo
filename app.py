import os
import secrets
import string
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

def generate_quantum_key(length=30):
    chars = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))

HTML_SISTEMA = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>KLEBMATRIX | QUANTUM DASHBOARD</title>
    <style>
        body { background: #0b1120; color: white; font-family: sans-serif; text-align: center; padding: 20px; }
        .container { background: #1e293b; padding: 25px; border-radius: 15px; display: inline-block; width: 95%; max-width: 600px; border: 1px solid #334155; }
        input { padding: 12px; margin: 8px; background: #0f172a; border: 1px solid #334155; color: white; border-radius: 6px; width: 80%; font-size: 1.1rem; }
        button { padding: 12px 24px; background: #0284c7; border: none; color: white; cursor: pointer; border-radius: 6px; font-weight: bold; transition: 0.3s; }
        .btn-main { background: #22c55e; width: 100%; font-size: 1.1rem; margin-top: 15px; }
        .btn-main:hover { background: #16a34a; }
        .card { background: #0f172a; padding: 20px; border-radius: 10px; text-align: left; margin-top: 20px; border: 1px solid #38bdf8; }
        .key-display { background: #fff; color: #000; padding: 15px; font-family: monospace; border-radius: 6px; margin: 15px 0; word-break: break-all; font-weight: bold; text-align: center; }
        .hist-item { background: #1e293b; padding: 10px; margin-top: 8px; border-radius: 5px; font-size: 12px; border: 1px solid #334155; display: flex; justify-content: space-between; align-items: center; }
        .copy-small { background: #334155; padding: 5px; font-size: 10px; border-radius: 3px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="container">
        {% if tipo == 'admin' %}
            <h2>PAINEL MASTER</h2>
            <input type="password" id="mestre" placeholder="Chave Mestre">
            <button onclick="listar()">LISTAR CLIENTES</button>
            <hr style="border:0; border-top:1px solid #334155; margin:20px 0;">
            <input type="text" id="n" placeholder="Nome Empresa">
            <input type="text" id="p" placeholder="PIN">
            <input type="number" id="l" placeholder="Créditos" value="10">
            <button onclick="add()" style="background:#22c55e">CADASTRAR</button>
            <div id="lista_admin"></div>
        {% else %}
            <h1 style="color:#38bdf8">KLEBMATRIX</h1>
            <div id="login_area">
                <input type="password" id="pin" placeholder="INSIRA SEU PIN">
                <button onclick="entrar_painel()" style="width:85%">ENTRAR NO SISTEMA</button>
            </div>
            <div id="cliente_dashboard" style="display:none;">
                <div class="card">
                    <h2 id="msg_boas_vindas" style="margin-top:0; color:#38bdf8"></h2>
                    <p>Créditos Usados: <b id="uso">0</b> / Total: <b id="total">0</b></p>
                    <button class="btn-main" onclick="gerar_chave()">GERAR NOVA CHAVE QUANTUM</button>
                    <div id="area_chave_nova"></div>
                    <h4 style="margin-top:25px; color:#94a3b8">MEU HISTÓRICO DE CHAVES:</h4>
                    <div id="historico_lista"></div>
                </div>
            </div>
        {% endif %}
    </div>

    <script>
    let pin_atual = "";

    async function entrar_painel() {
        pin_atual = document.getElementById('pin').value;
        await atualizar_dados_cliente();
    }

    async function atualizar_dados_cliente() {
        const res = await fetch('/v1/cliente/dados?pin=' + pin_atual);
        const d = await res.json();
        if(res.ok) {
            document.getElementById('login_area').style.display = 'none';
            document.getElementById('cliente_dashboard').style.display = 'block';
            document.getElementById('msg_boas_vindas').innerText = "Olá, " + d.empresa;
            document.getElementById('uso').innerText = d.usadas;
            document.getElementById('total').innerText = d.limite;
            
            let histHtml = "";
            d.hist.reverse().forEach(h => {
                histHtml += `<div class="hist-item">
                    <span>${h}</span>
                    <span class="copy-small" onclick="copiar_texto('${h}')">COPIAR</span>
                </div>`;
            });
            document.getElementById('historico_lista').innerHTML = histHtml;
        } else { alert("PIN Inválido!"); }
    }

    async function gerar_chave() {
        const res = await fetch('/v1/cliente/gerar', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ pin: pin_atual })
        });
        const d = await res.json();
        if(res.ok) {
            document.getElementById('area_chave_nova').innerHTML = `
                <div class="key-display" id="key_val">${d.key}</div>
                <button onclick="copiar_texto('${d.key}')" style="background:#0ea5e9; width:100%">COPIAR CHAVE AGORA</button>
            `;
            atualizar_dados_cliente();
        } else { alert(d.erro || "Sem créditos!"); }
    }

    function copiar_texto(t) {
        navigator.clipboard.writeText(t.split(' - ')[1] || t);
        alert("Copiado para a área de transferência!");
    }

    // Funções Admin
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
        const dados = await res.json();
        let html = "<table style='width:100%; margin-top:20px; font-size:12px;'><tr><th>Empresa</th><th>PIN</th><th>Uso</th></tr>";
        dados.forEach(c => { html += `<tr><td>${c.n}</td><td>${c.p}</td><td>${c.u}/${c.l}</td></tr>`; });
        document.getElementById('lista_admin').innerHTML = html + "</table>";
    }
    </script>
</body>
</html>
"""

@app.route('/')
def home(): return render_template_string(HTML_SISTEMA, tipo='login')

@app.route('/painel-secreto-kleber')
def admin_page(): return render_template_string(HTML_SISTEMA, tipo='admin')

@app.route('/v1/cliente/dados')
def get_dados():
    pin = request.args.get('pin')
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT nome_empresa, acessos, limite, historico_chaves FROM clientes WHERE pin_hash = %s", (pin,))
    c = cur.fetchone(); cur.close(); conn.close()
    if c: return jsonify({"empresa": c[0], "usadas": c[1], "limite": c[2], "hist": c[3]})
    return jsonify({"erro": "n"}), 404

@app.route('/v1/cliente/gerar', methods=['POST'])
def gerar():
    pin = request.json.get('pin')
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT acessos, limite FROM clientes WHERE pin_hash = %s", (pin,))
    c = cur.fetchone()
    if c and c[0] < c[1]:
        nk = generate_quantum_key(30)
        timestamp = datetime.now().strftime('%d/%m %H:%M')
        cur.execute("UPDATE clientes SET acessos=acessos+1, historico_chaves=array_append(historico_chaves, %s) WHERE pin_hash=%s", (f"{timestamp} - {nk}", pin))
        conn.commit(); cur.close(); conn.close()
        return jsonify({"key": nk})
    cur.close(); conn.close()
    return jsonify({"erro": "Limite de créditos atingido!"}), 403

@app.route('/admin/cadastrar', methods=['POST'])
def add():
    d = request.json
    if not ADMIN_KEY or d.get('key') != ADMIN_KEY: return jsonify({"erro": "Erro"}), 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("INSERT INTO clientes (nome_empresa, pin_hash, limite, historico_chaves) VALUES (%s, %s, %s, '{}')", (d['n'], d['p'], d['l']))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"msg": "OK"})

@app.route('/admin/listar')
def list_all():
    if not ADMIN_KEY or request.args.get('key') != ADMIN_KEY: return jsonify([]), 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT nome_empresa, pin_hash, COALESCE(acessos,0), COALESCE(limite,0) FROM clientes")
    r = cur.fetchall(); cur.close(); conn.close()
    return jsonify([{"n": x[0], "p": x[1], "u": x[2], "l": x[3]} for x in r])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))