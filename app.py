import os, secrets, string, psycopg2, datetime
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- CONFIGURAÇÃO MANUAL (PARA NÃO TER ERRO) ---
CHAVE_MESTRE_FIXA = "QUANTUM2026" 

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
        body { background: white; color: black; font-family: sans-serif; padding: 20px; text-align: center; }
        .container { max-width: 600px; margin: auto; border: 2px solid #000; padding: 30px; border-radius: 15px; }
        input { width: 100%; padding: 15px; margin: 10px 0; border: 1px solid #000; font-size: 16px; box-sizing: border-box; }
        button { width: 100%; padding: 15px; border: none; background: black; color: white; font-weight: bold; cursor: pointer; font-size: 16px; }
        .btn-green { background: #1a7f37 !important; margin-top: 10px; }
        .btn-red { background: #d73a49 !important; width: auto; padding: 5px 10px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #ddd; padding: 10px; text-align: left; color: black; }
    </style>
</head>
<body>
    <div class="container">
        {% if tipo == 'admin' %}
            <h2>PAINEL MASTER QUANTUM</h2>
            <p style="color: red; font-weight: bold;">A SENHA É: QUANTUM2026</p>
            <input type="password" id="mestre" placeholder="Digite QUANTUM2026">
            <button onclick="listar()">ENTRAR NO PAINEL</button>
            
            <div id="painel_admin" style="display:none; margin-top:30px;">
                <hr>
                <h3>CADASTRAR CLIENTE</h3>
                <input type="text" id="n" placeholder="NOME DA EMPRESA">
                <input type="text" id="p" placeholder="SENHA DO CLIENTE (6-8 dig)" maxlength="8">
                <input type="number" id="l" value="100">
                <button class="btn-green" onclick="cadastrar()">SALVAR CLIENTE</button>
                <div id="lista_dados"></div>
            </div>
        {% else %}
            <h1>QUANTUM LOGIN</h1>
            <input type="password" id="pin" placeholder="SUA SENHA" maxlength="8">
            <button onclick="entrar()">ENTRAR</button>
            <div id="dash" style="display:none; margin-top:20px;">
                <h2 id="cli_nome"></h2>
                <p>SALDO: <b id="uso"></b> / <b id="total"></b></p>
                <input type="text" id="obs" placeholder="EQUIPAMENTO">
                <button class="btn-green" onclick="gerar()">GERAR CHAVE</button>
                <div id="hist" style="text-align:left;"></div>
            </div>
        {% endif %}
    </div>

    <script>
    async function listar() {
        const k = document.getElementById('mestre').value;
        const res = await fetch('/admin/listar?key=' + k);
        if(!res.ok) {
            alert("ERRO! Tente digitar exatamente: QUANTUM2026");
            return;
        }
        const dados = await res.json();
        document.getElementById('painel_admin').style.display = 'block';
        let h = "<table><tr><th>Empresa</th><th>Senha</th><th>Uso</th><th>X</th></tr>";
        dados.forEach(c => {
            h += `<tr><td>${c.n}</td><td>${c.p}</td><td>${c.u}/${c.l}</td><td><button class='btn-red' onclick='excluir("${c.p}")'>X</button></td></tr>`;
        });
        document.getElementById('lista_dados').innerHTML = h + "</table>";
    }

    async function cadastrar() {
        const p = document.getElementById('p').value;
        if(p.length < 6) return alert("A senha do cliente deve ter no mínimo 6 dígitos!");
        const k = document.getElementById('mestre').value;
        await fetch('/admin/cadastrar', {
            method:'POST', headers:{'Content-Type':'application/json'},
            body: JSON.stringify({key:k, n:document.getElementById('n').value, p:p, l:document.getElementById('l').value})
        });
        listar();
    }

    async function excluir(pin) {
        if(confirm("Excluir?")) {
            const k = document.getElementById('mestre').value;
            await fetch('/admin/deletar', {method:'DELETE', headers:{'Content-Type':'application/json'}, body:JSON.stringify({key:k, pin:pin})});
            listar();
        }
    }

    async function entrar() {
        const p = document.getElementById('pin').value;
        const res = await fetch('/v1/cliente/dados?pin=' + p);
        if(!res.ok) return alert("SENHA INVÁLIDA!");
        const d = await res.json();
        document.querySelector('h1').style.display='none';
        document.getElementById('pin').style.display='none';
        document.querySelector('button').style.display='none';
        document.getElementById('dash').style.display='block';
        document.getElementById('cli_nome').innerText = d.empresa;
        document.getElementById('uso').innerText = d.usadas;
        document.getElementById('total').innerText = d.limite;
        let h = "";
        d.hist.reverse().forEach(t => {
            const pt = t.split(' | ');
            h += `<div style="border-bottom:1px solid #eee; padding:10px;"><b>${pt[1]}</b><br>${pt[2]}</div>`;
        });
        document.getElementById('hist').innerHTML = h;
    }

    async function gerar() {
        const res = await fetch('/v1/cliente/gerar', {
            method:'POST', headers:{'Content-Type':'application/json'},
            body: JSON.stringify({pin:document.getElementById('pin').value, obs:document.getElementById('obs').value})
        });
        if(res.ok) entrar(); else alert("SEM CRÉDITOS!");
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
    key_digitada = request.args.get('key', '')
    if key_digitada != CHAVE_MESTRE_FIXA: return jsonify([]), 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT nome_empresa, pin_hash, acessos, limite FROM clientes")
    r = cur.fetchall(); cur.close(); conn.close()
    return jsonify([{"n": x[0], "p": x[1], "u": x[2], "l": x[3]} for x in r])

@app.route('/admin/cadastrar', methods=['POST'])
def add_adm():
    d = request.json
    if d.get('key') != CHAVE_MESTRE_FIXA: return jsonify({"e":403}), 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("INSERT INTO clientes (nome_empresa, pin_hash, limite) VALUES (%s, %s, %s)", (d['n'], d['p'], d['l']))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"ok": True})

@app.route('/admin/deletar', methods=['DELETE'])
def del_adm():
    d = request.json
    if d.get('key') != CHAVE_MESTRE_FIXA: return jsonify({"e":403}), 403
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
        nk = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(20))
        reg = f"{datetime.datetime.now().strftime('%d/%m/%Y')} | {d['obs'].upper()} | {nk}"
        cur.execute("UPDATE clientes SET acessos=acessos+1, historico_chaves=array_append(historico_chaves, %s) WHERE pin_hash=%s", (reg, d['pin']))
        conn.commit(); cur.close(); conn.close()
        return jsonify({"ok": True})
    cur.close(); conn.close(); return jsonify({"e": "Erro"}), 403

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))