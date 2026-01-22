import os, secrets, string, psycopg2, datetime, time, random
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# --- BUSCA A CHAVE NO RENDER (Tenta Maiúscula ou Minúscula) ---
MASTER_KEY = os.environ.get('ADMIN_KEY') or os.environ.get('admin_key')

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
def setup_db_and_migrations():
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
        # Garante coluna de histórico para tabelas antigas
        cur.execute("""
            DO $$ BEGIN 
                ALTER TABLE clientes ADD COLUMN IF NOT EXISTS historico_chaves TEXT[] DEFAULT '{}';
            EXCEPTION WHEN duplicate_column THEN NULL; END $$;
        """)
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
        .no-print { max-width: 900px; margin: auto; background: var(--card); padding: 30px; border-radius: 20px; border: 1px solid rgba(197,160,89,0.3); box-shadow: 0 10px 40px rgba(0,0,0,0.8); }
        h1, h2 { font-family: 'Cinzel', serif; color: var(--gold); text-align: center; }
        input { width: 100%; padding: 12px; margin: 10px 0; background: #1e293b; border: 1px solid #334155; color: white; border-radius: 8px; font-size:16px; }
        .btn { width: 100%; padding: 15px; background: var(--gold); border: none; border-radius: 8px; font-weight: bold; cursor: pointer; text-transform: uppercase; color: black; transition: 0.3s; }
        .btn:hover { background: #e2c08d; }
        
        /* Dashboard do Cliente */
        .info-bar { display: flex; justify-content: space-around; background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; margin-bottom: 20px; border: 1px solid var(--gold); }
        .item-historico { background: rgba(255,255,255,0.03); padding: 15px; margin: 10px 0; border-radius: 10px; border-left: 5px solid var(--gold); display: flex; align-items: center; }
        .item-historico input[type="checkbox"] { width: 25px; height: 25px; margin-right: 15px; cursor: pointer; }

        #print_area { display: none; }
        @media print {
            .no-print { display: none !important; }
            #print_area { display: block !important; }
            .cert-page { height: 100vh; page-break-after: always; display: flex; justify-content: center; align-items: center; background: #fff; }
            .cert-box { border: 12px double #c5a059; width: 80%; padding: 50px; text-align: center; color: #1a1a1a; font-family: 'Cinzel', serif; }
            .cert-val { font-size: 40px; font-weight: bold; margin: 30px 0; border-top: 2px solid #c5a059; border-bottom: 2px solid #c5a059; padding: 20px 0; }
        }
    </style>
</head>
<body>
    <div class="no-print">
        {% if modo == 'admin' %}
            <h1>PAINEL MASTER</h1>
            <input type="password" id="ak" placeholder="DIGITE SUA ADMIN_KEY">
            <button class="btn" onclick="listar()">ACESSAR LISTA DE CLIENTES</button>
            <div id="res_adm" style="margin-top:20px"></div>
            <hr style="opacity:0.2; margin:30px 0;">
            <h3>CADASTRAR TERAPEUTA</h3>
            <input type="text" id="n" placeholder="NOME DO TERAPEUTA">
            <input type="text" id="p" placeholder="PIN (6 A 8 CARACTERES)">
            <input type="number" id="l" placeholder="LIMITE DE ATIVAÇÕES">
            <button class="btn" onclick="salvar()">ATIVAR ACESSO</button>
        {% else %}
            <div id="login_area">
                <h1>PORTAL QUÂNTICO</h1>
                <input type="password" id="pin" placeholder="SEU PIN">
                <button class="btn" onclick="logar()">ENTRAR</button>
            </div>
            <div id="dash_area" style="display:none;">
                <h2 id="nome_terapeuta" style="margin-bottom:10px"></h2>
                
                <div class="info-bar">
                    <div>Saldo: <strong id="txt_saldo" style="color:var(--gold); font-size:20px"></strong></div>
                    <div>Status: <strong style="color:#4ade80">Sintonizado</strong></div>
                </div>

                <input type="text" id="obs" placeholder="NOME DO PACIENTE / INTENÇÃO">
                <button class="btn" onclick="gerar()">GERAR NOVA FREQUÊNCIA</button>
                <button class="btn" style="background:transparent; border:1px solid var(--gold); color:var(--gold); margin-top:10px" onclick="window.print()">IMPRIMIR SELECIONADOS</button>
                
                <h3 style="margin-top:30px; border-bottom:1px solid rgba(197,160,89,0.3); padding-bottom:10px">Histórico de Ativações</h3>
                <div id="lista_cli"></div>
            </div>
        {% endif %}
    </div>
    <div id="print_area"></div>

    <script>
    async function listar() {
        const k = document.getElementById('ak').value;
        const res = await fetch(`/api/admin/list?k=${k}`);
        if(!res.ok) return alert("Erro: Chave Master Inválida.");
        const data = await res.json();
        let h = "<table style='width:100%'><tr><th>Nome</th><th>Uso/Limite</th><th>Ação</th></tr>";
        data.forEach(c => {
            h += `<tr><td>${c.n}</td><td>${c.u} / ${c.l}</td><td><button onclick="deletar('${c.p}')">Excluir</button></td></tr>`;
        });
        document.getElementById('res_adm').innerHTML = h + "</table>";
    }

    async function salvar() {
        const k = document.getElementById('ak').value;
        const payload = { k:k, n:document.getElementById('n').value, p:document.getElementById('p').value, l:parseInt(document.getElementById('l').value) };
        const res = await fetch('/api/admin/save', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload) });
        if(res.ok) { alert("Cliente Ativado!"); listar(); } else { alert("Erro ao salvar."); }
    }

    async function deletar(pin) {
        const k = document.getElementById('ak').value;
        if(confirm("Deseja remover este cliente?")) {
            await fetch('/api/admin/delete', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({k:k, p:pin}) });
            listar();
        }
    }

    async function logar() {
        const p = document.getElementById('pin').value;
        const res = await fetch(`/api/cli/info?p=${p}`, {cache: "no-store"});
        if(!res.ok) return alert("PIN Não Encontrado");
        const d = await res.json();
        
        document.getElementById('login_area').style.display='none';
        document.getElementById('dash_area').style.display='block';
        document.getElementById('nome_terapeuta').innerText = "Bem-vindo, " + d.n;
        
        // EXIBIÇÃO DO SALDO
        document.getElementById('txt_saldo').innerText = (d.l - d.u);
        
        let h = "";
        if(d.h) d.h.reverse().forEach(item => {
            const pts = item.split(' | ');
            h += `<div class="item-historico">
                <input type="checkbox" class="ck" data-full="${item}">
                <div>
                    <div style="font-size:11px; color:var(--gold)">${pts[0]} - ${pts[2]}</div>
                    <div style="font-weight:bold; font-size:16px">${pts[1]}</div>
                    <div style="font-size:13px; font-style:italic; opacity:0.8">"${pts[3]}"</div>
                </div>
            </div>`;
        });
        document.getElementById('lista_cli').innerHTML = h || "Nenhuma ativação realizada.";
    }

    async function gerar() {
        const p = document.getElementById('pin').value;
        const o = document.getElementById('obs').value || "GERAL";
        const res = await fetch('/api/cli/generate', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({p:p, o:o}) });
        if(res.ok) { document.getElementById('obs').value = ""; logar(); } else { alert("Limite atingido."); }
    }

    window.onbeforeprint = () => {
        let h = "";
        document.querySelectorAll('.ck:checked').forEach(c => {
            const p = c.getAttribute('data-full').split(' | ');
            h += `<div class="cert-page"><div class="cert-box">
                <div style="letter-spacing:5px; font-size:12px">SINTONIA VIBRACIONAL</div>
                <h1>ATIVAÇÃO QUÂNTICA</h1>
                <p>Paciente: <b style="font-size:22px">${p[1]}</b></p>
                <div class="cert-val">${p[2]}</div>
                <p style="font-size:20px"><i>"${p[3]}"</i></p>
                <p><small>Válido por 21 dias (Até: ${p[4]})</small></p>
                <div style="margin-top:20px"><img src="https://api.qrserver.com/v1/create-qr-code/?size=60x60&data=https://www.youtube.com/results?search_query=solfeggio+${p[2].split(' ')[0]}" /></div>
            </div></div>`;
        });
        document.getElementById('print_area').innerHTML = h;
    };
    </script>
</body>
</html>
"""

# --- ROTAS DA API ---

@app.route('/')
def r_h(): return render_template_string(HTML_SISTEMA, modo='cliente')

@app.route('/painel-secreto-kleber')
def r_a(): return render_template_string(HTML_SISTEMA, modo='admin')

@app.route('/api/admin/list')
def api_l():
    k = request.args.get('k')
    if not MASTER_KEY or k != MASTER_KEY: return "Err", 403
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT nome_empresa, pin_hash, acessos, limite FROM clientes ORDER BY id DESC")
    r = cur.fetchall(); cur.close(); conn.close()
    return jsonify([{"n": x[0], "p": x[1], "u": x[2], "l": x[3]} for x in r])

@app.route('/api/admin/save', methods=['POST'])
def api_s():
    d = request.json
    if not MASTER_KEY or d.get('k') != MASTER_KEY: return "Err", 403
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO clientes (nome_empresa, pin_hash, limite) 
        VALUES (%s, %s, %s) 
        ON CONFLICT (pin_hash) DO UPDATE SET limite = EXCLUDED.limite, nome_empresa = EXCLUDED.nome_empresa
    ''', (d['n'], d['p'], d['l']))
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