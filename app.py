import os, psycopg2, datetime, time, random
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Chave mestra definida nas variáveis de ambiente do Render
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
        "A proteção divina envolve este campo energético agora.",
        "Caminhos abertos e prosperidade fluindo em abundância.",
        "Toda negatividade é transmutada em luz pura.",
        "A saúde perfeita se manifesta em cada célula.",
        "Harmonia cósmica estabelecida neste ambiente."
    ]
}

HTML_SISTEMA = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>QUANTUM SEED - ELITE VIBRACIONAL</title>
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Montserrat:wght@300;400;600&display=swap" rel="stylesheet">
    <style>
        :root { --gold: #b38b4d; --bg: #fdfcf9; --text: #1a1a1a; --border: #eaddca; }
        body { background: var(--bg); color: var(--text); font-family: 'Montserrat', sans-serif; margin: 0; padding: 20px; }
        
        .glass-card { background: #fff; border: 1px solid var(--border); border-radius: 20px; padding: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.05); margin-bottom: 20px; }
        h1, h2 { font-family: 'Cinzel', serif; color: var(--gold); text-align: center; }
        
        input, select { width: 100%; padding: 14px; margin: 8px 0; border: 1px solid var(--border); border-radius: 8px; box-sizing: border-box; font-size: 16px; }
        .btn { padding: 15px 20px; border-radius: 8px; border: none; cursor: pointer; font-weight: bold; text-transform: uppercase; transition: 0.3s; }
        .btn-gold { background: var(--gold); color: white; width: 100%; font-family: 'Cinzel'; }
        .btn-gold:hover { background: #8e6d3a; }
        
        /* Dashboard Admin */
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th { color: var(--gold); border-bottom: 2px solid var(--gold); padding: 10px; text-align: left; font-size: 12px; }
        td { padding: 12px; border-bottom: 1px solid var(--border); font-size: 14px; }

        /* Dashboard Cliente */
        .energy-bar { background: #eee; height: 12px; border-radius: 6px; margin: 15px 0; overflow: hidden; border: 1px solid var(--border); }
        .energy-fill { height: 100%; background: linear-gradient(90deg, #d4af37, var(--gold)); width: 0%; transition: 1.5s ease; }
        .history-item { background: #fff; border: 1px solid var(--border); padding: 15px; margin: 10px 0; border-radius: 12px; display: flex; align-items: center; }

        /* CERTIFICADO - CONFIGURAÇÃO DE IMPRESSÃO */
        #print_area { display: none; }
        @media print {
            body { background: white !important; }
            .no-print { display: none !important; }
            #print_area { display: block !important; width: 100%; }
            .cert-page { height: 100vh; display: flex; justify-content: center; align-items: center; page-break-after: always; background: white; }
            .cert-box { border: 12px double var(--gold); width: 85%; padding: 50px; text-align: center; color: black; font-family: 'Cinzel', serif; background: white; }
            .cert-val { font-size: 42px; font-weight: bold; color: var(--gold); margin: 25px 0; border-top: 2px solid var(--gold); border-bottom: 2px solid var(--gold); padding: 15px 0; }
        }
    </style>
</head>
<body>
    <div class="no-print" style="max-width: 900px; margin: auto;">
        {% if modo == 'admin' %}
            <div class="glass-card">
                <h1>PAINEL MASTER QUANTUM</h1>
                <input type="password" id="ak" placeholder="CHAVE DE ACESSO ADMIN" style="max-width:300px; display:block; margin:auto; text-align:center;">
                <button class="btn btn-gold" onclick="listar()" style="max-width:200px; display:block; margin: 15px auto;">SINCRONIZAR REDE</button>
                
                <div id="lista_admin"></div>

                <hr style="border:0; border-top:1px solid var(--border); margin:40px 0;">
                
                <h2>GERENCIAR TERAPEUTA</h2>
                <input type="text" id="n" placeholder="Nome do Cliente/Terapeuta">
                <input type="text" id="p" placeholder="PIN de Acesso (6-8 caracteres)">
                <input type="number" id="l" placeholder="Limite de Créditos">
                <select id="st">
                    <option value="Ativo">Status: ATIVO</option>
                    <option value="VIP">Status: VIP (ILIMITADO)</option>
                    <option value="Bloqueado">Status: BLOQUEADO</option>
                </select>
                <button class="btn btn-gold" onclick="salvar()">SALVAR CONFIGURAÇÃO</button>
            </div>
        {% else %}
            <div class="glass-card" style="max-width: 450px; margin: auto;">
                <h1>QUANTUM SEED</h1>
                <div id="login_area">
                    <input type="password" id="pin" placeholder="PIN DE ACESSO" maxlength="8">
                    <button class="btn btn-gold" onclick="logar()">SINTONIZAR PORTAL</button>
                </div>
                <div id="dash_area" style="display:none;">
                    <h2 id="nome_cli" style="font-size:18px; margin-bottom:5px;"></h2>
                    <div style="display:flex; justify-content:space-between; font-size:11px; font-weight:600;">
                        <span>FLUXO DE ENERGIA</span>
                        <span id="txt_saldo"></span>
                    </div>
                    <div class="energy-bar"><div id="fill" class="energy-fill"></div></div>
                    
                    <input type="text" id="intencao" placeholder="DESCREVA A INTENÇÃO CÓSMICA">
                    <button class="btn btn-gold" id="btn_gerar" onclick="gerar()">MANIFESTAR INTENÇÃO</button>
                    
                    <button onclick="window.print()" style="background:none; border:none; color:var(--gold); width:100%; margin-top:20px; cursor:pointer; font-weight:bold; text-decoration:underline;">IMPRIMIR CERTIFICADOS SELECIONADOS</button>
                    
                    <div id="lista_cli" style="margin-top:25px;"></div>
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
        let h = "<table><tr><th>TERAPEUTA</th><th>STATUS/SALDO</th><th>AÇÕES</th></tr>";
        data.forEach(c => {
            h += `<tr>
                <td><b>${c.n}</b><br><small>${c.p}</small></td>
                <td>${c.s}<br>${c.u}/${c.l}</td>
                <td>
                    <button class="btn" style="background:#f0f0f0; padding:5px 10px;" onclick="addCr('${c.p}',50)">+50</button>
                    <button class="btn" style="background:#ffebee; color:red; padding:5px 10px;" onclick="remover('${c.p}')">X</button>
                </td>
            </tr>`;
        });
        document.getElementById('lista_admin').innerHTML = h + "</table>";
    }

    async function addCr(pin, q) {
        await fetch('/api/admin/add_credit', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({k:document.getElementById('ak').value, p:pin, q:q}) });
        listar();
    }

    async function salvar() {
        const payload = { k:document.getElementById('ak').value, n:document.getElementById('n').value, p:document.getElementById('p').value, l:parseInt(document.getElementById('l').value), s:document.getElementById('st').value };
        await fetch('/api/admin/save', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload) });
        listar();
    }

    async function remover(pin) {
        if(confirm("Excluir definitivamente?")) {
            await fetch('/api/admin/delete', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({k:document.getElementById('ak').value, p:pin}) });
            listar();
        }
    }

    // --- LÓGICA CLIENTE ---
    async function logar() {
        const p = document.getElementById('pin').value;
        const res = await fetch(`/api/cli/info?p=${p}`);
        if(!res.ok) return alert("PIN Inválido.");
        const d = await res.json();
        if(d.s === 'Bloqueado') return alert("Acesso Bloqueado.");

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
                <input type="checkbox" class="ck" data-full="${item}" style="margin-right:12px; width:20px; height:20px;">
                <div>
                    <div style="font-weight:700; color:var(--gold);">${pts[1]}</div>
                    <div style="font-size:11px;">${pts[2]} • Validade: ${pts[4]}</div>
                </div>
            </div>`;
        });
        document.getElementById('lista_cli').innerHTML = h;
    }

    async function gerar() {
        const p = document.getElementById('pin').value;
        const i = document.getElementById('intencao').value;
        if(!i) return alert("Defina a Intenção Cósmica.");
        const res = await fetch('/api/cli/generate', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({p:p, i:i}) });
        if(res.ok) { document.getElementById('intencao').value = ""; logar(); } else { alert("Saldo insuficiente."); }
    }

    window.onbeforeprint = () => {
        let h = "";
        document.querySelectorAll('.ck:checked').forEach(c => {
            const p = c.getAttribute('data-full').split(' | ');
            h += `<div class="cert-page"><div class="cert-box">
                <p style="letter-spacing:5px; font-size:14px;">CONSAGRAÇÃO VIBRACIONAL</p>
                <h1 style="font-size:40px; margin:15px 0;">QUANTUM SEED</h1>
                <p style="font-size:18px; margin-top:35px;">Intenção Cósmica Manifestada:</p>
                <h2 style="font-size:32px; color:#b38b4d;">${p[1]}</h2>
                <div class="cert-val">${p[2]}</div>
                <p style="font-style:italic; font-size:22px; padding: 0 20px;">"${p[3]}"</p>
                <p style="margin-top:50px; font-size:15px;">Ciclo de Ativação Válido até: <b>${p[4]}</b></p>
                <p style="font-size:10px; opacity:0.6; margin-top:15px;">A renovação deve ser feita ao fim do ciclo para manutenção da egrégora.</p>
            </div></div>`;
        });
        document.getElementById('print_area').innerHTML = h;
    };
    </script>
</body>
</html>
"""

# --- ROTAS DA API ---

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
        intencao_texto = str(d.get('i','GERAL')).upper()
        # LÓGICA DE DIAS: Saúde 90, Outros 180
        dias = 180
        if any(x in intencao_texto for x in ["SAUDE", "CURA", "ENFERMO", "HOSPITAL", "SAÚDE"]):
            dias = 90
            
        f = random.choice(CONHECIMENTO["freqs"])
        m = random.choice(CONHECIMENTO["mantras"])
        val = (datetime.datetime.now() + datetime.timedelta(days=dias)).strftime('%d/%m/%Y')
        res = f"{datetime.datetime.now().strftime('%d/%m/%Y')} | {intencao_texto} | {f} | {m} | {val}"
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