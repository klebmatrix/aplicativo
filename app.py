import os, secrets, string, psycopg2, datetime
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

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
                empresa TEXT NOT NULL,
                pin_hash TEXT UNIQUE NOT NULL,
                limite INTEGER DEFAULT 100,
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
        body { background: white; color: black; font-family: sans-serif; padding: 20px; }
        .container { max-width: 650px; margin: auto; border: 1px solid #ddd; padding: 25px; border-radius: 10px; }
        input { width: 100%; padding: 12px; margin: 8px 0; box-sizing: border-box; border: 1px solid #ccc; border-radius: 5px; }
        .btn { padding: 12px; border: none; font-weight: bold; cursor: pointer; border-radius: 5px; margin-top: 5px; }
        .btn-black { background: black; color: white; width: 100%; }
        .btn-red { background: #d9534f; color: white; padding: 5px 10px; font-size: 12px; }
        .card { border-bottom: 1px solid #eee; padding: 10px; display: flex; justify-content: space-between; align-items: center; }
        table { width: 100%; margin-top: 25px; border-collapse: collapse; font-size: 14px; }
        th, td { border-bottom: 1px solid #ddd; padding: 12px; text-align: left; }
        @media print { .no-print { display: none; } .print-area { display: block !important; } }
        .print-area { display: none; text-align: center; border: 12px double #000; padding: 60px; }
    </style>
</head>
<body>
    <div class="container no-print">
        {% if admin %}
            <h2>PAINEL DE GESTÃO - ADMIN</h2>
            <input type="text" id="n" placeholder="Nome da Empresa">
            <input type="text" id="p" placeholder="Senha de Acesso (6 a 8 car.)" minlength="6" maxlength="8">
            <input type="number" id="l" placeholder="Qtd. de Créditos" value="100">
            <button class="btn btn-black" onclick="cadastrar()">CADASTRAR E ADICIONAR CLIENTE</button>
            <div id="lista_clientes_sessao" style="margin-top:30px;">
                <h3>Clientes Ativos</h3>
                <div id="tabela_clientes">Carregando...</div>
            </div>
        {% else %}
            <div id="login">
                <h2>LOGIN DO CLIENTE</h2>
                <input type="password" id="pass" placeholder="Senha (6 a 8 caracteres)" minlength="6" maxlength="8">
                <button class="btn btn-black" onclick="entrar()">ACESSAR</button>
            </div>
            <div id="dash" style="display:none;">
                <h3 id="cli_nome" style="color:#2563eb;"></h3>
                <p><b>Créditos:</b> <span id="cli_limite"></span></p>
                <input type="text" id="prod" placeholder="Referência do Produto">
                <button class="btn btn-black" onclick="gerar()">GERAR AUTENTICAÇÃO</button>
                <div id="lista_hist" style="margin-top:20px;"></div>
            </div>
        {% endif %}
    </div>
    <div id="cert" class="print-area"></div>
    <script>
    async function cadastrar() {
        const p = document.getElementById('p').value;
        if(p.length < 6 || p.length > 8) return alert("Senha deve ter de 6 a 8 caracteres!");
        await fetch('/admin/cadastrar', {
            method:'POST', headers:{'Content-Type':'application/json'},
            body: JSON.stringify({empresa: document.getElementById('n').value, pin: p, limite: document.getElementById('l').value})
        });
        alert("Cliente Salvo!"); listar();
    }
    async function listar() {
        const res = await fetch('/admin/listar');
        const dados = await res.json();
        let h = "<table><tr><th>Empresa</th><th>Senha</th><th>Créditos</th><th>Ação</th></tr>";
        dados.forEach(c => {
            h += `<tr><td>${c.empresa}</td><td>${c.pin_hash}</td><td>${c.limite}</td>
            <td><button class="btn btn-red" onclick="excluir('${c.pin_hash}')">EXCLUIR</button></td></tr>`;
        });
        document.getElementById('tabela_clientes').innerHTML = h + "</table>";
    }
    async function excluir(pin) {
        if(confirm("Excluir cliente?")) {
            await fetch('/admin/excluir', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({pin: pin})});
            listar();
        }
    }
    async function entrar() {
        const pass = document.getElementById('pass').value;
        const res = await fetch('/v1/cliente/dados?pin=' + pass);
        if(!res.ok) return alert("Senha Incorreta!");
        const d = await res.json();
        document.getElementById('login').style.display='none';
        document.getElementById('dash').style.display='block';
        document.getElementById('cli_nome').innerText = d.empresa;
        document.getElementById('cli_limite').innerText = d.limite;
        let h = "";
        d.hist.reverse().forEach(t => {
            const p = t.split(' | ');
            h += `<div class="card"><span><b>${p[1]}</b><br><small>${p[0]}</small></span><button onclick="imprimir('${t}')">IMPRIMIR</button></div>`;
        });
        document.getElementById('lista_hist').innerHTML = h;
    }
    async function gerar() {
        const pass = document.getElementById('pass').value;
        const res = await fetch('/v1/cliente/gerar', {
            method:'POST', headers:{'Content-Type':'application/json'},
            body: JSON.stringify({pin: pass, obs: document.getElementById('prod').value})
        });
        if(res.status === 403) alert("Sem créditos!");
        else entrar();
    }
    function imprimir(texto) {
        const p = texto.split(' | ');
        document.getElementById('cert').innerHTML = `<h1>CERTIFICADO</h1><br><h2>${p[1]}</h2><br><p>CHAVE:</p><h3>${p[2]}</h3><p>${p[0]}</p>`;
        window.print();
    }
    if(window.location.pathname.includes('admin') || window.location.pathname.includes('painel-secreto-kleber')) {
        setTimeout(listar, 500);
    }
    </script>
</body>
</html>
"""

@app.route('/')
def home(): return render_template_string(HTML_SISTEMA, admin=False)

@app.route('/painel-secreto-kleber')
@app.route('/admin')
def admin_pg(): return render_template_string(HTML_SISTEMA, admin=True)

@app.route('/admin/listar')
def listar_api():
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT empresa, pin_hash, limite FROM clientes")
    rows = cur.fetchall()
    cur.close(); conn.close()
    return jsonify([{"empresa": r[0], "pin_hash": r[1], "limite": r[2]} for r in rows])

@app.route('/admin/excluir', methods=['POST'])
def excluir_api():
    d = request.json
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("DELETE FROM clientes WHERE pin_hash = %s", (d['pin'],))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"ok": True})

@app.route('/v1/cliente/dados')
def dados():
    pin = request.args.get('pin')
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT empresa, historico_chaves, limite FROM clientes WHERE pin_hash = %s", (pin,))
    res = cur.fetchone()
    cur.close(); conn.close()
    return jsonify({"empresa": res[0], "hist": res[1], "limite": res[2]}) if res else (jsonify({}), 404)

@app.route('/v1/cliente/gerar', methods=['POST'])
def gerar_api():
    d = request.json
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT limite FROM clientes WHERE pin_hash = %s", (d['pin'],))
    row = cur.fetchone()
    if not row or row[0] <= 0:
        cur.close(); conn.close()
        return jsonify({"erro": "sem creditos"}), 403
    ch = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(12))
    info = f"{datetime.datetime.now().strftime('%d/%m/%Y')} | {d['obs'].upper()} | {ch}"
    cur.execute("UPDATE clientes SET historico_chaves = array_append(historico_chaves, %s), limite = limite - 1 WHERE pin_hash = %s", (info, d['pin']))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"ok": True})

@app.route('/admin/cadastrar', methods=['POST'])
def add_api():
    d = request.json
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("INSERT INTO clientes (empresa, pin_hash, limite, historico_chaves) VALUES (%s, %s, %s, %s)", (d['empresa'], d['pin'], d.get('limite', 100), []))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"ok": True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))