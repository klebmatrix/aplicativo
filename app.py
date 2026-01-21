import os, secrets, string, psycopg2, datetime
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- BUSCA NO RENDER COM PROTEÇÃO CONTRA ESPAÇOS ---
def get_admin_key():
    key = os.environ.get('ADMIN_KEY')
    return key.strip() if key else None

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
                historico_chaves TEXT[] DEFAULT '{}',
                ativo BOOLEAN DEFAULT TRUE
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
        .container { max-width: 900px; margin: auto; border: 1px solid #ddd; padding: 20px; border-radius: 10px; }
        input { padding: 12px; margin: 5px; border: 1px solid #ccc; border-radius: 5px; }
        button { padding: 10px 15px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; color: white; }
        .btn-black { background: black; color: white; width: 100%; margin-top: 10px; }
        .btn-blue { background: #2563eb; }
        .btn-red { background: #dc2626; }
        .btn-green { background: #16a34a; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #ddd; padding: 10px; text-align: center; }
        .print-only { display: none; }
        @media print { .no-print { display: none !important; } .print-only { display: block !important; border: 2px solid black; padding: 40px; text-align: center; } }
    </style>
</head>
<body>
    <div class="container no-print">
        {% if tipo == 'admin' %}
            <h1>PAINEL ADMIN</h1>
            <input type="password" id="mestre" placeholder="Chave ADMIN_KEY do Render">
            <button class="btn-blue" onclick="listar()">LOGAR NO SISTEMA</button>
            <div id="lista_admin" style="margin-top:20px;"></div>
        {% else %}
            <div id="login_area">
                <h1>LOGIN CLIENTE</h1>
                <input type="password" id="pin" placeholder="Sua Senha" maxlength="8" style="width:100%; box-sizing:border-box;">
                <button class="btn-black" onclick="entrar()">ENTRAR</button>
            </div>
            <div id="dashboard" style="display:none;">
                <h2 id="emp_nome"></h2>
                <p>Saldo: <b id="uso"></b> / <b id="total"></b></p>
                <input type="text" id="obs" placeholder="Referência" style="width:60%">
                <button class="btn-green" onclick="gerar()">GERAR CHAVE</button>
                <div id="lista_historico" style="margin-top:20px;"></div>
            </div>
        {% endif %}
    </div>
    <div id="cert_print" class="print-only"></div>

    <script>
    async function listar() {
        const k = document.getElementById('mestre').value.trim();
        const res = await fetch('/admin/listar?key=' + k);
        if(!res.ok) return alert("ERRO: A chave que você digitou não bate com a do Render!");
        const dados = await res.json();
        let h = "<h3>Cadastrar Novo</h3><input type='text' id='n' placeholder='Empresa'><input type='text' id='p' placeholder='Senha (6-8)' maxlength='8'><input type='number' id='l' value='100'><button class='btn-green' onclick='cadastrar()'>SALVAR</button><hr>";
        h += "<table><tr><th>Empresa</th><th>Senha</th><th>Uso</th><th>Ações</th></tr>";
        dados.forEach(c => {
            h += `<tr><td>${c.n}</td><td>${c.p}</td><td>${c.u}/${c.l}</td><td><button class='btn-red' onclick='del("${c.p}")'>X</button></td></tr>`;
        });
        document.getElementById('lista_admin').innerHTML = h + "</table>";
    }

    async function cadastrar() {
        const p = document.getElementById('p').value;
        if(p.length < 6 || p.length > 8) return alert("Senha do cliente deve ter 6 a 8 dígitos!");
        await fetch('/admin/cadastrar', {
            method:'POST', headers:{'Content-Type':'application/json'},
            body: JSON.stringify({key:document.getElementById('mestre').value.trim(), n:document.getElementById('n').value, p:p, l:document.getElementById('l').value})
        });
        listar();
    }

    async function del(p) {
        if(confirm("Excluir?")) {
            await fetch('/admin/deletar', {method:'DELETE', headers:{'Content-Type':'application/json'}, body:JSON.stringify({key:document.getElementById('mestre').value.trim(), pin:p})});
            listar();
        }
    }

    async function entrar() {
        const p = document.getElementById('pin').value;
        const res = await fetch('/v1/cliente/dados?pin=' + p);
        if(!res.ok) return alert("Senha Inválida!");
        const d = await res.json();
        document.getElementById('login_area').style.display='none';
        document.getElementById('dashboard').style.display='block';
        document.getElementById('emp_nome').innerText = d.empresa;
        document.getElementById('uso').innerText = d.usadas;
        document.getElementById('total').innerText = d.limite;
        let h = "";
        d.hist.reverse().forEach(t => {
            const pt = t.split(' | ');
            h += `<div style="border:1px solid #eee; padding:5px; margin-top:5px;"><b>${pt[1]}</b> - ${pt[2]}</div>`;
        });
        document.getElementById('lista_historico').innerHTML = h;
    }

    async function gerar() {
        const res = await fetch('/v1/cliente/gerar', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({pin:document.getElementById('pin').value, obs:document.getElementById('obs').value})});
        if(res.ok) entrar(); else alert("Erro ou sem créditos!");
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
    real_key = get_admin_key()
    user_key = request.args.get('key', '').strip()
    if not real_key or user_key != real_key:
        print(f"LOGIN FALHOU: Recebido '{user_key}', Esperado '{real_key}'") # Aparece nos logs do Render
        return jsonify([]), 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT nome_empresa, pin_hash, acessos, limite FROM clientes")
    r = cur.fetchall(); cur.close(); conn.close()
    return jsonify([{"n": x[0], "p": x[1], "u": x[2], "l": x[3]} for x in r])

@app.route('/admin/cadastrar', methods=['POST'])
def add_adm():
    d = request.json
    if d.get('key', '').strip() != get_admin_key(): return jsonify({"e":403}), 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("INSERT INTO clientes (nome_empresa, pin_hash, limite) VALUES (%s, %s, %s)", (d['n'], d['p'], d['l']))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"ok": True})

@app.route('/admin/deletar', methods=['DELETE'])
def del_adm():
    d = request.json
    if d.get('key', '').strip() != get_admin_key(): return jsonify({"e":403}), 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("DELETE FROM clientes WHERE pin_hash = %s", (d['pin'],))
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
        reg = f"{datetime.datetime.now().strftime('%d/%m/%Y')} | {d['obs'].upper()} | {nk}"
        cur.execute("UPDATE clientes SET acessos=acessos+1, historico_chaves=array_append(historico_chaves, %s) WHERE pin_hash=%s", (reg, d['pin']))
        conn.commit(); cur.close(); conn.close()
        return jsonify({"ok": True})
    cur.close(); conn.close(); return jsonify({"e": "Erro"}), 403

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))