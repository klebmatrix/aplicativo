import os, psycopg2, datetime, time, random
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Extração de Chave do Ambiente Render
MASTER_KEY = os.environ.get('ADMIN_KEY') or os.environ.get('admin_key')

def get_db_connection():
    url = os.environ.get('DATABASE_URL')
    if url and url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    try:
        return psycopg2.connect(url, sslmode='require')
    except:
        return None

@app.before_request
def setup_db():
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
                status TEXT DEFAULT 'Ativo',
                historico_chaves TEXT[] DEFAULT '{}'
            );
        ''')
        cur.execute("DO $$ BEGIN ALTER TABLE clientes ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'Ativo'; EXCEPTION WHEN duplicate_column THEN NULL; END $$;")
        conn.commit(); cur.close(); conn.close()

CONHECIMENTO = {
    "freqs": ["432Hz", "528Hz", "639Hz", "741Hz", "852Hz", "963Hz"],
    "mantras": [
        "Eu sou um íman para milagres e abundância.",
        "Minha vibração está em harmonia com o universo.",
        "A cura flui através de mim agora.",
        "Eu confio no processo da vida e na minha intuição.",
        "A prosperidade é meu estado natural de ser."
    ]
}

# --- INTERFACE DE ELITE (ADMIN E CLIENTE) ---
HTML_SISTEMA = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>QUANTUM SEED - PLATAFORMA DE ELITE</title>
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Montserrat:wght@300;400;600&display=swap" rel="stylesheet">
    <style>
        :root { --gold: #c5a059; --bg: #020617; --card: #0f172a; --red: #ef4444; --green: #22c55e; }
        body { background: var(--bg); color: #f8fafc; font-family: 'Montserrat', sans-serif; margin: 0; padding: 20px; }
        .glass-card { background: rgba(15, 23, 42, 0.9); border: 1px solid rgba(197, 160, 89, 0.3); border-radius: 20px; padding: 25px; box-shadow: 0 20px 50px rgba(0,0,0,0.6); }
        h1, h2 { font-family: 'Cinzel', serif; color: var(--gold); text-align: center; margin-top: 0; }
        input, select { width: 100%; padding: 12px; margin: 8px 0; background: #1e293b; border: 1px solid #334155; color: white; border-radius: 8px; box-sizing: border-box; }
        .btn { padding: 12px 20px; border-radius: 8px; border: none; cursor: pointer; font-weight: bold; transition: 0.3s; text-transform: uppercase; font-size: 12px; }
        .btn-gold { background: var(--gold); color: black; width: 100%; font-size: 14px; }
        .btn-red { background: var(--red); color: white; }
        
        /* Layout Admin */
        .admin-grid { display: grid; grid-template-columns: 1fr 2fr; gap: 20px; margin-top: 20px; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th { color: var(--gold); border-bottom: 1px solid var(--gold); padding: 10px; text-align: left; font-size: 11px; }
        td { padding: 10px; border-bottom: 1px solid rgba(255,255,255,0.05); font-size: 13px; }
        
        /* Layout Cliente */
        .energy-bar { background: rgba(255,255,255,0.05); height: 10px; border-radius: 5px; margin: 15px 0; overflow: hidden; }
        .energy-fill { height: 100%; background: var(--gold); width: 0%; transition: 1s ease; }
        .history-item { background: rgba(255,255,255,0.02); border-left: 4px solid var(--gold); padding: 12px; margin: 8px 0; border-radius: 4px; display: flex; align-items: center; }
        
        @media print { .no-print { display: none; } #print_area { display: block; color: black; } }
    </style>
</head>
<body>
    <div class="no-print" style="max-width: 1000px; margin: auto;">
        {% if modo == 'admin' %}
            <div class="glass-card">
                <h1>GESTÃO MASTER QUANTUM</h1>
                <div style="text-align:center"><input type="password" id="ak" placeholder="CHAVE ADMIN_KEY" style="max-width:300px"></div>
                <button class="btn btn-gold" onclick="listar()" style="max-width:200px; display:block; margin: 10px auto;">SINCRONIZAR REDE</button>

                <div class="admin-grid">
                    <div class="glass-card" style="background: rgba(0,0,0,0.3)">
                        <h3>NOVO PORTADOR</h3>
                        <input type="text" id="n" placeholder="Nome do Cliente">
                        <input type="text" id="p" placeholder="PIN (6-8 dig)">
                        <input type="number" id="l" placeholder="Limite Inicial">
                        <select id="st">
                            <option value="Ativo">Status: ATIVO</option>
                            <option value="VIP">Status: VIP (ILIMITADO)</option>
                            <option value="Bloqueado">Status: BLOQUEADO</option>
                        </select>
                        <button class="btn btn-gold" onclick="salvar()">CONSEGRAR / ATUALIZAR</button>
                    </div>
                    <div class="glass-card" style="background: rgba(0,0,0,0.3)">
                        <h3>GERENCIAMENTO</h3>
                        <div id="lista_admin"></div>
                    </div>
                </div>
            </div>
        {% else %}
            <div class="glass-card" style="max-width:500px; margin: auto;">
                <h1>QUANTUM SEED</h1>
                <div id="login_area">
                    <input type="password" id="pin" placeholder="Chave de Acesso" maxlength="8">
                    <button class="btn btn-gold" onclick="logar()">SINTONIZAR PORTAL</button>
                </div>
                <div id="dash_area" style="display:none;">
                    <h2 id="nome_cli" style="font-size:18px"></h2>
                    <div style="display:flex; justify-content:space-between; font-size:12px">
                        <span>Fluxo de Créditos</span>
                        <span id="txt_saldo"></span>
                    </div>
                    <div class="energy-bar"><div id="fill" class="energy-fill"></div></div>
                    
                    <input type="text" id="obs" placeholder="Nome do Paciente ou Intenção">
                    <button class="btn btn-gold" id="btn_gerar" onclick="gerar()">MANIFESTAR FREQUÊNCIA</button>
                    <button onclick="window.print()" style="background:none; border:none; color:var(--gold); width:100%; margin-top:15px; cursor:pointer; font-size:11px; text-decoration:underline;">IMPRIMIR CERTIFICADOS</button>
                    <div id="lista_cli" style="margin-top:20px"></div>
                </div>
            </div>
        {% endif %}
    </div>
    <div id="print_area"></div>

    <script>
    // --- LÓGICA ADMIN ---
    async function listar() {
        const k = document.getElementById('ak').value;
        const res = await fetch(`/api/admin/list?k=${k}`);
        if(!res.ok) return alert("Acesso Negado.");
        const data = await res.json();
        let h = "<table><tr><th>NOME</th><th>SALDO</th><th>AÇÃO</th></tr>";
        data.forEach(c => {
            h += `<tr>
                <td><b>${c.n}</b><br><small>${c.p}</small></td>
                <td>${c.u}/${c.l}<br><small>${c.s}</small></td>
                <td>
                    <button class="btn" style="background:#3b82f6; padding:5px" onclick="addCr('${c.p}',50)">+50</button>
                    <button class="btn btn-red" style="padding:5px" onclick="remover('${c.p}')">X</button>
                </td>
            </tr>`;
        });
        document.getElementById('lista_admin').innerHTML = h + "</table>";
    }

    async function addCr(pin, q) {
        const k = document.getElementById('ak').value;
        await fetch('/api/admin/add_credit', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({k:k, p:pin, q:q}) });
        listar();
    }

    async function salvar() {
        const payload = { k:document.getElementById('ak').value, n:document.getElementById('n').value, p:document.getElementById('p').value, l:parseInt(document.getElementById('l').value), s:document.getElementById('st').value };
        await fetch('/api/admin/save', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload) });
        listar();
    }

    async function remover(pin) {
        if(!confirm("Excluir cliente?")) return;
        await fetch('/api/admin/delete', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({k:document.getElementById('ak').value, p:pin}) });
        listar();
    }

    // --- LÓGICA CLIENTE ---
    async function logar() {
        const p = document.getElementById('pin').value;
        const res = await fetch(`/api/cli/info?p=${p}`, {cache: "no-store"});
        if(!res.ok) return alert("PIN inválido ou Bloqueado.");
        const d = await res.json();
        if(d.s === 'Bloqueado') return alert("Assinatura suspensa. Contate o administrador.");
        
        document.getElementById('login_area').style.display='none';
        document.getElementById('dash_area').style.display='block';
        document.getElementById('nome_cli').innerText = d.n;
        const saldo = (d.s === 'VIP') ? 'ILIMITADO' : (d.l - d.u);
        document.getElementById('txt_saldo').innerText = saldo;
        document.getElementById('fill').style.width = (d.s === 'VIP') ? '100%' : ((d.l-d.u)/d.l*100) + "%";

        let h = "";
        if(d.h) d.h.reverse().forEach(item => {
            const pts = item.split(' | ');
            h += `<div class="history-item">
                <input type="checkbox" class="ck" data-full="${item}" style="margin-right:10px">
                <div><b>${pts[1]}</b><br><small>${pts[2]} • ${pts[0]}</small></div>
            </div>`;
        });
        document.getElementById('lista_cli').innerHTML = h;
    }

    async function gerar() {
        const p = document.getElementById('pin').value;
        const o = document.getElementById('obs').value || "GERAL";
        const res = await fetch('/api/cli/generate', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({p:p, o:o}) });
        if(res.ok) { document.getElementById('obs').value = ""; logar(); } else { alert("Saldo insuficiente."); }
    }
    </script>
</body>
</html>
"""

# --- ROTAS DE GESTÃO ---

@app.route('/api/admin/list')
def api_l():
    k = request.args.get('k')
    if not MASTER_KEY or k != MASTER_KEY: return "Err", 403
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT nome_empresa, pin_hash, acessos, limite, status FROM clientes ORDER BY id DESC")
    r = cur.fetchall(); cur.close(); conn.close()
    return jsonify([{"n": x[0], "p": x[1], "u": x[2], "l": x[3], "s": x[4]} for x in r])

@app.route('/api/admin/add_credit', methods=['POST'])
def api_add():
    d = request.json
    if not MASTER_KEY or d.get('k') != MASTER_KEY: return "Err", 403
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE clientes SET limite = limite + %s WHERE pin_hash = %s", (d['q'], d['p']))
    conn.commit(); cur.close(); conn.close()
    return "OK"

@app.route('/api/admin/save', methods=['POST'])
def api_s():
    d = request.json
    if not MASTER_KEY or d.get('k') != MASTER_KEY: return "Err", 403
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO clientes (nome_empresa, pin_hash, limite, status) VALUES (%s, %s, %s, %s) 
        ON CONFLICT (pin_hash) DO UPDATE SET limite = EXCLUDED.limite, nome_empresa = EXCLUDED.nome_empresa, status = EXCLUDED.status
    ''', (d['n'], d['p'], d['l'], d['s']))
    conn.commit(); cur.close(); conn.close()
    return "OK"

