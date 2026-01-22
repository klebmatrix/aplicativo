import os, secrets, string, psycopg2, datetime, time
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

MASTER_KEY = os.environ.get('admin_key') or os.environ.get('ADMIN_KEY')

def connect_db_with_retry(attempts=3, delay=2):
    url = os.environ.get('DATABASE_URL')
    if url and url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    for i in range(attempts):
        try:
            conn = psycopg2.connect(url, sslmode='require', connect_timeout=5)
            return conn
        except:
            time.sleep(delay)
    return None

@app.before_request
def setup_database():
    conn = connect_db_with_retry()
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

UI_VIBRACIONAL = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>SISTEMA NUMEROLOGIA QUÂNTICA</title>
    <style>
        :root { --gold: #d4af37; --bg: #05070a; --card: #0f172a; }
        body { background: var(--bg); color: white; font-family: 'Georgia', serif; padding: 20px; }
        .container { max-width: 850px; margin: auto; background: var(--card); padding: 30px; border-radius: 20px; border: 1px solid var(--gold); }
        input { padding: 12px; margin: 5px; background: #1e293b; border: 1px solid #334155; color: white; border-radius: 8px; width: 250px; }
        button { padding: 12px 25px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; text-transform: uppercase; }
        .btn-gold { background: var(--gold); color: black; }
        .btn-red { background: #991b1b; color: white; font-size: 10px; }
        .item { background: #1e293b; padding: 15px; margin: 10px 0; border-radius: 10px; border-left: 4px solid var(--gold); display: flex; align-items: center; }
        
        @media print {
            .no-print { display: none !important; }
            .cert-page { page-break-after: always; height: 98vh; display: flex; justify-content: center; align-items: center; background: white; }
            .cert-box { border: 10px double #d4af37; width: 80%; padding: 60px; text-align: center; color: #1a1a1a; position: relative; }
            .cert-title { font-size: 32px; color: #856404; margin-bottom: 10px; }
            .cert-val { background: #fdf6e3 !important; padding: 25px; font-size: 28px; font-weight: bold; border: 1px solid #d4af37; margin: 30px 0; letter-spacing: 3px; }
            .cert-footer { font-size: 12px; color: #666; font-style: italic; }
        }
    </style>
</head>
<body>
    <div class="container no-print">
        {% if modo == 'admin' %}
            <h1 style="color:var(--gold)">PAINEL MASTER QUÂNTICO</h1>
            <input type="password" id="ak" placeholder="Chave Master">
            <button class="btn-gold" onclick="listar()">Ver Portadores</button>
            <hr style="border:0.5px solid var(--gold); margin:30px 0;">
            <h3>CADASTRAR TERAPEUTA / +FLUXO</h3>
            <input type="text" id="n" placeholder="Nome/Empresa">
            <input type="text" id="p" placeholder="PIN (6-8 dig)" maxlength="8">
            <input type="number" id="l" placeholder="Qtd. Ativações">
            <button class="btn-gold" onclick="salvar()">Consagrar Acesso</button>
            <div id="res_adm"></div>
        {% else %}
            <div id="login">
                <h1 style="text-align:center; color:var(--gold)">SINTONIA QUÂNTICA</h1>
                <div style="text-align:center">
                    <input type="password" id="pin" placeholder="SEU PIN" style="width:80%">
                    <br><br>
                    <button class="btn-gold" onclick="logar()">Acessar Frequências</button>
                </div>
            </div>
            <div id="painel" style="display:none;">
                <h2 id="emp" style="color:var(--gold)"></h2>
                <p>Ativações Realizadas: <b id="u"></b> / Limite Contratado: <b id="lim"></b></p>
                <input type="text" id="o" placeholder="Nome do Cliente ou Intenção">
                <button class="btn-gold" onclick="gerar()">GERAR ATIVAÇÃO</button>
                <button onclick="window.print()">🖨️ IMPRIMIR CERTIFICADOS</button>
                <br><br>
                <label><input type="checkbox" onclick="tudo(this)"> Selecionar Todos</label>
                <div id="lista_cli"></div>
            </div>
        {% endif %}
    </div>
    <div id="print_area"></div>

    <script>
    async function listar() {
        const k = document.getElementById('ak').value;
        const r = await fetch('/api/admin/list?k='+k);
        if(!r.ok) return alert("Erro");
        const d = await r.json();
        let h = "<table><tr><th>Portador</th><th>PIN</th><th>Fluxo</th><th>Ação</th></tr>";
        d.forEach(c => { h += `<tr><td>${c.n}</td><td>${c.p}</td><td>${c.u}/${c.l}</td><td><button class="btn-red" onclick="excluir('${c.p}')">REMOVER</button></td></tr>`; });
        document.getElementById('res_adm').innerHTML = h + "</table>";
    }
    async function salvar() {
        const k = document.getElementById('ak').value;
        await fetch('/api/admin/save', { method:'POST', headers:{'Content-Type':'application/json'}, 
            body: JSON.stringify({k:k, n:document.getElementById('n').value, p:document.getElementById('p').value, l:document.getElementById('l').value}) 
        });
        listar();
    }
    async function excluir(p) {
        if(confirm("Remover?")) {
            await fetch('/api/admin/delete', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({k:document.getElementById('ak').value, p:p}) });
            listar();
        }
    }
    let pAtivo = "";
    async function logar() {
        pAtivo = document.getElementById('pin').value;
        const r = await fetch('/api/cli/info?p='+pAtivo);
        if(!r.ok) return alert("PIN Não Sintonizado");
        const d = await r.json();
        document.getElementById('login').style.display='none';
        document.getElementById('painel').style.display='block';
        document.getElementById('emp').innerText = "Terapeuta: " + d.n;
        document.getElementById('u').innerText = d.u;
        document.getElementById('lim').innerText = d.l;
        let h = "";
        d.h.reverse().forEach((t, i) => {
            h += `<div class="item"><input type="checkbox" class="ck" data-key="${t.split(' | ')[2]}"><span style="margin-left:15px">${t}</span></div>`;
        });
        document.getElementById('lista_cli').innerHTML = h;
    }
    async function gerar() {
        await fetch('/api/cli/generate', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({p:pAtivo, o:document.getElementById('o').value}) });
        logar();
    }
    function tudo(s) { document.querySelectorAll('.ck').forEach(c => c.checked = s.checked); }
    window.onbeforeprint = () => {
        let h = "";
        document.querySelectorAll('.ck:checked').forEach(c => {
            h += `<div class="cert-page"><div class="cert-box"><div class="cert-title">CERTIFICADO DE ATIVAÇÃO</div><p>ASSINATURA VIBRACIONAL QUÂNTICA</p><div class="cert-val">${c.getAttribute('data-key')}</div><div class="cert-footer">Este código representa uma frequência única gerada para sua harmonia pessoal.</div></div></div>`;
        });
        document.getElementById('print_area').innerHTML = h;
    };
    </script>
</body>
</html>
"""

@app.route('/')
def r_h(): return render_template_string(UI_VIBRACIONAL, modo='cliente')

@app.route('/painel-secreto-kleber')
def r_a(): return render_template_string(UI_VIBRACIONAL, modo='admin')

@app.route('/api/admin/list')
def api_l():
    if request.args.get('k') != MASTER_KEY: return "Err", 403
    conn = connect_db_with_retry()
    cur = conn.cursor()
    cur.execute("SELECT nome_empresa, pin_hash, acessos, limite FROM clientes ORDER BY id DESC")
    r = cur.fetchall(); cur.close(); conn.close()
    return jsonify([{"n": x[0], "p": x[1], "u": x[2], "l": x[3]} for x in r])

@app.route('/api/admin/save', methods=['POST'])
def api_s():
    d = request.json
    if d.get('k') != MASTER_KEY: return "Err", 403
    conn = connect_db_with_retry()
    cur = conn.cursor()
    cur.execute("INSERT INTO clientes (nome_empresa, pin_hash, limite) VALUES (%s, %s, %s) ON CONFLICT (pin_hash) DO UPDATE SET limite = EXCLUDED.limite, nome_empresa = EXCLUDED.nome_empresa", (d['n'], d['p'], d['l']))
    conn.commit(); cur.close(); conn.close()
    return "OK"

@app.route('/api/admin/delete', methods=['POST'])
def api_d():
    d = request.json
    if d.get('k') != MASTER_KEY: return "Err", 403
    conn = connect_db_with_retry()
    cur = conn.cursor()
    cur.execute("DELETE FROM clientes WHERE pin_hash = %s", (d['p'],))
    conn.commit(); cur.close(); conn.close()
    return "OK"

@app.route('/api/cli/info')
def api_i():
    p = request.args.get('p')
    conn = connect_db_with_retry()
    cur = conn.cursor()
    cur.execute("SELECT nome_empresa, acessos, limite, historico_chaves FROM clientes WHERE pin_hash = %s", (p,))
    c = cur.fetchone(); cur.close(); conn.close()
    if c: return jsonify({"n": c[0], "u": c[1], "l": c[2], "h": c[3]})
    return "Err", 404

@app.route('/api/cli/generate', methods=['POST'])
def api_g():
    d = request.json
    conn = connect_db_with_retry()
    cur = conn.cursor()
    cur.execute("SELECT acessos, limite FROM clientes WHERE pin_hash = %s", (d['p'],))
    c = cur.fetchone()
    if c and c[0] < c[1]:
        freqs = ["432Hz", "528Hz", "639Hz", "741Hz", "852Hz", "963Hz"]
        sel_f = secrets.choice(freqs)
        n_quantico = f"{sel_f} | {''.join(secrets.choice(string.digits) for _ in range(3))}.{secrets.choice(string.digits*3)}.{secrets.choice(string.digits*2)}"
        t = f"{datetime.datetime.now().strftime('%d/%m/%Y')} | {str(d.get('o','GERAL')).upper()} | {n_quantico}"
        cur.execute("UPDATE clientes SET acessos=acessos+1, historico_chaves=array_append(historico_chaves, %s) WHERE pin_hash=%s", (t, d['p']))
        conn.commit(); cur.close(); conn.close()
        return "OK"
    return "Err", 403

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))