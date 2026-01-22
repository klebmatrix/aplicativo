import os, secrets, string, psycopg2, datetime
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# BUSCA A CHAVE DO AMBIENTE RENDER
ADMIN_KEY = os.environ.get('ADMIN_KEY')

def get_db_connection():
    url = os.environ.get('DATABASE_URL')
    if not url: return None
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    try:
        return psycopg2.connect(url, sslmode='require')
    except:
        return None

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

HTML_SISTEMA = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>SISTEMA QUANTUM</title>
    <style>
        body { font-family: sans-serif; text-align: center; padding: 20px; }
        .box { max-width: 500px; margin: auto; border: 1px solid #000; padding: 20px; border-radius: 10px; }
        input { width: 90%; padding: 10px; margin: 10px 0; border: 1px solid #000; }
        button { width: 95%; padding: 10px; background: #000; color: #fff; cursor: pointer; font-weight: bold; }
        table { width: 100%; margin-top: 20px; border-collapse: collapse; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
    </style>
</head>
<body>
    <div class="box">
        {% if tipo == 'admin' %}
            <h2>PAINEL MASTER</h2>
            <input type="password" id="mestre" placeholder="Chave ADMIN_KEY do Render">
            <button onclick="listar()">ENTRAR</button>
            <div id="painel" style="display:none; margin-top:20px;">
                <hr>
                <input type="text" id="n" placeholder="Nome Empresa">
                <input type="text" id="p" placeholder="PIN (6-8 dig)" maxlength="8">
                <button style="background: green;" onclick="cadastrar()">CADASTRAR</button>
                <div id="lista"></div>
            </div>
        {% else %}
            <h2>LOGIN CLIENTE</h2>
            <input type="password" id="pin" placeholder="Seu PIN">
            <button onclick="entrar()">ENTRAR</button>
            <div id="dash" style="display:none; margin-top:20px;">
                <h3 id="c_nome"></h3>
                <p>Uso: <b id="uso"></b> / <b id="total"></b></p>
                <input type="text" id="obs" placeholder="Equipamento">
                <button style="background: green;" onclick="gerar()">GERAR CHAVE</button>
                <div id="hist"></div>
            </div>
        {% endif %}
    </div>

    <script>
    async function listar() {
        const k = document.getElementById('mestre').value;
        const res = await fetch('/admin/listar?key=' + k);
        if(!res.ok) return alert("Acesso Negado!");
        document.getElementById('painel').style.display = 'block';
        const dados = await res.json();
        let h = "<table><tr><th>Empresa</th><th>PIN</th><th>Uso</th></tr>";
        dados.forEach(c => { h += `<tr><td>${c.n}</td><td>${c.p}</td><td>${c.u}/${c.l}</td></tr>`; });
        document.getElementById('lista').innerHTML = h + "</table>";
    }

    async function cadastrar() {
        const k = document.getElementById('mestre').value;
        const n = document.getElementById('n').value;
        const p = document.getElementById('p').value;
        if(p.length < 6) return alert("PIN curto!");
        await fetch('/admin/cadastrar', {
            method:'POST', headers:{'Content-Type':'application/json'},
            body: JSON.stringify({key:k, n:n, p:p})
        });
        listar();
    }

    async function entrar() {
        const p = document.getElementById('pin').value;
        const res = await fetch('/v1/cliente/dados?pin=' + p);
        if(!res.ok) return alert("PIN Inválido");
        const d = await res.json();
        document.getElementById('dash').style.display='block';
        document.getElementById('c_nome').innerText = d.empresa;
        document.getElementById('uso').innerText = d.usadas;
        document.getElementById('total').innerText = d.limite;
        let h = "";
        d.hist.reverse().forEach(t => { h += `<div style="border-bottom:1px solid #eee; padding:5px;">${t}</div>`; });
        document.getElementById('hist').innerHTML = h;
    }

    async function gerar() {
        const res = await fetch('/v1/cliente/gerar', {
            method:'POST', headers:{'Content-Type':'application/json'},
            body: JSON.stringify({pin:document.getElementById('pin').value, obs:document.getElementById('obs').value})
        });
        if(res.ok) entrar(); else alert("Erro!");
    }
    </script>
</body>
</html>
"""

@app.route('/')
def home(): return render_template_string(HTML_SISTEMA, tipo='cliente')

@app.route('/painel-secreto-kleber')
def admin_page(): return render_template_string(HTML_SISTEMA, tipo='admin')

@app.route('/admin/listar')
def list_adm():
    if request.args.get('key') != ADMIN_KEY: return jsonify([]), 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT nome_empresa, pin_hash, acessos, limite FROM clientes")
    r = cur.fetchall(); cur.close(); conn.close()
    return jsonify([{"n": x[0], "p": x[1], "u": x[2], "l": x[3]} for x in r])

@app.route('/admin/cadastrar', methods=['POST'])
def add_adm():
    d = request.json
    if d.get('key') != ADMIN_KEY: return "Erro", 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("INSERT INTO clientes (nome_empresa, pin_hash) VALUES (%s, %s)", (d['n'], d['p']))
    conn.commit(); cur.close(); conn.close()
    return "OK"

@app.route('/v1/cliente/dados')
def get_cli():
    pin = request.args.get('pin')
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT nome_empresa, acessos, limite, historico_chaves FROM clientes WHERE pin_hash = %s", (pin,))
    c = cur.fetchone(); cur.close(); conn.close()
    if c: return jsonify({"empresa": c[0], "usadas": c[1], "limite": c[2], "hist": c[3]})
    return jsonify({"e": 401}), 401

@app.route('/v1/cliente/gerar', methods=['POST'])
def gen_key():
    d = request.json
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT acessos, limite FROM clientes WHERE pin_hash = %s", (d['pin'],))
    c = cur.fetchone()
    if c and c[0] < c[1]:
        nk = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(15))
        reg = f"{datetime.datetime.now().strftime('%d/%m')} | {d.get('obs','').upper()} | {nk}"
        cur.execute("UPDATE clientes SET acessos=acessos+1, historico_chaves=array_append(historico_chaves, %s) WHERE pin_hash=%s", (reg, d['pin']))
        conn.commit(); cur.close(); conn.close()
        return jsonify({"ok": True})
    return "Erro", 403

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))