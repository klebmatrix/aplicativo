import os, secrets, string, psycopg2, datetime
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def get_admin_key():
    # Puxa a chave e remove qualquer espaço acidental que você tenha deixado no Render
    key = os.environ.get('ADMIN_KEY')
    return key.strip() if key else ""

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
        body { background: white; color: black; font-family: sans-serif; padding: 20px; }
        .container { max-width: 800px; margin: auto; border: 1px solid #ddd; padding: 20px; border-radius: 10px; }
        input { width: 100%; padding: 12px; margin: 8px 0; border: 1px solid #ccc; border-radius: 5px; box-sizing: border-box; }
        button { width: 100%; padding: 12px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; }
        .btn-blue { background: #2563eb; color: white; margin-bottom: 20px; }
        .btn-green { background: #16a34a; color: white; }
        .btn-red { background: #dc2626; color: white; width: auto; padding: 5px 10px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border-bottom: 1px solid #eee; padding: 10px; text-align: left; }
    </style>
</head>
<body>
    <div class="container">
        {% if tipo == 'admin' %}
            <h2>PAINEL DE CONTROLE (ADMIN)</h2>
            <p>Digite a chave configurada no Render:</p>
            <input type="password" id="mestre" placeholder="Chave de Ambiente">
            <button class="btn-blue" onclick="listar()">ENTRAR NO PAINEL</button>
            
            <div id="painel_admin" style="display:none;">
                <hr>
                <h3>Cadastrar Novo Cliente</h3>
                <input type="text" id="n" placeholder="Nome da Empresa">
                <input type="text" id="p" placeholder="Senha (6 a 8 dígitos)" maxlength="8">
                <input type="number" id="l" value="100" placeholder="Créditos">
                <button class="btn-green" onclick="cadastrar()">SALVAR CLIENTE</button>
                <div id="lista_dados"></div>
            </div>
        {% else %}
            <div id="login_cliente">
                <h2>LOGIN CLIENTE</h2>
                <input type="password" id="pin" placeholder="Sua Senha" maxlength="8">
                <button style="background:black; color:white;" onclick="entrar()">ACESSAR</button>
            </div>
            <div id="dash" style="display:none;">
                <h2 id="cli_nome"></h2>
                <p>Saldo: <b id="uso"></b> / <b id="total"></b></p>
                <input type="text" id="obs" placeholder="Referência">
                <button style="background:green; color:white;" onclick="gerar()">GERAR CHAVE QUANTICA</button>
                <div id="hist" style="margin-top:20px;"></div>
            </div>
        {% endif %}
    </div>

    <script>
    async function listar() {
        const k = document.getElementById('mestre').value.trim();
        const res = await fetch('/admin/listar?key=' + k);
        
        if (res.status === 403) {
            return alert("A CHAVE NÃO BATE! Verifique se no Render a ADMIN_KEY é igual à que você digitou.");
        }
        
        const dados = await res.json();
        document.getElementById('painel_admin').style.display = 'block';
        let h = "<table><tr><th>Empresa</th><th>Senha</th><th>Créditos</th><th>Ação</th></tr>";
        dados.forEach(c => {
            h += `<tr><td>${c.n}</td><td>${c.p}</td><td>${c.u}/${c.l}</td>
            <td><button class="btn-red" onclick="excluir('${c.p}')">Remover</button></td></tr>`;
        });
        document.getElementById('lista_dados').innerHTML = h + "</table>";
    }

    async function cadastrar() {
        const p = document.getElementById('p').value;
        if(p.length < 6 || p.length > 8) return alert("Senha do cliente deve ter entre 6 e 8 dígitos.");
        const k = document.getElementById('mestre').value.trim();
        await fetch('/admin/cadastrar', {
            method:'POST', headers:{'Content-Type':'application/json'},
            body: JSON.stringify({key:k, n:document.getElementById('n').value, p:p, l:document.getElementById('l').value})
        });
        listar();
    }

    async function excluir(pin) {
        if(confirm("Excluir cliente?")) {
            const k = document.getElementById('mestre').value.trim();
            await fetch('/admin/deletar', {
                method:'DELETE', headers:{'Content-Type':'application/json'},
                body: JSON.stringify({key:k, pin:pin})
            });
            listar();
        }
    }

    async function entrar() {
        const p = document.getElementById('pin').value;
        const res = await fetch('/v1/cliente/dados?pin=' + p);
        if(!res.ok) return alert("Senha incorreta!");
        const d = await res.json();
        document.getElementById('login_cliente').style.display='none';
        document.getElementById('dash').style.display='block';
        document.getElementById('cli_nome').innerText = d.empresa;
        document.getElementById('uso').innerText = d.usadas;
        document.getElementById('total').innerText = d.limite;
        let h = "";
        d.hist.reverse().forEach(t => {
            const pt = t.split(' | ');
            h += `<div style="border:1px solid #eee; padding:10px; margin-top:5px;"><b>${pt[1]}</b><br><small>${pt[2]}</small></div>`;
        });
        document.getElementById('hist').innerHTML = h;
    }

    async function gerar() {
        const p = document.getElementById('pin').value;
        const res = await fetch('/v1/cliente/gerar', {
            method:'POST', headers:{'Content-Type':'application/json'},
            body: JSON.stringify({pin:p, obs:document.getElementById('obs').value})
        });
        if(res.ok) entrar(); else alert("Erro ao gerar!");
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
    # Comparação segura: limpa espaços e ignora se é maiúsculo/minúsculo
    real_key = get_admin_key().lower()
    user_key = request.args.get('key', '').strip().lower()
    
    if not real_key or user_key != real_key:
        return jsonify([]), 403
        
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT nome_empresa, pin_hash, acessos, limite FROM clientes")
    r = cur.fetchall(); cur.close(); conn.close()
    return jsonify([{"n": x[0], "p": x[1], "u": x[2], "l": x[3]} for x in r])

@app.route('/admin/cadastrar', methods=['POST'])
def add_adm():
    d = request.json
    if d.get('key', '').strip().lower() != get_admin_key().lower(): return jsonify({"e":403}), 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("INSERT INTO clientes (nome_empresa, pin_hash, limite) VALUES (%s, %s, %s)", (d['n'], d['p'], d['l']))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"ok": True})

@app.route('/admin/deletar', methods=['DELETE'])
def del_adm():
    d = request.json
    if d.get('key', '').strip().lower() != get_admin_key().lower(): return jsonify({"e":403}), 403
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
        nk = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(25))
        reg = f"{datetime.datetime.now().strftime('%d/%m/%Y')} | {d['obs'].upper()} | {nk}"
        cur.execute("UPDATE clientes SET acessos=acessos+1, historico_chaves=array_append(historico_chaves, %s) WHERE pin_hash=%s", (reg, d['pin']))
        conn.commit(); cur.close(); conn.close()
        return jsonify({"ok": True})
    cur.close(); conn.close(); return jsonify({"e": "Erro"}), 403

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))