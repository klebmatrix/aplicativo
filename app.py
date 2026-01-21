import os, secrets, string, psycopg2
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Busca a senha do Admin das variáveis de ambiente (conforme solicitado)
ADMIN_KEY = os.environ.get('ADMIN_KEY')

def get_db_connection():
    url = os.environ.get('DATABASE_URL')
    if not url:
        return None
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    try:
        # Força conexão segura e imediata
        return psycopg2.connect(url, sslmode='require', connect_timeout=10)
    except:
        return None

def init_db():
    """Garante que a estrutura do banco esteja correta antes de listar ou cadastrar"""
    conn = get_db_connection()
    if not conn: return
    cur = conn.cursor()
    # Cria tabela se não existir
    cur.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id SERIAL PRIMARY KEY,
            nome_empresa TEXT,
            pin_hash TEXT UNIQUE,
            limite INTEGER DEFAULT 0,
            acessos INTEGER DEFAULT 0,
            historico_chaves TEXT[] DEFAULT '{}',
            ativo BOOLEAN DEFAULT TRUE
        )
    """)
    # Força a criação da coluna 'ativo' caso ela falte
    cur.execute("DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='clientes' AND column_name='ativo') THEN ALTER TABLE clientes ADD COLUMN ativo BOOLEAN DEFAULT TRUE; END IF; END $$;")
    conn.commit()
    cur.close(); conn.close()

# Executa a limpeza/ajuste do banco ao iniciar
init_db()

HTML_SISTEMA = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>SISTEMA QUANTUM GESTÃO</title>
    <style>
        :root { --blue: #38bdf8; --dark: #0b1120; --card: #1e293b; --red: #ef4444; --green: #22c55e; }
        body { background: var(--dark); color: white; font-family: sans-serif; padding: 20px; }
        .container { max-width: 950px; margin: auto; background: var(--card); padding: 25px; border-radius: 15px; border: 1px solid #334155; }
        input { padding: 10px; margin: 5px; background: #0f172a; border: 1px solid #334155; color: white; border-radius: 5px; }
        button { padding: 8px 12px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; color: white; margin: 2px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; background: #0f172a; }
        th, td { padding: 12px; border: 1px solid #334155; text-align: center; }
        .status-ativo { color: var(--green); } .status-bloqueado { color: var(--red); }
        .hist-item { background: #0f172a; padding: 12px; margin-top: 8px; border-radius: 8px; display: flex; align-items: center; border: 2px solid transparent; }
        .hist-item.selected { border-color: var(--blue); background: #162e45; }
        .no-print { font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        {% if tipo == 'admin' %}
            <h1>GESTOR DE ACESSOS</h1>
            <input type="password" id="mestre" placeholder="Chave Mestra do Render">
            <button style="background:var(--blue)" onclick="listar()">FORÇAR LISTA DO BANCO</button>
            
            <div style="background:#0f172a; padding:15px; margin-top:20px; border-radius:10px;">
                <h3>Cadastrar Empresa</h3>
                <input type="text" id="n" placeholder="Nome">
                <input type="text" id="p" placeholder="PIN (6 dígitos)" maxlength="6">
                <input type="number" id="l" placeholder="Créditos">
                <button style="background:var(--green)" onclick="add()">SALVAR NO DB</button>
            </div>
            <div id="lista_admin"></div>
        {% else %}
            <div id="login_area">
                <h1>QUANTUM LOGIN</h1>
                <input type="text" id="pin" placeholder="PIN" maxlength="6">
                <button style="background:var(--blue); width:100%" onclick="entrar()">ENTRAR</button>
            </div>
            <div id="dashboard" style="display:none;">
                <h2 id="emp_nome" style="color:var(--blue)"></h2>
                <div style="background:#0f172a; padding:15px; border-radius:10px; margin-bottom:20px; display:flex; justify-content:space-between;">
                    <span>Saldo: <b id="uso"></b> / <b id="total"></b></span>
                    <button style="background:#475569" onclick="window.print()">IMPRIMIR</button>
                </div>
                <input type="text" id="obs" placeholder="Obs/Lote">
                <button style="background:var(--green); width:100%" onclick="gerar()">GERAR CHAVE</button>
                <div id="lista_historico" style="margin-top:20px"></div>
            </div>
        {% endif %}
    </div>

    <script>
    async function listar() {
        const k = document.getElementById('mestre').value;
        const res = await fetch('/admin/listar?key=' + k);
        if(!res.ok) return alert("Erro de Conexão ou Senha Errada!");
        const dados = await res.json();
        let h = "<table><tr><th>Empresa</th><th>PIN</th><th>Saldo</th><th>Status</th><th>Ações</th></tr>";
        dados.forEach(c => {
            h += `<tr><td>${c.n}</td><td>${c.p}</td><td>${c.u}/${c.l}</td>
                <td class="${c.a?'status-ativo':'status-bloqueado'}"><b>${c.a?'ATIVO':'BLOQUEADO'}</b></td>
                <td>
                    <button style="background:var(--blue)" onclick="addCr('${c.p}')">+ Crédito</button>
                    <button style="background:orange" onclick="altSt('${c.p}',${c.a})">Bloquear/Lib</button>
                    <button style="background:var(--red)" onclick="del('${c.p}')">Remover</button>
                </td></tr>`;
        });
        document.getElementById('lista_admin').innerHTML = h + "</table>";
    }

    async function add() {
        const k = document.getElementById('mestre').value;
        await fetch('/admin/cadastrar', {method:'POST', headers:{'Content-Type':'application/json'}, 
        body: JSON.stringify({key:k, n:document.getElementById('n').value, p:document.getElementById('p').value, l:document.getElementById('l').value})});
        listar();
    }

    async function addCr(p) {
        const q = prompt("Adicionar quantos créditos?");
        if(q) await fetch('/admin/credito', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({key:document.getElementById('mestre').value, pin:p, qtd:q})});
        listar();
    }

    async function altSt(p, a) {
        await fetch('/admin/status', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({key:document.getElementById('mestre').value, pin:p, ativo:!a})});
        listar();
    }

    async function del(p) {
        if(confirm("Excluir cliente?")) await fetch('/admin/deletar', {method:'DELETE', headers:{'Content-Type':'application/json'}, body: JSON.stringify({key:document.getElementById('mestre').value, pin:p})});
        listar();
    }

    async function entrar() {
        const p = document.getElementById('pin').value;
        const res = await fetch('/v1/cliente/dados?pin=' + p);
        if(res.ok) {
            const d = await res.json();
            document.getElementById('login_area').style.display='none';
            document.getElementById('dashboard').style.display='block';
            document.getElementById('emp_nome').innerText = d.empresa;
            document.getElementById('uso').innerText = d.usadas;
            document.getElementById('total').innerText = d.limite;
            let h = "";
            d.hist.reverse().forEach((t, i) => {
                const pt = t.split(' | ');
                h += `<div class="hist-item" id="r-${i}"><input type="checkbox" onchange="document.getElementById('r-${i}').classList.toggle('selected')" class="no-print"> <b style="color:var(--blue); margin-left:10px">${pt[1]}</b> <span style="margin-left:20px; font-family:monospace">${pt[2]}</span></div>`;
            });
            document.getElementById('lista_historico').innerHTML = h;
        } else { alert("Acesso Negado ou Bloqueado!"); }
    }

    async function gerar() {
        const o = document.getElementById('obs').value || "GERAL";
        const p = document.getElementById('pin').value;
        await fetch('/v1/cliente/gerar', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({pin:p, obs:o})});
        entrar();
    }
    </script>
</body>
</html>
"""

