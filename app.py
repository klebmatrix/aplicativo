import os
import secrets
import string
import psycopg2
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Busca a chave (minúsculo ou maiúsculo)
ADMIN_KEY_ENV = os.environ.get('admin_key') or os.environ.get('ADMIN_KEY')

def get_db_connection():
    url = os.environ.get('DATABASE_URL')
    if url and url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    try:
        return psycopg2.connect(url, sslmode='require')
    except Exception as e:
        print(f"Erro ao conectar no banco: {e}")
        return None

# Garante que a tabela exista ao iniciar
@app.before_request
def init_db():
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id SERIAL PRIMARY KEY,
                nome_empresa TEXT NOT NULL,
                pin_hash TEXT UNIQUE NOT NULL,
                limite INTEGER DEFAULT 100,
                acessos INTEGER DEFAULT 0,
                historico_chaves TEXT[] DEFAULT '{}'
            );
        ''')
        conn.commit()
        cur.close(); conn.close()

def generate_quantum_key(length=30):
    chars = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))

# --- O SEU HTML (MANTIDO EXATAMENTE COMO VOCÊ ENVIOU) ---
HTML_SISTEMA = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>KEYQUANTUM | SISTEMA OFICIAL 2026</title>
    <style>
        :root { --blue: #38bdf8; --dark: #0b1120; --card: #1e293b; --input: #0f172a; }
        body { background: var(--dark); color: white; font-family: sans-serif; padding: 20px; }
        .container { max-width: 850px; margin: auto; background: var(--card); padding: 30px; border-radius: 20px; border: 1px solid #334155; }
        h1 { color: var(--blue); text-align: center; }
        input { padding: 12px; margin: 10px 0; background: var(--input); border: 1px solid #334155; color: white; border-radius: 8px; width: 90%; }
        button { padding: 12px 20px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; transition: 0.3s; color: white; }
        .btn-green { background: #22c55e; width: 100%; font-size: 1.1rem; }
        .btn-blue { background: #0284c7; }
        .btn-red { background: #ef4444; padding: 5px 10px; }
        .btn-gray { background: #475569; font-size: 12px; }
        .hist-item { background: var(--input); padding: 15px; margin-top: 10px; border-radius: 10px; display: flex; align-items: center; border: 2px solid transparent; }
        .hist-item.selected { border-color: var(--blue); background: #162e45; }
        .checkbox-item { width: 22px; height: 22px; margin-right: 15px; cursor: pointer; }
        .dashboard-header { display: flex; justify-content: space-between; align-items: center; background: var(--input); padding: 15px; border-radius: 12px; margin: 20px 0; }
        table { width: 100%; margin-top: 20px; border-collapse: collapse; background: var(--input); }
        th, td { padding: 12px; border: 1px solid #334155; text-align: left; }
        @media print {
            body { background: white !important; color: black !important; }
            button, input, .no-print, h1, .btn-green { display: none !important; }
            .hist-item:not(.selected) { display: none !important; }
            .hist-item { color: black !important; border: 1px solid #000 !important; }
        }
    </style>
</head>
<body>
    <div class="container">
        {% if tipo == 'admin' %}
            <h1>PAINEL ADMIN</h1>
            <input type="password" id="mestre" placeholder="Chave Mestra">
            <button class="btn-blue" onclick="listar()">LISTAR CLIENTES</button>
            <hr style="margin:25px 0; border:1px solid #334155;">
            <input type="text" id="n" placeholder="Empresa">
            <input type="text" id="p" placeholder="PIN de 6 dígitos" maxlength="6">
            <input type="number" id="l" placeholder="Créditos" value="10">
            <button class="btn-green" onclick="add()">ATIVAR NOVO CLIENTE</button>
            <div id="lista_admin"></div>
        {% else %}
            <div id="login_area">
                <h1>SISTEMA QUANTUM</h1>
                <input type="text" id="pin" placeholder="PIN DE 6 DÍGITOS" maxlength="6">
                <button class="btn-blue" style="width: 95%;" onclick="entrar()">ENTRAR NO PAINEL</button>
            </div>
            <div id="dashboard" style="display:none;">
                <h2 id="emp_nome" style="color: var(--blue);"></h2>
                <div class="dashboard-header">
                    <span>Uso: <b id="uso">0</b> / <b id="total">0</b></span>
                    <div>
                        <button class="btn-gray" onclick="window.print()">🖨️ IMPRIMIR</button>
                        <button class="btn-blue" style="font-size:12px;" onclick="exportarExcel()">📊 EXCEL</button>
                    </div>
                </div>
                <input type="text" id="obs" placeholder="Observação/Lote">
                <button class="btn-green" onclick="gerar()">GERAR NOVA CHAVE</button>
                <div id="lista_historico"></div>
            </div>
        {% endif %}
    </div>

    <script>
        let pinAtivo = "";
        async function entrar() {
            pinAtivo = document.getElementById('pin').value;
            const res = await fetch('/v1/cliente/dados?pin=' + pinAtivo);
            if(res.ok) { 
                document.getElementById('login_area').style.display='none';
                document.getElementById('dashboard').style.display='block';
                atualizarUI(); 
            } else { alert("PIN Inválido!"); }
        }
        async function atualizarUI() {
            const res = await fetch('/v1/cliente/dados?pin=' + pinAtivo);
            const d = await res.json();
            document.getElementById('emp_nome').innerText = d.empresa;
            document.getElementById('uso').innerText = d.usadas;
            document.getElementById('total').innerText = d.limite;
            let html = "";
            d.hist.reverse().forEach((txt, i) => {
                html += `<div class="hist-item" id="row-${i}">
                    <input type="checkbox" class="checkbox-item" onchange="this.parentElement.classList.toggle('selected')" data-info="${txt}">
                    <span style="flex-grow:1">${txt}</span>
                </div>`;
            });
            document.getElementById('lista_historico').innerHTML = html;
        }
        async function gerar() {
            await fetch('/v1/cliente/gerar', {
                method: 'POST', headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ pin: pinAtivo, obs: document.getElementById('obs').value })
            });
            atualizarUI();
        }
        async function add() {
            await fetch('/admin/cadastrar', {
                method: 'POST', headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({key: document.getElementById('mestre').value, n: document.getElementById('n').value, p: document.getElementById('p').value, l: document.getElementById('l').value})
            });
            listar();
        }
        async function listar() {
            const res = await fetch('/admin/listar?key=' + document.getElementById('mestre').value);
            const dados = await res.json();
            let h = "<table>";
            dados.forEach(c => { h += `<tr><td>${c.n}</td><td>${c.p}</td><td>${c.u}/${c.l}</td></tr>`; });
            document.getElementById('lista_admin').innerHTML = h + "</table>";
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
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT nome_empresa, acessos, limite, historico_chaves FROM clientes WHERE pin_hash = %s", (pin,))
    c = cur.fetchone(); cur.close(); conn.close()
    if c: return jsonify({"empresa": c[0], "usadas": c[1], "limite": c[2], "hist": c[3]})
    return jsonify({"erro": "n"}), 404

@app.route('/v1/cliente/gerar', methods=['POST'])
def gerar_api():
    d = request.json
    pin = d.get('pin')
    obs = d.get('obs', 'GERAL').upper()
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT acessos, limite FROM clientes WHERE pin_hash = %s", (pin,))
    c = cur.fetchone()
    if c and c[0] < c[1]:
        nk = generate_quantum_key(30)
        reg = f"{datetime.now().strftime('%d/%m/%Y %H:%M')} | {obs} | {nk}"
        cur.execute("UPDATE clientes SET acessos=acessos+1, historico_chaves=array_append(historico_chaves, %s) WHERE pin_hash=%s", (reg, pin))
        conn.commit(); cur.close(); conn.close()
        return jsonify({"key": nk})
    return jsonify({"erro": "Full"}), 403

@app.route('/admin/cadastrar', methods=['POST'])
def add_cli():
    d = request.json
    if not ADMIN_KEY_ENV or d.get('key') != ADMIN_KEY_ENV: return jsonify({"erro": "Erro"}), 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("INSERT INTO clientes (nome_empresa, pin_hash, limite) VALUES (%s, %s, %s)", (d['n'], d['p'], d['l']))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"msg": "OK"})

@app.route('/admin/listar')
def list_all():
    if not ADMIN_KEY_ENV or request.args.get('key') != ADMIN_KEY_ENV: return jsonify([]), 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT nome_empresa, pin_hash, acessos, limite FROM clientes ORDER BY id DESC")
    r = cur.fetchall(); cur.close(); conn.close()
    return jsonify([{"n": x[0], "p": x[1], "u": x[2], "l": x[3]} for x in r])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))