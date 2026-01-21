import os, secrets, string, psycopg2
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

ADMIN_KEY = os.environ.get('ADMIN_KEY', 'ADMIN123')

def get_db_connection():
    url = os.environ.get('DATABASE_URL')
    if url and url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return psycopg2.connect(url, sslmode='require')

# FUNÇÃO QUE CORRIGE O BANCO AUTOMATICAMENTE
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    # Cria a tabela se não existir
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
    # Garante que a coluna 'ativo' existe (evita o erro 404)
    cur.execute("DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='clientes' AND column_name='ativo') THEN ALTER TABLE clientes ADD COLUMN ativo BOOLEAN DEFAULT TRUE; END IF; END $$;")
    conn.commit()
    cur.close()
    conn.close()

# Inicia o banco ao abrir o app
init_db()

HTML_SISTEMA = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>SISTEMA QUANTUM | GESTÃO TOTAL</title>
    <style>
        :root { --blue: #38bdf8; --dark: #0b1120; --card: #1e293b; --red: #ef4444; --green: #22c55e; }
        body { background: var(--dark); color: white; font-family: 'Segoe UI', sans-serif; padding: 20px; margin: 0; }
        .container { max-width: 900px; margin: 20px auto; background: var(--card); padding: 30px; border-radius: 15px; border: 1px solid #334155; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        input { padding: 12px; margin: 5px; background: #0f172a; border: 1px solid #334155; color: white; border-radius: 8px; width: 200px; }
        button { padding: 10px 15px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; color: white; transition: 0.2s; }
        
        table { width: 100%; border-collapse: collapse; margin-top: 25px; background: #0f172a; border-radius: 10px; overflow: hidden; }
        th, td { padding: 15px; border: 1px solid #1e293b; text-align: center; }
        th { background: #1e293b; color: var(--blue); }
        
        .status-ativo { color: var(--green); }
        .status-bloqueado { color: var(--red); }
        
        .hist-item { background: #0f172a; padding: 15px; margin-top: 10px; border-radius: 10px; display: flex; align-items: center; border: 2px solid transparent; }
        .hist-item.selected { border-color: var(--blue); background: #162e45; }
        .obs-label { color: var(--blue); font-weight: bold; min-width: 130px; }
        .key-label { font-family: monospace; flex-grow: 1; color: #cbd5e1; }
        
        @media print {
            .no-print, button, input { display: none !important; }
            .hist-item:not(.selected) { display: none !important; }
            .hist-item { border: 1px solid #000 !important; color: black !important; }
        }
    </style>
</head>
<body>
    <div class="container">
        {% if tipo == 'admin' %}
            <h1 style="text-align:center; color: var(--blue);">PAINEL ADMINISTRATIVO</h1>
            <div style="text-align:center; margin-bottom: 20px;">
                <input type="password" id="mestre" placeholder="Chave Mestre">
                <button style="background:var(--blue)" onclick="listar()">ATUALIZAR LISTA</button>
            </div>

            <div style="background:#0f172a; padding:20px; border-radius:12px; border: 1px solid #334155;">
                <h3 style="margin-top:0">Cadastrar Novo Cliente</h3>
                <input type="text" id="n" placeholder="Nome da Empresa">
                <input type="text" id="p" placeholder="PIN (6 dígitos)" maxlength="6">
                <input type="number" id="l" placeholder="Créditos Iniciais">
                <button style="background:var(--green)" onclick="add()">CADASTRAR</button>
            </div>
            <div id="lista_admin"></div>
        {% else %}
            <div id="login_area" style="text-align:center">
                <h1 style="color: var(--blue)">LOGIN QUANTUM</h1>
                <input type="text" id="pin" placeholder="PIN 6 DÍGITOS" maxlength="6" style="width: 80%; text-align:center; font-size: 1.2rem;">
                <button style="background:var(--blue); width: 85%; margin-top: 15px; font-size: 1.1rem;" onclick="entrar()">ENTRAR NO PAINEL</button>
            </div>

            <div id="dashboard" style="display:none;">
                <h2 id="emp_nome" style="color: var(--blue); margin-top: 0;"></h2>
                <div style="background:#0f172a; padding:15px; border-radius:10px; display:flex; justify-content:space-between; align-items:center;">
                    <span>Saldo: <b id="uso"></b> / <b id="total"></b></span>
                    <button style="background:#475569" onclick="window.print()">🖨️ IMPRIMIR SELECIONADOS</button>
                </div>
                
                <div style="margin-top: 20px;">
                    <input type="text" id="obs" placeholder="Observação do Lote" style="width: 70%">
                    <button style="background:var(--green); width: 25%" onclick="gerar()">GERAR</button>
                </div>
                <div id="lista_historico" style="margin-top:20px;"></div>
            </div>
        {% endif %}
    </div>

    <script>
    async function listar() {
        const k = document.getElementById('mestre').value;
        const res = await fetch('/admin/listar?key=' + k);
        const dados = await res.json();
        let h = `<table><tr><th>Empresa</th><th>PIN</th><th>Saldo</th><th>Status</th><th>Ações</th></tr>`;
        dados.forEach(c => {
            h += `<tr>
                <td>${c.n}</td><td><code>${c.p}</code></td><td>${c.u}/${c.l}</td>
                <td class="${c.a?'status-ativo':'status-bloqueado'}"><b>${c.a?'ATIVO':'BLOQUEADO'}</b></td>
                <td>
                    <button style="background:var(--blue)" onclick="addCred('${c.p}')">+ Créditos</button>
                    <button style="background:orange" onclick="status('${c.p}',${c.a})">${c.a?'Bloquear':'Liberar'}</button>
                    <button style="background:var(--red)" onclick="apagar('${c.p}')">Excluir</button>
                </td></tr>`;
        });
        document.getElementById('lista_admin').innerHTML = h + "</table>";
    }

    async function addCred(p) {
        const q = prompt("Quantos créditos deseja ADICIONAR?");
        if(q) {
            await fetch('/admin/limite', {method:'POST', headers:{'Content-Type':'application/json'}, 
            body: JSON.stringify({key:document.getElementById('mestre').value, pin:p, qtd:q})});
            listar();
        }
    }

    async function status(p, a) {
        await fetch('/admin/status', {method:'POST', headers:{'Content-Type':'application/json'}, 
        body: JSON.stringify({key:document.getElementById('mestre').value, pin:p, ativo:!a})});
        listar();
    }

    async function add() {
        const n=document.getElementById('n').value, p=document.getElementById('p').value, l=document.getElementById('l').value;
        await fetch('/admin/cadastrar', {method:'POST', headers:{'Content-Type':'application/json'}, 
        body: JSON.stringify({key:document.getElementById('mestre').value, n, p, l})});
        listar();
    }

    async function apagar(p) {
        if(confirm("Deseja deletar este cliente?")) {
            await fetch('/admin/deletar', {method:'DELETE', headers:{'Content-Type':'application/json'}, 
            body: JSON.stringify({key:document.getElementById('mestre').value, pin:p})});
            listar();
        }
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
                h += `<div class="hist-item" id="row-${i}">
                    <input type="checkbox" onchange="document.getElementById('row-${i}').classList.toggle('selected')" class="no-print" style="width:20px; height:20px; margin-right:15px;">
                    <span class="obs-label">${pt[1]}</span>
                    <span class="key-label">${pt[2]}</span>
                </div>`;
            });
            document.getElementById('lista_historico').innerHTML = h;
        } else { alert("Acesso negado ou Empresa Bloqueada."); }
    }

    async function gerar() {
        const o = document.getElementById('obs').value || "GERAL";
        const p = document.getElementById('pin').value;
        const res = await fetch('/v1/cliente/gerar', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({pin:p, obs:o})});
        if(res.ok) { entrar(); document.getElementById('obs').value = ""; } else { alert("Sem saldo!"); }
    }
    </script>
</body>
</html>
"""

@app.route('/')
def home(): return render_template_string(HTML_SISTEMA)

@app.route('/painel-secreto-kleber')
def admin_p(): return render_template_string(HTML_SISTEMA, tipo='admin')

@app.route('/v1/cliente/dados')
def get_dados():
    pin = request.args.get('pin')
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT nome_empresa, acessos, limite, historico_chaves, ativo FROM clientes WHERE pin_hash = %s", (pin,))
    c = cur.fetchone(); cur.close(); conn.close()
    if c:
        if not c[4]: return jsonify({"e": "block"}), 403
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
    cur.close(); conn.close(); return jsonify({"e": "err"}), 403

@app.route('/admin/listar')
def list_adm():
    if request.args.get('key') != ADMIN_KEY: return jsonify([]), 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT nome_empresa, pin_hash, acessos, limite, ativo FROM clientes ORDER BY id DESC")
    r = cur.fetchall(); cur.close(); conn.close()
    return jsonify([{"n": x[0], "p": x[1], "u": x[2], "l": x[3], "a": x[4]} for x in r])

@app.route('/admin/status', methods=['POST'])
def m_status():
    d = request.json
    if d.get('key') != ADMIN_KEY: return jsonify({"e": 403}), 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("UPDATE clientes SET ativo = %s WHERE pin_hash = %s", (d['ativo'], d['pin']))
    conn.commit(); cur.close(); conn.close(); return jsonify({"ok": True})

@app.route('/admin/limite', methods=['POST'])
def m_limite():
    d = request.json
    if d.get('key') != ADMIN_KEY: return jsonify({"e": 403}), 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("UPDATE clientes SET limite = limite + %s WHERE pin_hash = %s", (int(d['qtd']), d['pin']))
    conn.commit(); cur.close(); conn.close(); return jsonify({"ok": True})

@app.route('/admin/cadastrar', methods=['POST'])
def m_add():
    d = request.json
    if d.get('key') != ADMIN_KEY: return jsonify({"e": 403}), 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("INSERT INTO clientes (nome_empresa, pin_hash, limite, acessos, ativo, historico_chaves) VALUES (%s, %s, %s, 0, TRUE, '{}')", (d['n'], d['p'], d['l']))
    conn.commit(); cur.close(); conn.close(); return jsonify({"ok": True})

@app.route('/admin/deletar', methods=['DELETE'])
def m_del():
    d = request.json
    if d.get('key') != ADMIN_KEY: return jsonify({"e": 403}), 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("DELETE FROM clientes WHERE pin_hash = %s", (d['pin'],))
    conn.commit(); cur.close(); conn.close(); return jsonify({"ok": True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))