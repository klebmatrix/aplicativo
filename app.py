import os, secrets, string, psycopg2, datetime
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Busca a chave no Render usando nome em minúsculo
# Se não estiver configurado no Render, o acesso será negado (sem senha padrão)
admin_key = os.environ.get('admin_key')

def get_db_connection():
    url = os.environ.get('database_url') or os.environ.get('DATABASE_URL')
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
    <title>SISTEMA</title>
    <style>
        body { font-family: sans-serif; text-align: center; padding: 20px; text-transform: lowercase; }
        .container { max-width: 500px; margin: auto; border: 1px solid #000; padding: 20px; }
        input { width: 90%; padding: 10px; margin: 10px 0; border: 1px solid #000; text-transform: lowercase; }
        button { width: 95%; padding: 10px; background: #000; color: #fff; cursor: pointer; text-transform: lowercase; }
        table { width: 100%; margin-top: 20px; border-collapse: collapse; }
        td { border: 1px solid #000; padding: 8px; }
    </style>
</head>
<body>
    <div class="container">
        {% if tipo == 'admin' %}
            <h2>painel admin</h2>
            <input type="password" id="key" placeholder="chave de acesso">
            <button onclick="listar()">entrar</button>
            <div id="painel" style="display:none; margin-top:20px;">
                <input type="text" id="n" placeholder="nome empresa">
                <input type="text" id="p" placeholder="pin (6-8 digitos)" maxlength="8">
                <button onclick="cadastrar()">salvar cliente</button>
                <div id="lista"></div>
            </div>
        {% else %}
            <h2>login</h2>
            <input type="password" id="pin" placeholder="digite seu pin">
            <button onclick="entrar()">acessar</button>
            <div id="dash" style="display:none; margin-top:20px;">
                <h3 id="cli_nome"></h3>
                <p>uso: <b id="uso"></b> / <b id="total"></b></p>
                <input type="text" id="obs" placeholder="equipamento">
                <button onclick="gerar()">gerar chave</button>
                <div id="hist"></div>
            </div>
        {% endif %}
    </div>

    <script>
    async function listar() {
        const k = document.getElementById('key').value.toLowerCase();
        const res = await fetch('/admin/listar?key=' + k);
        if(!res.ok) return alert("acesso negado");
        document.getElementById('painel').style.display = 'block';
        const dados = await res.json();
        let h = "<table>";
        dados.forEach(c => { h += `<tr><td>${c.n}</td><td>${c.p}</td><td>${c.u}/${c.l}</td></tr>`; });
        document.getElementById('lista').innerHTML = h + "</table>";
    }

    async function cadastrar() {
        const k = document.getElementById('key').value.toLowerCase();
        const n = document.getElementById('n').value.toLowerCase();
        const p = document.getElementById('p').value;
        if(p.length < 6) return alert("pin muito curto");
        await fetch('/admin/cadastrar', {
            method:'POST', headers:{'Content-Type':'application/json'},
            body: JSON.stringify({key:k, n:n, p:p})
        });
        listar();
    }

    async function entrar() {
        const p = document.getElementById('pin').value;
        const res = await fetch('/v1/cliente/dados?pin=' + p);
        if(!res.ok) return alert("pin invalido");
        const d = await res.json();
        document.getElementById('dash').style.display='block';
        document.getElementById('cli_nome').innerText = d.empresa;
        document.getElementById('uso').innerText = d.usadas;
        document.getElementById('total').innerText = d.limite;
        let h = "";
        d.hist.reverse().forEach(t => { h += `<div style="border-bottom:1px solid #000; padding:5px;">${t.toLowerCase()}</div>`; });
        document.getElementById('hist').innerHTML = h;
    }

    async function gerar() {
        const res = await fetch('/v1/cliente/gerar', {
            method:'POST', headers:{'Content-Type':'application/json'},
            body: JSON.stringify({pin:document.getElementById('pin').value, obs:document.getElementById('obs').value.toLowerCase()})
        });
        if(res.ok) entrar(); else alert("erro");
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
    key_input = request.args.get('key', '').lower()
    # Verifica se a chave existe no Render e se bate com o que foi digitado
    if not admin_key_env or key_input != admin_key_env.lower():
        return "negado", 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT nome_empresa, pin_hash, acessos, limite FROM clientes")
    r = cur.fetchall(); cur.close(); conn.close()
    return jsonify([{"n": x[0], "p": x[1], "u": x[2], "l": x[3]} for x in r])

@app.route('/admin/cadastrar', methods=['POST'])
def add_adm():
    d = request.json
    key_input = d.get('key', '').lower()
    if not admin_key_env or key_input != admin_key_env.lower():
        return "negado", 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("INSERT INTO clientes (nome_empresa, pin_hash) VALUES (%s, %s)", (d['n'], d['p']))
    conn.commit(); cur.close(); conn.close()
    return "ok"

@app.route('/v1/cliente/dados')
def get_cli():
    pin = request.args.get('pin')
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT nome_empresa, acessos, limite, historico_chaves FROM clientes WHERE pin_hash = %s", (pin,))
    c = cur.fetchone(); cur.close(); conn.close()
    if c: return jsonify({"empresa": c[0], "usadas": c[1], "limite": c[2], "hist": c[3]})
    return "erro", 401

@app.route('/v1/cliente/gerar', methods=['POST'])
def gen_key():
    d = request.json
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT acessos, limite FROM clientes WHERE pin_hash = %s", (d['pin'],))
    c = cur.fetchone()
    if c and c[0] < c[1]:
        nk = ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(15))
        reg = f"{datetime.datetime.now().strftime('%d/%m')} | {d.get('obs','').lower()} | {nk}"
        cur.execute("UPDATE clientes SET acessos=acessos+1, historico_chaves=array_append(historico_chaves, %s) WHERE pin_hash=%s", (reg, d['pin']))
        conn.commit(); cur.close(); conn.close()
        return "ok"
    return "erro", 403

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))