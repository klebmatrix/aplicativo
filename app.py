import os, secrets, string, psycopg2, datetime
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

# Versão 3.0 - Forçando atualização de Cache
app = Flask(__name__)
CORS(app)

# Chave vinda do Render
MASTER_KEY = os.environ.get('admin_key') or os.environ.get('ADMIN_KEY')

def connect_db():
    url = os.environ.get('DATABASE_URL')
    if url and url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return psycopg2.connect(url, sslmode='require')

@app.before_request
def setup_database():
    conn = connect_db()
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
    conn.commit(); cur.close(); conn.close()

# Interface Única com Abas para Forçar Refresh
UI_V3 = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SISTEMA QUANTUM V3</title>
    <style>
        :root { --accent: #38bdf8; --bg: #0b1120; --card: #1e293b; }
        body { background: var(--bg); color: white; font-family: 'Segoe UI', sans-serif; margin: 0; padding: 20px; }
        .main-container { max-width: 900px; margin: auto; background: var(--card); padding: 30px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        input { padding: 12px; margin: 8px 0; background: #0f172a; border: 1px solid #334155; color: white; border-radius: 8px; width: 100%; box-sizing: border-box; }
        button { padding: 12px 20px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; color: white; transition: 0.2s; }
        .btn-add { background: #22c55e; width: 100%; margin-top: 10px; }
        .btn-list { background: #0284c7; }
        .btn-del { background: #ef4444; padding: 5px 10px; font-size: 11px; }
        
        /* Tabela e Itens */
        table { width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 14px; }
        th, td { border-bottom: 1px solid #334155; padding: 12px; text-align: left; }
        .item-chave { background: #0f172a; padding: 15px; margin: 8px 0; border-radius: 8px; display: flex; align-items: center; border: 1px solid transparent; }
        .item-chave.selected { border-color: var(--accent); background: #1e3a5a; }
        
        /* Certificado */
        #area_impressao { display: none; }
        @media print {
            .main-container { display: none !important; }
            #area_impressao { display: block !important; }
            .cert-page { page-break-after: always; height: 98vh; display: flex; justify-content: center; align-items: center; }
            .cert-box { border: 15px solid black; width: 80%; padding: 50px; text-align: center; font-family: serif; }
            .cert-title { font-size: 35px; font-weight: bold; margin-bottom: 30px; }
            .cert-key { background: #f2f2f2 !important; padding: 20px; font-family: monospace; font-size: 24px; border: 1px solid #ccc; font-weight: bold; }
        }
    </style>
</head>
<body>
    <div class="main-container">
        {% if modo == 'admin' %}
            <h1 style="color:var(--accent)">PAINEL ADMINISTRATIVO</h1>
            <input type="password" id="adm_pass" placeholder="CHAVE MASTER RENDER">
            <button class="btn-list" onclick="refreshList()">LISTAR CLIENTES / ATUALIZAR</button>
            <hr style="border:0.5px solid #334155; margin: 25px 0;">
            
            <div style="background:#0f172a; padding:20px; border-radius:10px;">
                <h3>CADASTRAR OU +CRÉDITOS</h3>
                <input type="text" id="new_n" placeholder="Nome da Empresa">
                <input type="text" id="new_p" placeholder="PIN de Acesso (6 a 8 dígitos)" maxlength="8">
                <input type="number" id="new_l" placeholder="Limite de Créditos">
                <button class="btn-add" onclick="saveClient()">SALVAR / ATUALIZAR LIMITE</button>
            </div>
            <div id="adm_results"></div>
        {% else %}
            <div id="view_login">
                <h1 style="text-align:center">SISTEMA QUANTUM</h1>
                <input type="password" id="c_pin" placeholder="DIGITE SEU PIN" maxlength="8">
                <button class="btn-list" style="width:100%" onclick="loginCli()">ENTRAR NO SISTEMA</button>
            </div>
            
            <div id="view_dash" style="display:none;">
                <h2 id="txt_empresa" style="color:var(--accent)"></h2>
                <div style="display:flex; justify-content:space-between; background:#0f172a; padding:15px; border-radius:8px;">
                    <span>Saldos: <b id="txt_uso"></b> / <b id="txt_limite"></b></span>
                    <button class="btn-list" onclick="window.print()" style="font-size:12px">🖨️ GERAR CERTIFICADOS PDF</button>
                </div>
                <br>
                <input type="text" id="c_obs" placeholder="Observação no Certificado (Lote/Equipamento)">
                <button class="btn-add" onclick="generateKey()">GERAR NOVA CHAVE QUANTUM</button>
                <br><br>
                <label><input type="checkbox" id="check_all" onclick="toggleAll(this)"> Selecionar Todas</label>
                <div id="cli_history"></div>
            </div>
        {% endif %}
    </div>

    <div id="area_impressao"></div>

    <script>
    // --- LÓGICA ADMIN ---
    async function refreshList() {
        const k = document.getElementById('adm_pass').value;
        const r = await fetch('/api/admin/list?k=' + k);
        if(!r.ok) return alert("Acesso Negado!");
        const data = await r.json();
        let html = "<table><tr><th>Empresa</th><th>PIN</th><th>Créditos</th><th>Ação</th></tr>";
        data.forEach(c => {
            html += `<tr><td>${c.n}</td><td>${c.p}</td><td>${c.u}/${c.l}</td>
            <td><button class="btn-del" onclick="deleteCli('${c.p}')">EXCLUIR</button></td></tr>`;
        });
        document.getElementById('adm_results').innerHTML = html + "</table>";
    }

    async function saveClient() {
        const payload = {
            k: document.getElementById('adm_pass').value,
            n: document.getElementById('new_n').value,
            p: document.getElementById('new_p').value,
            l: document.getElementById('new_l').value
        };
        await fetch('/api/admin/save', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload) });
        alert("Processado com Sucesso!");
        refreshList();
    }

    async function deleteCli(pin) {
        if(!confirm("Excluir cliente definitivamente?")) return;
        await fetch('/api/admin/delete', { 
            method:'POST', headers:{'Content-Type':'application/json'}, 
            body:JSON.stringify({k:document.getElementById('adm_pass').value, p:pin}) 
        });
        refreshList();
    }

    // --- LÓGICA CLIENTE ---
    let activePin = "";
    async function loginCli() {
        activePin = document.getElementById('c_pin').value;
        const r = await fetch('/api/cli/info?p=' + activePin);
        if(!r.ok) return alert("PIN INVÁLIDO");
        const d = await r.json();
        document.getElementById('view_login').style.display = 'none';
        document.getElementById('view_dash').style.display = 'block';
        document.getElementById('txt_empresa').innerText = d.n;
        document.getElementById('txt_uso').innerText = d.u;
        document.getElementById('txt_limite').innerText = d.l;
        let h = "";
        d.h.reverse().forEach((txt, i) => {
            const k = txt.split(' | ')[2];
            h += `<div class="item-chave" id="row-${i}">
                <input type="checkbox" class="sel-ck" data-key="${k}" onchange="this.parentElement.classList.toggle('selected')">
                <span style="margin-left:15px">${txt}</span>
            </div>`;
        });
        document.getElementById('cli_history').innerHTML = h;
    }

    async function generateKey() {
        const obs = document.getElementById('c_obs').value;
        const r = await fetch('/api/cli/generate', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({p:activePin, o:obs}) });
        if(r.ok) loginCli(); else alert("LIMITE ESGOTADO!");
    }

    function toggleAll(src) {
        document.querySelectorAll('.sel-ck').forEach(cb => {
            cb.checked = src.checked;
            cb.parentElement.classList.toggle('selected', src.checked);
        });
    }

    window.onbeforeprint = () => {
        const checks = document.querySelectorAll('.sel-ck:checked');
        let html = "";
        checks.forEach(c => {
            html += `<div class="cert-page"><div class="cert-box">
                <div class="cert-title">CERTIFICADO DE AUTENTICIDADE</div>
                <div class="cert-key">${c.getAttribute('data-key')}</div>
                <p>Software Quantum Original 2026</p>
            </div></div>`;
        });
        document.getElementById('area_impressao').innerHTML = html;
    };
    </script>
</body>
</html>
"""

@app.route('/')
def route_home(): return render_template_string(UI_V3, modo='cliente')

@app.route('/painel-secreto-kleber')
def route_admin(): return render_template_string(UI_V3, modo='admin')

# API ADMIN
@app.route('/api/admin/list')
def api_list():
    if request.args.get('k') != MASTER_KEY: return "Forbidden", 403
    conn = connect_db(); cur = conn.cursor()
    cur.execute("SELECT nome_empresa, pin_hash, acessos, limite FROM clientes ORDER BY id DESC")
    rows = cur.fetchall(); cur.close(); conn.close()
    return jsonify([{"n": r[0], "p": r[1], "u": r[2], "l": r[3]} for r in rows])

@app.route('/api/admin/save', methods=['POST'])
def api_save():
    d = request.json
    if d.get('k') != MASTER_KEY: return "Forbidden", 403
    conn = connect_db(); cur = conn.cursor()
    cur.execute('''INSERT INTO clientes (nome_empresa, pin_hash, limite) VALUES (%s, %s, %s)
                   ON CONFLICT (pin_hash) DO UPDATE SET limite = EXCLUDED.limite, nome_empresa = EXCLUDED.nome_empresa''', 
                (d['n'], d['p'], d['l']))
    conn.commit(); cur.close(); conn.close()
    return "OK"

@app.route('/api/admin/delete', methods=['POST'])
def api_delete():
    d = request.json
    if d.get('k') != MASTER_KEY: return "Forbidden", 403
    conn = connect_db(); cur = conn.cursor()
    cur.execute("DELETE FROM clientes WHERE pin_hash = %s", (d['p'],))
    conn.commit(); cur.close(); conn.close()
    return "OK"

# API CLIENTE
@app.route('/api/cli/info')
def api_info():
    p = request.args.get('p')
    conn = connect_db(); cur = conn.cursor()
    cur.execute("SELECT nome_empresa, acessos, limite, historico_chaves FROM clientes WHERE pin_hash = %s", (p,))
    c = cur.fetchone(); cur.close(); conn.close()
    if c: return jsonify({"n": c[0], "u": c[1], "l": c[2], "h": c[3]})
    return "Error", 404

@app.route('/api/cli/generate', methods=['POST'])
def api_generate():
    d = request.json
    conn = connect_db(); cur = conn.cursor()
    cur.execute("SELECT acessos, limite FROM clientes WHERE pin_hash = %s", (d['p'],))
    c = cur.fetchone()
    if c and c[0] < c[1]:
        key = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(30))
        txt = f"{datetime.datetime.now().strftime('%d/%m/%Y')} | {str(d.get('o','')).upper()} | {key}"
        cur.execute("UPDATE clientes SET acessos=acessos+1, historico_chaves=array_append(historico_chaves, %s) WHERE pin_hash=%s", (txt, d['p']))
        conn.commit(); cur.close(); conn.close()
        return "OK"
    return "Limit", 403

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))