@app.route('/')
def home(): return render_template_string(HTML_SISTEMA)

@app.route('/painel-secreto-kleber')
def admin(): return render_template_string(HTML_SISTEMA, tipo='admin')

@app.route('/v1/cliente/dados')
def get_dados():
    pin = request.args.get('pin')
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT nome_empresa, acessos, limite, historico_chaves, ativo FROM clientes WHERE pin_hash = %s", (pin,))
    c = cur.fetchone(); cur.close(); conn.close()
    if c:
        if not c[4]: return jsonify({"e": "bloqueado"}), 403
        return jsonify({"empresa": c[0], "usadas": c[1], "limite": c[2], "hist": c[3]})
    return jsonify({"e": "404"}), 404

@app.route('/v1/cliente/gerar', methods=['POST'])
def gerar_key():
    d = request.json
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT acessos, limite, ativo FROM clientes WHERE pin_hash = %s", (d['pin'],))
    c = cur.fetchone()
    if c and c[2] and c[0] < c[1]:
        nk = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(30))
        reg = f"X | {d['obs'].upper()} | {nk}"
        cur.execute("UPDATE clientes SET acessos=acessos+1, historico_chaves=array_append(historico_chaves, %s) WHERE pin_hash=%s", (reg, d['pin']))
        conn.commit()
    cur.close(); conn.close(); return jsonify({"ok": True})

@app.route('/admin/listar')
def list_adm():
    if request.args.get('key') != ADMIN_KEY: return jsonify([]), 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT nome_empresa, pin_hash, acessos, limite, ativo FROM clientes ORDER BY id DESC")
    r = cur.fetchall(); cur.close(); conn.close()
    return jsonify([{"n": x[0], "p": x[1], "u": x[2], "l": x[3], "a": x[4]} for x in r])

@app.route('/admin/status', methods=['POST'])
def status():
    d = request.json
    if d.get('key') != ADMIN_KEY: return jsonify({"e": 403}), 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("UPDATE clientes SET ativo = %s WHERE pin_hash = %s", (d['ativo'], d['pin']))
    conn.commit(); cur.close(); conn.close(); return jsonify({"ok": True})

@app.route('/admin/credito', methods=['POST'])
def credito():
    d = request.json
    if d.get('key') != ADMIN_KEY: return jsonify({"e": 403}), 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("UPDATE clientes SET limite = limite + %s WHERE pin_hash = %s", (int(d['qtd']), d['pin']))
    conn.commit(); cur.close(); conn.close(); return jsonify({"ok": True})

@app.route('/admin/cadastrar', methods=['POST'])
def add_cli():
    d = request.json
    if d.get('key') != ADMIN_KEY: return jsonify({"e": 403}), 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("INSERT INTO clientes (nome_empresa, pin_hash, limite, historico_chaves, ativo, acessos) VALUES (%s, %s, %s, '{}', TRUE, 0)", (d['n'], d['p'], d['l']))
    conn.commit(); cur.close(); conn.close(); return jsonify({"ok": True})

@app.route('/admin/deletar', methods=['DELETE'])
def del_cli():
    d = request.json
    if d.get('key') != ADMIN_KEY: return jsonify({"e": 403}), 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("DELETE FROM clientes WHERE pin_hash = %s", (d['pin'],))
    conn.commit(); cur.close(); conn.close(); return jsonify({"ok": True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))