@app.route('/api/admin/delete', methods=['POST'])
def api_delete():
    d = request.json
    if not MASTER_KEY or d.get('k') != MASTER_KEY: return "Err", 403
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM clientes WHERE pin_hash = %s", (d['p'],))
    conn.commit(); cur.close(); conn.close()
    return "OK"

@app.route('/api/cli/info')
def api_i():
    p = request.args.get('p')
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT nome_empresa, acessos, limite, historico_chaves, status FROM clientes WHERE pin_hash = %s", (p,))
    c = cur.fetchone(); cur.close(); conn.close()
    if c: return jsonify({"n": c[0], "u": c[1], "l": c[2], "h": c[3], "s": c[4]})
    return "Err", 404

@app.route('/api/cli/generate', methods=['POST'])
def api_g():
    d = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT acessos, limite, status FROM clientes WHERE pin_hash = %s", (d['p'],))
    c = cur.fetchone()
    if c and (c[2] == 'VIP' or c[0] < c[1]):
        f = random.choice(CONHECIMENTO["freqs"])
        m = random.choice(CONHECIMENTO["mantras"])
        val = (datetime.datetime.now() + datetime.timedelta(days=21)).strftime('%d/%m/%Y')
        res = f"{datetime.datetime.now().strftime('%d/%m/%Y')} | {str(d.get('o','GERAL')).upper()} | {f} | {m} | {val}"
        cur.execute("UPDATE clientes SET acessos=acessos+1, historico_chaves=array_append(historico_chaves, %s) WHERE pin_hash=%s", (res, d['p']))
        conn.commit(); cur.close(); conn.close()
        return "OK"
    return "Err", 403

@app.route('/painel-secreto-kleber')
def r_a(): return render_template_string(HTML_SISTEMA, modo='admin')

@app.route('/')
def r_h(): return render_template_string(HTML_SISTEMA, modo='cliente')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))