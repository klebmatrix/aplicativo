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
    <title>KEYQUANTUM | Chaves de Alta Segurança</title>
    <style>
        body { background: #0b1120; color: white; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; text-align: center; padding: 20px; }
        .container { background: #1e293b; padding: 30px; border-radius: 20px; display: inline-block; width: 95%; max-width: 650px; border: 1px solid #334155; box-shadow: 0 15px 35px rgba(0,0,0,0.6); }
        h1 { color: #38bdf8; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 30px; }
        input { padding: 14px; margin: 10px 0; background: #0f172a; border: 1px solid #334155; color: white; border-radius: 8px; width: 85%; font-size: 1rem; }
        button { padding: 12px 25px; background: #0284c7; border: none; color: white; cursor: pointer; border-radius: 8px; font-weight: bold; transition: 0.3s; }
        button:hover { background: #0ea5e9; transform: translateY(-2px); }
        .btn-main { background: #22c55e; width: 90%; font-size: 1.2rem; margin-top: 20px; box-shadow: 0 4px 15px rgba(34, 197, 94, 0.3); }
        .card { background: #0f172a; padding: 25px; border-radius: 15px; text-align: left; margin-top: 25px; border-top: 4px solid #38bdf8; }
        .key-display { background: #ffffff; color: #0f172a; padding: 18px; font-family: 'Courier New', monospace; border-radius: 8px; margin: 20px 0; word-break: break-all; font-weight: bold; text-align: center; font-size: 1.2rem; border: 2px solid #38bdf8; }
        .hist-item { background: #1e293b; padding: 12px; margin-top: 10px; border-radius: 8px; font-size: 11px; border: 1px solid #334155; display: flex; justify-content: space-between; align-items: center; }
        .copy-btn { background: #334155; padding: 6px 12px; font-size: 10px; border-radius: 5px; text-transform: uppercase; }
        table { width: 100%; margin-top: 20px; border-collapse: collapse; font-size: 13px; }
        th, td { border: 1px solid #334155; padding: 12px; text-align: left; }
        .btn-del { background: #ef4444; padding: 6px 10px; }
    </style>
</head>
<body>
    <div class="container">
        {% if tipo == 'admin' %}
            <h2 style="color:#38bdf8">ADMINISTRAÇÃO | KEYQUANTUM</h2>
            <input type="password" id="mestre" placeholder="Sua Chave Mestre">
            <button onclick="listar()">CARREGAR SISTEMA</button>
            <hr style="border:0; border-top:1px solid #334155; margin:30px 0;">
            <h3>CADASTRAR NOVO CLIENTE</h3>
            <input type="text" id="n" placeholder="Nome da Empresa">
            <input type="text" id="p" placeholder="PIN de 6 dígitos">
            <input type="number" id="l" placeholder="Total de Créditos" value="10">
            <button onclick="add()" style="background:#22c55e; width: 85%;">ATIVAR CLIENTE</button>
            <div id="lista_admin"></div>
        {% else %}
            <h1>KEYQUANTUM</h1>
            <div id="login_area">
                <p style="color: #94a3b8;">Sistema de Geração de Chaves de 30 Dígitos</p>
                <input type="password" id="pin" placeholder="DIGITE SEU PIN">
                <button onclick="entrar_painel()" style="width:85%; margin-top:10px;">ACESSAR PAINEL</button>
            </div>
            <div id="cliente_dashboard" style="display:none;">
                <div class="card">
                    <h2 id="msg_boas_vindas" style="margin-top:0; color:#38bdf8; font-size: 1.2rem;"></h2>
                    <p>Saldo de Chaves: <b id="uso" style="color:#22c55e">0</b> / <b id="total">0</b></p>
                    <button class="btn-main" onclick="gerar_chave()">GERAR NOVA CHAVE QUANTUM</button>
                    <div id="area_chave_nova"></div>
                    <h4 style="margin-top:30px; color:#94a3b8; border-bottom: 1px solid #334155; padding-bottom: 5px;">HISTÓRICO DE GERAÇÕES:</h4>
                    <div id="historico_lista"></div>
                </div>
            </div>
        {% endif %}
    </div>

    <script>
    let pin_atual = "";

    async function entrar_painel() {
        pin_atual = document.getElementById('pin').value;
        const res = await fetch('/v1/cliente/dados?pin=' + pin_atual);
        if(res.ok) { await atualizar_dados_cliente(); } else { alert("PIN de acesso incorreto!"); }
    }

    async function atualizar_dados_cliente() {
        const res = await fetch('/v1/cliente/dados?pin=' + pin_atual);
        const d = await res.json();
        document.getElementById('login_area').style.display = 'none';
        document.getElementById('cliente_dashboard').style.display = 'block';
        document.getElementById('msg_boas_vindas').innerText = "Portal do Cliente: " + d.empresa;
        document.getElementById('uso').innerText = d.usadas;
        document.getElementById('total').innerText = d.limite;
        
        let histHtml = "";
        d.hist.reverse().forEach(h => {
            const so_chave = h.split(' - ')[1];
            histHtml += `<div class="hist-item">
                <span>${h}</span>
                <button class="copy-btn" onclick="copiar_texto('${so_chave}')">Copiar</button>
            </div>`;
        });
        document.getElementById('historico_lista').innerHTML = histHtml;
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
                <div class="key-display">${d.key}</div>
                <button onclick="copiar_texto('${d.key}')" style="background:#0ea5e9; width:100%; border-radius: 8px;">COPIAR CHAVE GERADA</button>
            `;
            atualizar_dados_cliente();
        } else { alert("Você não possui mais créditos!"); }
    }

    function copiar_texto(t) {
        navigator.clipboard.writeText(t);
        alert("Copiado!");
    }

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
        let html = "<table><tr><th>Cliente</th><th>PIN</th><th>Uso/Limite</th><th>Ação</th></tr>";
        dados.forEach(c => { 
            html += `<tr><td>${c.n}</td><td>${c.p}</td><td>${c.u}/${c.l}</td>
            <td><button class="btn-del" onclick="apagar('${c.p}')">X</button></td></tr>`; 
        });
        document.getElementById('lista_admin').innerHTML = html + "</table>";
    }

    async function apagar(p) {
        if(!confirm("Deseja remover este acesso?")) return;
        await fetch('/admin/deletar', {method: 'DELETE', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({key: document.getElementById('mestre').value, pin: p})});
        listar();
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
        cur.execute("UPDATE clientes SET acessos=acessos+1, historico_chaves=array_append(historico_chaves, %s) WHERE pin_hash=%s", (f"{datetime.now().strftime('%d/%m %H:%M')} - {nk}", pin))
        conn.commit(); cur.close(); conn.close()
        return jsonify({"key": nk})
    cur.close(); conn.close()
    return jsonify({"erro": "Full"}), 403

@app.route('/admin/cadastrar', methods=['POST'])
def add():
    d = request.json
    if not ADMIN_KEY or d.get('key') != ADMIN_KEY: return jsonify({"erro": "Negado"}), 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("INSERT INTO clientes (nome_empresa, pin_hash, limite, historico_chaves) VALUES (%s, %s, %s, '{}')", (d['n'], d['p'], d['l']))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"msg": "Cliente Ativado com Sucesso!"})

@app.route('/admin/listar')
def list_all():
    if not ADMIN_KEY or request.args.get('key') != ADMIN_KEY: return jsonify([]), 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT nome_empresa, pin_hash, COALESCE(acessos,0), COALESCE(limite,0) FROM clientes ORDER BY id DESC")
    r = cur.fetchall(); cur.close(); conn.close()
    return jsonify([{"n": x[0], "p": x[1], "u": x[2], "l": x[3]} for x in r])

@app.route('/admin/deletar', methods=['DELETE'])
def deletar_cli():
    d = request.json
    if not ADMIN_KEY or d.get('key') != ADMIN_KEY: return jsonify({"erro": "Erro"}), 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("DELETE FROM clientes WHERE pin_hash = %s", (d.get('pin'),))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"msg": "Removido"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))