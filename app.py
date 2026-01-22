import os, secrets, string, psycopg2, datetime, time, random, hashlib
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Configuração de Segurança
MASTER_KEY = os.environ.get('ADMIN_KEY', 'QUANTUM2026')

def get_db_connection(attempts=3):
    url = os.environ.get('DATABASE_URL')
    if url and url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    for i in range(attempts):
        try:
            return psycopg2.connect(url, sslmode='require', connect_timeout=5)
        except:
            time.sleep(2)
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
        conn.commit(); cur.close(); conn.close()

# Conteúdo do Conhecimento Quântico
CONHECIMENTO = {
    "freqs": ["432Hz", "528Hz", "639Hz", "741Hz", "852Hz", "963Hz"],
    "mantras": [
        "Eu sou um íman para milagres e abundância.",
        "Minha vibração está em harmonia com o universo.",
        "A cura flui através de mim agora.",
        "Eu confio no processo da vida e na minha intuição.",
        "Eu sou digno de prosperidade e amor infinito."
    ]
}

HTML_SISTEMA = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>SISTEMA QUANTUM SEED</title>
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Montserrat:wght@300;400;600&display=swap" rel="stylesheet">
    <style>
        :root { --gold: #c5a059; --bg: #05070a; --card: #0f172a; }
        body { background: var(--bg); color: white; font-family: 'Montserrat', sans-serif; margin: 0; padding: 20px; }
        .no-print { max-width: 900px; margin: auto; background: var(--card); padding: 30px; border-radius: 20px; border: 1px solid rgba(197,160,89,0.3); }
        h1, h2 { font-family: 'Cinzel', serif; color: var(--gold); text-align: center; }
        input { width: 100%; padding: 12px; margin: 10px 0; background: #1e293b; border: 1px solid #334155; color: white; border-radius: 8px; }
        .btn { width: 100%; padding: 15px; background: var(--gold); border: none; border-radius: 8px; font-weight: bold; cursor: pointer; text-transform: uppercase; margin-top: 10px; }
        
        .item-historico { background: rgba(255,255,255,0.03); padding: 15px; margin: 10px 0; border-radius: 10px; border-left: 4px solid var(--gold); display: flex; align-items: center; }
        .item-historico input { width: 25px; height: 25px; margin-right: 15px; }

        #print_area { display: none; }
        @media print {
            .no-print { display: none !important; }
            #print_area { display: block !important; }
            .cert-page { height: 100vh; page-break-after: always; display: flex; justify-content: center; align-items: center; background: #fff; }
            .cert-box { border: 10px double #c5a059; width: 85%; padding: 50px; text-align: center; color: #1a1a1a; position: relative; font-family: 'Cinzel', serif; }
            .cert-val { font-size: 38px; font-weight: bold; margin: 30px 0; border-top: 1px solid #c5a059; border-bottom: 1px solid #c5a059; padding: 15px 0; }
            .cert-mantra { font-family: 'Montserrat', sans-serif; font-style: italic; font-size: 18px; margin: 20px 0; }
        }
    </style>
</head>
<body>
    <div class="no-print">
        {% if modo == 'admin' %}
            <h1>ADMIN QUANTUM</h1>
            <input type="password" id="ak" placeholder="CHAVE MASTER">
            <button class="btn" onclick="listar()">Sincronizar</button>
            <div id="res_adm"></div>
            <hr style="opacity:0.1; margin:30px 0;">
            <input type="text" id="n" placeholder="Nome Terapeuta">
            <input type="text" id="p" placeholder="PIN (6-8 dig)" maxlength="8">
            <input type="number" id="l" placeholder="Limite de Ativações">
            <button class="btn" onclick="salvar()">Cadastrar</button>
        {% else %}
            <div id="login_area">
                <h1>PORTAL QUÂNTICO</h1>
                <input type="password" id="pin" placeholder="SEU PIN">
                <button class="btn" onclick="logar()">Acessar</button>
            </div>
            <div id="dash_area" style="display:none;">
                <h2 id="nome_terapeuta"></h2>
                <p style="text-align:center">Saldo: <span id="txt_saldo" style="color:var(--gold); font-weight:bold"></span></p>
                <input type="text" id="obs" placeholder="Nome do Paciente / Intenção">
                <button class="btn" onclick="gerar()">GERAR ATIVAÇÃO</button>
                <button class="btn" style="background:transparent; border:1px solid var(--gold); color:var(--gold)" onclick="window.print()">IMPRIMIR SELECIONADOS</button>
                <div id="lista_cli"></div>
            </div>
        {% endif %}
    </div>
    <div id="print_area"></div>

    <script>
    async function logar() {
        const p = document.getElementById('pin').value;
        const res = await fetch('/api/cli/info?p='+p);
        if(!res.ok) return alert("PIN Inválido");
        const d = await res.json();
        document.getElementById('login_area').style.display='none';
        document.getElementById('dash_area').style.display='block';
        document.getElementById('nome_terapeuta').innerText = d.n;
        document.getElementById('txt_saldo').innerText = (d.l - d.u) + " ativações";
        
        let h = "";
        d.h.reverse().forEach(item => {
            const pts = item.split(' | ');
            h += `<div class="item-historico">
                <input type="checkbox" class="ck" data-full="${item}">
                <div>
                    <div style="font-size:11px; color:var(--gold)">${pts[0]} - ${pts[2]}</div>
                    <div style="font-weight:bold">${pts[1]}</div>
                    <div style="font-size:12px; opacity:0.7">${pts[3]}</div>
                </div>
            </div>`;
        });
        document.getElementById('lista_cli').innerHTML = h;
    }

    async function gerar() {
        const p = document.getElementById('pin').value;
        const o = document.getElementById('obs').value;
        await fetch('/api/cli/generate', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({p:p, o:o}) });
        logar();
    }

    async function listar() {
        const k = document.getElementById('ak').value;
        const res = await fetch('/api/admin/list?k='+k);
        const data = await res.json();
        let h = "<table>";
        data.forEach(c => { h += `<tr><td>${c.n}</td><td>${c.u}/${c.l}</td></tr>`; });
        document.getElementById('res_adm').innerHTML = h + "</table>";
    }

    async function salvar() {
        const payload = { k:document.getElementById('ak').value, n:document.getElementById('n').value, p:document.getElementById('p').value, l:document.getElementById('l').value };
        await fetch('/api/admin/save', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload) });
        listar();
    }

    window.onbeforeprint = () => {
        let h = "";
        document.querySelectorAll('.ck:checked').forEach(c => {
            const p = c.getAttribute('data-full').split(' | ');
            h += `<div class="cert-page"><div class="cert-box">
                <div style="letter-spacing:5px; font-size:12px">SINTONIA VIBRACIONAL</div>
                <h1 style="color:#000">ATIVAÇÃO QUÂNTICA</h1>
                <p>Frequência gerada para:</p>
                <h2 style="color:#c5a059; font-size:30px">${p[1]}</h2>
                <div class="cert-val">${p[2]}</div>
                <div class="cert-mantra">"${p[3]}"</div>
                <div style="font-size:11px; margin-top:40px">Válido até: ${p[4]}</div>
                <div style="margin-top:20px"><img src="https://api.qrserver.com/v1/create-qr-code/?size=60x60&data=https://www.youtube.com/results?search_query=solfeggio+${p[2].split(' ')[0]}" /></div>
            </div></div>`;
        });
        document.getElementById('print_area').innerHTML = h;
    };
    </script>
</body>
</html>
"""

@app.route('/')
def r_h(): return render_template_string(HTML_SISTEMA, modo='cliente')

@app.route('/painel-secreto-kleber')
def r_a(): return render_template_string(HTML_SISTEMA, modo='admin')

@app.route('/api/admin/list')
def api_l():
    if request.args.get('k') != MASTER_KEY: return "Err", 403
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT nome_empresa, pin_hash, acessos, limite FROM clientes")
    r = cur.fetchall(); cur.close(); conn.close()
    return jsonify([{"n": x[0], "p": x[1], "u": x[2], "l": x[3]} for x in r])

@app.route('/api/admin/save', methods=['POST'])
def api_s():
    d = request.json
    if d.get('k') != MASTER_KEY: return "Err", 403
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO clientes (nome_empresa, pin_hash, limite) VALUES (%s, %s, %s) ON CONFLICT (pin_hash) DO UPDATE SET limite = EXCLUDED.limite, nome_empresa = EXCLUDED.nome_empresa", (d['n'], d['p'], d['l']))
    conn.commit(); cur.close(); conn.close()
    return "OK"

@app.route('/api/cli/info')
def api_i():
    p = request.args.get('p')
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT nome_empresa, acessos, limite, historico_chaves FROM clientes WHERE pin_hash = %s", (p,))
    c = cur.fetchone(); cur.close(); conn.close()
    if c: return jsonify({"n": c[0], "u": c[1], "l": c[2], "h": c[3]})
    return "Err", 404

@app.route('/api/cli/generate', methods=['POST'])
def api_g():
    d = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT acessos, limite FROM clientes WHERE pin_hash = %s", (d['p'],))
    c = cur.fetchone()
    if c and c[0] < c[1]:
        f = random.choice(CONHECIMENTO["freqs"])
        m = random.choice(CONHECIMENTO["mantras"])
        val = (datetime.datetime.now() + datetime.timedelta(days=21)).strftime('%d/%m/%Y')
        res = f"{datetime.datetime.now().strftime('%d/%m/%Y')} | {str(d.get('o','GERAL')).upper()} | {f} | {m} | {val}"
        cur.execute("UPDATE clientes SET acessos=acessos+1, historico_chaves=array_append(historico_chaves, %s) WHERE pin_hash=%s", (res, d['p']))
        conn.commit(); cur.close(); conn.close()
        return "OK"
    return "Err", 403

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))