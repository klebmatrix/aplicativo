import os, secrets, string, psycopg2, datetime
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# SENHA MESTRE DEFINIDA DIRETAMENTE
CHAVE_MESTRE = "QUANTUM2026"

def get_db_connection():
    url = os.environ.get('DATABASE_URL')
    if not url: 
        print("ERRO: DATABASE_URL não encontrada!")
        return None
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    try:
        conn = psycopg2.connect(url, sslmode='require')
        return conn
    except Exception as e:
        print(f"Erro de conexão com banco: {e}")
        return None

@app.before_request
def init_db():
    try:
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
    except Exception as e:
        print(f"Erro ao inicializar banco: {e}")

HTML_BASE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QUANTUM MASTER</title>
    <style>
        body { background: white; color: black; font-family: sans-serif; padding: 20px; text-align: center; }
        .box { max-width: 500px; margin: auto; border: 2px solid black; padding: 20px; border-radius: 10px; }
        input { width: 90%; padding: 12px; margin: 10px 0; border: 1px solid #000; font-size: 16px; }
        button { width: 95%; padding: 12px; background: black; color: white; border: none; cursor: pointer; font-weight: bold; }
        table { width: 100%; margin-top: 20px; border-collapse: collapse; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; font-size: 14px; }
        .admin-area { display: none; margin-top: 20px; text-align: left; }
    </style>
</head>
<body>
    <div class="box">
        {% if tipo == 'admin' %}
            <h2>PAINEL ADMIN</h2>
            <input type="password" id="key" placeholder="Senha Master">
            <button onclick="logarAdmin()">ENTRAR</button>
            <div id="area" class="admin-area">
                <hr>
                <h4>Cadastrar Cliente</h4>
                <input type="text" id="n" placeholder="Nome da Empresa">
                <input type="text" id="p" placeholder="PIN (6 a 8 dígitos)" maxlength="8">
                <input type="number" id="l" value="100">
                <button style="background: green;" onclick="cadastrar()">SALVAR</button>
                <div id="lista"></div>
            </div>
        {% else %}
            <h2>LOGIN CLIENTE</h2>
            <input type="password" id="pin_cli" placeholder="Digite seu PIN">
            <button onclick="logarCliente()">ACESSAR</button>
            <div id="dash" style="display:none; margin-top:20px; text-align:left;">
                <h3 id="c_nome"></h3>
                <p>Saldo: <b id="c_uso"></b> / <b id="c_total"></b></p>
                <input type="text" id="obs" placeholder="Equipamento">
                <button style="background: green;" onclick="gerarChave()">GERAR CHAVE QUANTICA</button>
                <div id="chaves" style="margin-top:10px;"></div>
            </div>
        {% endif %}
    </div>

    <script>
    async function logarAdmin() {
        const k = document.getElementById('key').value;
        const r = await fetch('/admin/listar?key=' + k);
        if(!r.ok) return alert("Senha incorreta!");
        document.getElementById('area').style.display = 'block';
        const dados = await r.json();
        let h = "<table><tr><th>Empresa</th><th>PIN</th><th>Uso</th></tr>";
        dados.forEach(c => { h += `<tr><td>${c.n}</td><td>${c.p}</td><td>${c.u}/${c.l}</td></tr>`; });
        document.getElementById('lista').innerHTML = h + "</table>";
    }

    async function cadastrar() {
        const k = document.getElementById('key').value;
        const body = {key:k, n:document.getElementById('n').value, p:document.getElementById('p').value, l:document.getElementById('l').value};
        await fetch('/admin/cadastrar', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(body)});
        logarAdmin();
    }

    async function logarCliente() {
        const p = document.getElementById('pin_cli').value;
        const r = await fetch('/v1/cliente/dados?pin=' + p);
        if(!r.ok) return alert("PIN Inválido!");
        const d = await r.json();
        document.getElementById('dash').style.display='block';
        document.getElementById('c_nome').innerText = d.empresa;
        document.getElementById('c_uso').innerText = d.usadas;
        document.getElementById('c_total').innerText = d.limite;
        let h = "";
        d.hist.reverse().forEach(t => { h += `<div style="border-bottom:1px solid #eee; padding:5px;">${t}</div>`; });
        document.getElementById('chaves').innerHTML = h;
    }

    async function gerarChave() {
        const p = document.getElementById('pin_cli').value;
        const res = await fetch('/v1/cliente/gerar', {
            method:'POST', headers:{'Content-Type':'application/json'},
            body: JSON.stringify({pin:p, obs:document.getElementById('obs').value})
        });
        if(res.ok) logarCliente(); else alert("Erro ou Sem Saldo!");
    }
    </script>
</body>
</html>
"""

@app.route('/')
def home(): return render_template_string(HTML_BASE, tipo='cliente')

@app.route('/painel-secreto-kleber')
def admin_page(): return render_template_string(HTML_BASE, tipo='admin')

@app.route('/admin/listar')
def list_adm():
    try:
        if request.args.get('key') != CHAVE_MESTRE: return jsonify([]), 403
        conn = get_db_connection()
        if not conn: return jsonify({"erro": "Banco offline"}), 500
        cur = conn.cursor()
        cur.execute("SELECT nome_empresa, pin_hash, acessos, limite FROM clientes")
        r = cur.fetchall(); cur.close(); conn.close()
        return jsonify([{"n": x[0], "p": x[1], "u": x[2], "l": x[3]} for x in r])
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/admin/cadastrar', methods=['POST'])
def add_adm():
    d = request.json
    if d.get('key') != CHAVE_MESTRE: return jsonify({"e":403}), 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("INSERT INTO clientes (nome_empresa, pin_hash, limite) VALUES (%s, %s, %s)", (d['n'], d['p'], d['l']))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"ok": True})

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
    return jsonify({"e": "Erro"}), 403

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))