import os, secrets, string, psycopg2
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Busca a chave quântica e o banco das variáveis de ambiente do Render
ADMIN_KEY = os.environ.get('ADMIN_KEY')

def get_db_connection():
    url = os.environ.get('DATABASE_URL')
    if not url: return None
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    try:
        return psycopg2.connect(url, sslmode='require', connect_timeout=10)
    except:
        return None

def init_db():
    conn = get_db_connection()
    if not conn: return
    cur = conn.cursor()
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
    cur.execute("DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='clientes' AND column_name='ativo') THEN ALTER TABLE clientes ADD COLUMN ativo BOOLEAN DEFAULT TRUE; END IF; END $$;")
    conn.commit()
    cur.close(); conn.close()

init_db()

HTML_SISTEMA = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>SISTEMA QUANTUM | GESTÃO</title>
    <style>
        :root { --blue: #38bdf8; --dark: #0b1120; --card: #1e293b; --red: #ef4444; --green: #22c55e; }
        body { background: var(--dark); color: white; font-family: sans-serif; padding: 20px; }
        .container { max-width: 1000px; margin: auto; background: var(--card); padding: 25px; border-radius: 15px; border: 1px solid #334155; }
        input { padding: 10px; margin: 5px; background: #0f172a; border: 1px solid #334155; color: white; border-radius: 5px; }
        button { padding: 8px 12px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; color: white; margin: 2px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; background: #0f172a; }
        th, td { padding: 10px; border: 1px solid #334155; text-align: center; font-size: 13px; }
        .status-ativo { color: var(--green); } .status-bloqueado { color: var(--red); }
    </style>
</head>
<body>
    <div class="container">
        {% if tipo == 'admin' %}
            <h1>PAINEL DE CONTROLE ADMIN</h1>
            <input type="password" id="mestre" placeholder="Insira sua Chave Quântica">
            <button style="background:var(--blue)" onclick="listar()">FORÇAR LISTA DO BANCO</button>
            
            <div style="background:#0f172a; padding:15px; margin-top:20px; border-radius:10px; border:1px solid #334155;">
                <h3>Cadastrar Empresa</h3>
                <input type="text" id="n" placeholder="Nome">
                <input type="text" id="p" placeholder="PIN (6 dígitos)" maxlength="6">
                <input type="number" id="l" placeholder="Créditos">
                <button style="background:var(--green)" onclick="add()">SALVAR NO DB</button>
            </div>
            <div id="lista_admin"></div>
        {% else %}
            <div id="login_area">
                <h1>LOGIN QUANTUM</h1>
                <input type="text" id="pin" placeholder="PIN" maxlength="6">
                <button style="background:var(--blue); width:100%" onclick="entrar()">ENTRAR</button>
            </div>
            <div id="dashboard" style="display:none;">
                <h2 id="emp_nome" style="color:var(--blue)"></h2>
                <div id="lista_historico"></div>
            </div>
        {% endif %}
    </div>

    <script>
    async function listar() {
        const k = document.getElementById('mestre').value;
        const res = await fetch('/admin/listar?key=' + k);
        if(!res.ok) return alert("Erro: Chave Admin Inválida!");
        const dados = await res.json();
        let h = "<table><tr><th>Empresa</th><th>PIN</th><th>Uso/Total</th><th>Status</th><th>Ações</th></tr>";
        dados.forEach(c => {
            h += `<tr><td>${c.n}</td><td>${c.p}</td><td>${c.u}/${c.l}</td>
                <td class="${c.a?'status-ativo':'status-bloqueado'}"><b>${c.a?'ATIVO':'BLOQUEADO'}</b></td>
                <td>
                    <button style="background:var(--blue)" onclick="addCr('${c.p}')">+ Crédito</button>
                    <button style="background:orange" onclick="altSt('${c.p}',${c.a})">Bloq/Lib</button>
                    <button style="background:#6366f1" onclick="limpHist('${c.p}')">Limpar Hist.</button>
                    <button style="background:var(--red)" onclick="del('${c.p}')">Excluir</button>
                </td></tr>`;
        });
        document.getElementById('lista_admin').innerHTML = h + "</table>";
    }

    async function limpHist(p) {
        if(!confirm("Zerar consumo e apagar chaves deste cliente?")) return;
        const k = document.getElementById('mestre').value;
        await fetch('/admin/limpar_historico', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({key:k, pin:p})});
        listar();
    }

    async function add() {
        const k = document.getElementById('mestre').value;
        await fetch('/admin/cadastrar', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({key:k, n:document.getElementById('n').value, p:document.getElementById('p').value, l:document.getElementById('l').value})});
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
        if(confirm("Remover cliente?")) await fetch('/admin/deletar', {method:'DELETE', headers:{'Content-Type':'application/json'}, body: JSON.stringify({key:document.getElementById('mestre').value, pin:p})});
        listar();
    }
    </script>
</body>
</html>
"""

@app.route('/')
def home(): return render_template_string(HTML_SISTEMA)

@app.route('/painel-secreto-kleber')
def admin_route(): return render_template_string(HTML_SISTEMA, tipo='admin')

@app.route('/admin/listar')
def list_adm():
    if request.args.get('key') != ADMIN_KEY: return jsonify([]), 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT nome_empresa, pin_hash, acessos, limite, ativo FROM clientes ORDER BY id DESC")
    r = cur.fetchall(); cur.close(); conn.close()
    return jsonify([{"n": x[0], "p": x[1], "u": x[2], "l": x[3], "a": x[4]} for x in r])

@app.route('/admin/limpar_historico', methods=['POST'])
def clean_hist():
    d = request.json
    if d.get('key') != ADMIN_KEY: return jsonify({"e": 403}), 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("UPDATE clientes SET acessos = 0, historico_chaves = '{}' WHERE pin_hash = %s", (d['pin'],))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"ok": True})

@app.route('/admin/status', methods=['POST'])
def st_adm():
    d = request.json
    if d.get('key') != ADMIN_KEY: return jsonify({"e": 403}), 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("UPDATE clientes SET ativo = %s WHERE pin_hash = %s", (d['ativo'], d['pin']))
    conn.commit(); cur.close(); conn.close(); return jsonify({"ok": True})

@app.route('/admin/credito', methods=['POST'])
def cr_adm():
    d = request.json
    if d.get('key') != ADMIN_KEY: return jsonify({"e": 403}), 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("UPDATE clientes SET limite = limite + %s WHERE pin_hash = %s", (int(d['qtd']), d['pin']))
    conn.commit(); cur.close(); conn.close(); return jsonify({"ok": True})

@app.route('/admin/cadastrar', methods=['POST'])
def add_adm():
    d = request.json
    if d.get('key') != ADMIN_KEY: return jsonify({"e": 403}), 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("INSERT INTO clientes (nome_empresa, pin_hash, limite, historico_chaves, ativo, acessos) VALUES (%s, %s, %s, '{}', TRUE, 0)", (d['n'], d['p'], d['l']))
    conn.commit(); cur.close(); conn.close(); return jsonify({"ok": True})

@app.route('/admin/deletar', methods=['DELETE'])
def del_adm():
    d = request.json
    if d.get('key') != ADMIN_KEY: return jsonify({"e": 403}), 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("DELETE FROM clientes WHERE pin_hash = %s", (d['pin'],))
    conn.commit(); cur.close(); conn.close(); return jsonify({"ok": True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))