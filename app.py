import os, secrets, string, psycopg2
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- CONFIGURAÇÕES DE AMBIENTE (RENDER) ---
def get_admin_key():
    key = os.environ.get('ADMIN_KEY')
    return key.strip() if key else None

def get_db_connection():
    url = os.environ.get('DATABASE_URL')
    if not url: return None
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return psycopg2.connect(url, sslmode='require')

# --- INICIALIZAÇÃO DO BANCO ---
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

# --- INTERFACE HTML COMPLETA (ADMIN + CLIENTE) ---
HTML_SISTEMA = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QUANTUM | SISTEMA DE GESTÃO</title>
    <style>
        :root { --blue: #38bdf8; --dark: #0b1120; --card: #1e293b; --red: #ef4444; --green: #22c55e; }
        body { background: var(--dark); color: white; font-family: sans-serif; padding: 20px; }
        .container { max-width: 1000px; margin: auto; background: var(--card); padding: 25px; border-radius: 15px; border: 1px solid #334155; }
        input { padding: 12px; margin: 5px; background: #0f172a; border: 1px solid #334155; color: white; border-radius: 8px; }
        button { padding: 10px 15px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; color: white; margin: 2px; }
        
        /* Estilos da Tabela e Lista */
        table { width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 14px; }
        th, td { padding: 12px; border: 1px solid #334155; text-align: center; }
        th { background: #0f172a; color: var(--blue); }
        .status-on { color: var(--green); } .status-off { color: var(--red); }

        .hist-item { background: #0f172a; padding: 15px; margin-top: 10px; border-radius: 10px; display: flex; align-items: center; border: 2px solid transparent; }
        .hist-item.selected { border-color: var(--blue); background: #162e45; }
        
        /* Impressão */
        @media print {
            .no-print, button, input, h1 { display: none !important; }
            body { background: white !important; color: black !important; }
            .container { border: none; background: white !important; }
            .hist-item { border: 1px solid #000 !important; color: black !important; background: white !important; }
            .hist-item:not(.selected) { display: none !important; }
        }
    </style>
</head>
<body>
    <div class="container">
        {% if tipo == 'admin' %}
            <h1 style="color:var(--blue)">PAINEL ADMINISTRATIVO</h1>
            <input type="password" id="mestre" placeholder="Chave Admin do Render">
            <button style="background:var(--blue)" onclick="listar()">FORÇAR LISTA DO BANCO</button>

            <div style="margin-top:20px; padding:20px; background:#0f172a; border-radius:10px; border:1px solid #334155;">
                <h3>Cadastrar Nova Empresa</h3>
                <input type="text" id="n" placeholder="Nome da Empresa">
                <input type="text" id="p" placeholder="PIN (6 dígitos)" maxlength="6">
                <input type="number" id="l" placeholder="Limite de Créditos">
                <button style="background:var(--green)" onclick="cadastrar()">SALVAR NO BANCO</button>
            </div>
            
            <div id="lista_admin"></div>

        {% else %}
            <div id="login_area">
                <h1>LOGIN CLIENTE</h1>
                <input type="text" id="pin" placeholder="Seu PIN de 6 dígitos" maxlength="6" style="width:100%; box-sizing:border-box;">
                <button style="background:var(--blue); width:100%; margin-top:10px;" onclick="entrar()">ENTRAR</button>
            </div>

            <div id="dashboard" style="display:none;">
                <h2 id="emp_nome" style="color:var(--blue)"></h2>
                <div style="display:flex; justify-content:space-between; align-items:center; background:#0f172a; padding:15px; border-radius:10px;">
                    <span>Saldo: <b id="uso"></b> / <b id="total"></b></span>
                    <button style="background:#475569" onclick="window.print()">🖨️ IMPRIMIR SELECIONADOS</button>
                </div>
                <div class="no-print" style="margin-top:20px;">
                    <input type="text" id="obs" placeholder="Observação (Ex: Lote 500)" style="width:60%">
                    <button style="background:var(--green); width:35%" onclick="gerar()">GERAR CHAVE</button>
                </div>
                <div id="lista_historico" style="margin-top:20px;"></div>
            </div>
        {% endif %}
    </div>

    <script>
    // FUNÇÕES ADMIN
    async function listar() {
        const k = document.getElementById('mestre').value.trim();
        const res = await fetch('/admin/listar?key=' + k);
        if(!res.ok) return alert("Chave Admin Inválida!");
        const dados = await res.json();
        let h = "<table><tr><th>Empresa</th><th>PIN</th><th>Uso/Total</th><th>Status</th><th>Ações</th></tr>";
        dados.forEach(c => {
            h += `<tr><td>${c.n}</td><td>${c.p}</td><td>${c.u}/${c.l}</td>
                <td class="${c.a?'status-on':'status-off'}"><b>${c.a?'ATIVO':'BLOQUEADO'}</b></td>
                <td>
                    <button style="background:var(--blue)" onclick="addCr('${c.p}')">+ Cr</button>
                    <button style="background:orange" onclick="altSt('${c.p}',${c.a})">${c.a?'Bloq':'Lib'}</button>
                    <button style="background:#6366f1" onclick="limp('${c.p}')">Limpar</button>
                    <button style="background:var(--red)" onclick="del('${c.p}')">X</button>
                </td></tr>`;
        });
        document.getElementById('lista_admin').innerHTML = h + "</table>";
    }

    async function cadastrar() {
        const k = document.getElementById('mestre').value.trim();
        const body = {key:k, n:document.getElementById('n').value, p:document.getElementById('p').value, l:document.getElementById('l').value};
        const res = await fetch('/admin/cadastrar', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(body)});
        if(res.ok) { alert("Cadastrado!"); listar(); }
    }

    async function addCr(p) {
        const q = prompt("Adicionar quantos créditos?");
        if(q) await fetch('/admin/credito', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({key:document.getElementById('mestre').value.trim(), pin:p, qtd:q})});
        listar();
    }
    async function altSt(p, a) {
        await fetch('/admin/status', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({key:document.getElementById('mestre').value.trim(), pin:p, ativo:!a})});
        listar();
    }
    async function limp(p) {
        if(confirm("Zerar histórico e consumo?")) await fetch('/admin/limpar', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({key:document.getElementById('mestre').value.trim(), pin:p})});
        listar();
    }
    async function del(p) {
        if(confirm("Excluir empresa?")) await fetch('/admin/deletar', {method:'DELETE', headers:{'Content-Type':'application/json'}, body:JSON.stringify({key:document.getElementById('mestre').value.trim(), pin:p})});
        listar();
    }

    // FUNÇÕES CLIENTE
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
                    <input type="checkbox" class="no-print" onchange="document.getElementById('row-${i}').classList.toggle('selected')">
                    <span style="margin-left:15px; font-weight:bold; color:var(--blue)">${pt[1]}</span>
                    <span style="margin-left:auto; font-family:monospace">${pt[2]}</span>
                </div>`;
            });
            document.getElementById('lista_historico').innerHTML = h;
        } else { alert("PIN Inválido ou Bloqueado!"); }
    }

    async function gerar() {
        const p = document.getElementById('pin').value;
        const o = document.getElementById('obs').value || "GERAL";
        await fetch('/v1/cliente/gerar', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({pin:p, obs:o})});
        entrar();
    }
    </script>
</body>
</html>
"""

# --- ROTAS DO SERVIDOR ---
@app.route('/')
def home(): return render_template_string(HTML_SISTEMA)

@app.route('/painel-secreto-kleber')
def admin_page(): return render_template_string(HTML_SISTEMA, tipo='admin')

@app.route('/admin/listar')
def list_adm():
    key = get_admin_key()
    if not key or request.args.get('key', '').strip() != key: return jsonify([]), 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT nome_empresa, pin_hash, acessos, limite, ativo FROM clientes ORDER BY id DESC")
    r = cur.fetchall(); cur.close(); conn.close()
    return jsonify([{"n": x[0], "p": x[1], "u": x[2], "l": x[3], "a": x[4]} for x in r])

@app.route('/admin/cadastrar', methods=['POST'])
def add_adm():
    d = request.json
    if not get_admin_key() or d.get('key', '').strip() != get_admin_key(): return jsonify({"e":403}), 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("INSERT INTO clientes (nome_empresa, pin_hash, limite, historico_chaves, ativo, acessos) VALUES (%s, %s, %s, '{}', TRUE, 0)", (d['n'], d['p'], d['l']))
    conn.commit(); cur.close(); conn.close(); return jsonify({"ok": True})

@app.route('/admin/limpar', methods=['POST'])
def limp_adm():
    d = request.json
    if not get_admin_key() or d.get('key', '').strip() != get_admin_key(): return jsonify({"e":403}), 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("UPDATE clientes SET acessos = 0, historico_chaves = '{}' WHERE pin_hash = %s", (d['pin'],))
    conn.commit(); cur.close(); conn.close(); return jsonify({"ok": True})

@app.route('/admin/status', methods=['POST'])
def st_adm():
    d = request.json
    if not get_admin_key() or d.get('key', '').strip() != get_admin_key(): return jsonify({"e":403}), 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("UPDATE clientes SET ativo = %s WHERE pin_hash = %s", (d['ativo'], d['pin']))
    conn.commit(); cur.close(); conn.close(); return jsonify({"ok": True})

@app.route('/admin/credito', methods=['POST'])
def cr_adm():
    d = request.json
    if not get_admin_key() or d.get('key', '').strip() != get_admin_key(): return jsonify({"e":403}), 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("UPDATE clientes SET limite = limite + %s WHERE pin_hash = %s", (int(d['qtd']), d['pin']))
    conn.commit(); cur.close(); conn.close(); return jsonify({"ok": True})

@app.route('/admin/deletar', methods=['DELETE'])
def del_adm():
    d = request.json
    if not get_admin_key() or d.get('key', '').strip() != get_admin_key(): return jsonify({"e":403}), 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("DELETE FROM clientes WHERE pin_hash = %s", (d['pin'],))
    conn.commit(); cur.close(); conn.close(); return jsonify({"ok": True})

@app.route('/v1/cliente/dados')
def get_cli():
    pin = request.args.get('pin')
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT nome_empresa, acessos, limite, historico_chaves, ativo FROM clientes WHERE pin_hash = %s", (pin,))
    c = cur.fetchone(); cur.close(); conn.close()
    if c and c[4]: return jsonify({"empresa": c[0], "usadas": c[1], "limite": c[2], "hist": c[3]})
    return jsonify({"e": 401}), 401

@app.route('/v1/cliente/gerar', methods=['POST'])
def gen_key():
    d = request.json
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT acessos, limite, ativo FROM clientes WHERE pin_hash = %s", (d['pin'],))
    c = cur.fetchone()
    if c and c[4] and c[0] < c[1]:
        nk = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(30))
        reg = f"X | {d['obs'].upper()} | {nk}"
        cur.execute("UPDATE clientes SET acessos=acessos+1, historico_chaves=array_append(historico_chaves, %s) WHERE pin_hash=%s", (reg, d['pin']))
        conn.commit()
    cur.close(); conn.close(); return jsonify({"ok": True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))