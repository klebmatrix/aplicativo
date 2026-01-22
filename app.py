import os, secrets, string, psycopg2, datetime
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
# CORS configurado para permitir a conexão da Extensão Chrome
CORS(app, resources={r"/api/*": {"origins": "*"}})

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

UI_FINAL = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>SISTEMA QUANTUM V4</title>
    <style>
        :root { --accent: #38bdf8; --bg: #0b1120; --card: #1e293b; }
        body { background: var(--bg); color: white; font-family: sans-serif; padding: 20px; }
        .container { max-width: 900px; margin: auto; background: var(--card); padding: 25px; border-radius: 15px; border: 1px solid #334155; }
        input { padding: 12px; margin: 5px; background: #0f172a; border: 1px solid #334155; color: white; border-radius: 8px; }
        button { padding: 12px 20px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; color: white; }
        .btn-green { background: #22c55e; } .btn-blue { background: #0284c7; } .btn-red { background: #ef4444; }
        
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border-bottom: 1px solid #334155; padding: 12px; text-align: left; }
        .item { background: #0f172a; padding: 15px; margin: 10px 0; border-radius: 8px; display: flex; align-items: center; border: 1px solid #334155; }
        .item.selected { border-color: var(--accent); background: #1e3a5a; }

        @media print {
            .no-print { display: none !important; }
            .cert-page { page-break-after: always; height: 95vh; display: flex; justify-content: center; align-items: center; }
            .cert-box { border: 12px solid black; width: 85%; padding: 50px; text-align: center; color: black; }
            .cert-key { background: #f9f9f9 !important; padding: 20px; font-family: monospace; font-size: 22px; font-weight: bold; margin: 20px 0; border: 1px solid #ccc; }
        }
    </style>
</head>
<body>
    <div class="container no-print">
        {% if modo == 'admin' %}
            <h1>PAINEL ADMIN</h1>
            <input type="password" id="ak" placeholder="Chave Master">
            <button class="btn-blue" onclick="listar()">LISTAR CLIENTES</button>
            <hr style="border:0.5px solid #334155; margin:20px 0;">
            <h3>CADASTRAR / +CREDITOS</h3>
            <input type="text" id="n" placeholder="Empresa">
            <input type="text" id="p" placeholder="PIN (6-8 dig)" maxlength="8">
            <input type="number" id="l" placeholder="Limite">
            <button class="btn-green" onclick="salvar()">SALVAR / ATUALIZAR</button>
            <div id="res_adm"></div>
        {% else %}
            <div id="login">
                <h1>QUANTUM LOGIN</h1>
                <input type="password" id="pin" placeholder="SEU PIN">
                <button class="btn-blue" onclick="logar()">ENTRAR</button>
            </div>
            <div id="painel" style="display:none;">
                <h2 id="emp" style="color:var(--accent)"></h2>
                <p>Uso: <b id="u"></b> / Limite: <b id="lim"></b></p>
                <input type="text" id="o" placeholder="Observação">
                <button class="btn-green" onclick="gerar()">GERAR CHAVE</button>
                <button class="btn-blue" onclick="window.print()">🖨️ IMPRIMIR CERTIFICADOS</button>
                <button style="background:#475569" onclick="excel()">📊 EXCEL</button>
                <br><br>
                <label><input type="checkbox" onclick="tudo(this)"> Selecionar Todos</label>
                <div id="lista_cli"></div>
            </div>
        {% endif %}
    </div>
    <div id="print_area" class="print-only"></div>

    <script>
    // ADMIN
    async function listar() {
        const k = document.getElementById('ak').value;
        const r = await fetch('/api/admin/list?k='+k);
        if(!r.ok) return alert("Erro");
        const d = await r.json();
        let h = "<table><tr><th>Empresa</th><th>PIN</th><th>Créditos</th><th>Ação</th></tr>";
        d.forEach(c => { h += `<tr><td>${c.n}</td><td>${c.p}</td><td>${c.u}/${c.l}</td><td><button class="btn-red" onclick="excluir('${c.p}')">EXCLUIR</button></td></tr>`; });
        document.getElementById('res_adm').innerHTML = h + "</table>";
    }
    async function salvar() {
        await fetch('/api/admin/save', { method:'POST', headers:{'Content-Type':'application/json'}, 
            body: JSON.stringify({k:document.getElementById('ak').value, n:document.getElementById('n').value, p:document.getElementById('p').value, l:document.getElementById('l').value}) 
        });
        listar();
    }
    async function excluir(p) {
        if(!confirm("Excluir?")) return;
        await fetch('/api/admin/delete', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({k:document.getElementById('ak').value, p:p}) });
        listar();
    }

    // CLIENTE
    let pAtivo = "";
    async function logar() {
        pAtivo = document.getElementById('pin').value;
        const r = await fetch('/api/cli/info?p='+pAtivo);
        if(!r.ok) return alert("Erro");
        const d = await r.json();
        document.getElementById('login').style.display='none';
        document.getElementById('painel').style.display='block';
        document.getElementById('emp').innerText = d.n;
        document.getElementById('u').innerText = d.u;
        document.getElementById('lim').innerText = d.l;
        let h = "";
        d.h.reverse().forEach((t, i) => {
            h += `<div class="item" id="row-${i}"><input type="checkbox" class="ck" data-key="${t.split(' | ')[2]}" data-full="${t}" onchange="this.parentElement.classList.toggle('selected')"><span style="margin-left:15px">${t}</span></div>`;
        });
        document.getElementById('lista_cli').innerHTML = h;
    }
    async function gerar() {
        await fetch('/api/cli/generate', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({p:pAtivo, o:document.getElementById('o').value}) });
        logar();
    }
    function tudo(s) { document.querySelectorAll('.ck').forEach(c => { c.checked = s.checked; c.parentElement.classList.toggle('selected', s.checked); }); }
    function excel() {
        let csv = "DATA;OBS;CHAVE\\n";
        document.querySelectorAll('.ck:checked').forEach(c => { csv += c.getAttribute('data-full').replaceAll(" | ", ";") + "\\n"; });
        const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([csv], {type:'text/csv'})); a.download = "chaves.csv"; a.click();
    }
    window.onbeforeprint = () => {
        let h = "";
        document.querySelectorAll('.ck:checked').forEach(c => {
            h += `<div class="cert-page"><div class="cert-box"><h2>Certificado de Autenticidade</h2><div class="cert-key">${c.getAttribute('data-key')}</div><p>Quantum Software 2026 - Original</p></div></div>`;
        });
        document.getElementById('print_area').innerHTML = h;
    };
    </script>
</body>
</html>
"""

@app.route('/')
def r_h(): return render_template_string(UI_FINAL, modo='cliente')

@app.route('/painel-secreto-kleber')
def r_a(): return render_template_string(UI_FINAL, modo='admin')

@app.route('/api/admin/list')
def api_l():
    if request.args.get('k') != MASTER_KEY: return "Err", 403
    conn = connect_db(); cur = conn.cursor()
    cur.execute("SELECT nome_empresa, pin_hash, acessos, limite FROM clientes ORDER BY id DESC")
    r = cur.fetchall(); cur.close(); conn.close()
    return jsonify([{"n": x[0], "p": x[1], "u": x[2], "l": x[3]} for x in r])

@app.route('/api/admin/save', methods=['POST'])
def api_s():
    d = request.json
    if d.get('k') != MASTER_KEY: return "Err", 403
    conn = connect_db(); cur = conn.cursor()
    cur.execute("INSERT INTO clientes (nome_empresa, pin_hash, limite) VALUES (%s, %s, %s) ON CONFLICT (pin_hash) DO UPDATE SET limite = EXCLUDED.limite, nome_empresa = EXCLUDED.nome_empresa", (d['n'], d['p'], d['l']))
    conn.commit(); cur.close(); conn.close()
    return "OK"

@app.route('/api/admin/delete', methods=['POST'])
def api_d():
    d = request.json
    if d.get('k') != MASTER_KEY: return "Err", 403
    conn = connect_db(); cur = conn.cursor()
    cur.execute("DELETE FROM clientes WHERE pin_hash = %s", (d['p'],))
    conn.commit(); cur.close(); conn.close()
    return "OK"

@app.route('/api/cli/info')
def api_i():
    p = request.args.get('p')
    conn = connect_db(); cur = conn.cursor()
    cur.execute("SELECT nome_empresa, acessos, limite, historico_chaves FROM clientes WHERE pin_hash = %s", (p,))
    c = cur.fetchone(); cur.close(); conn.close()
    if c: return jsonify({"n": c[0], "u": c[1], "l": c[2], "h": c[3]})
    return "Err", 404

@app.route('/api/cli/generate', methods=['POST'])
def api_g():
    d = request.json
    conn = connect_db(); cur = conn.cursor()
    cur.execute("SELECT acessos, limite FROM clientes WHERE pin_hash = %s", (d['p'],))
    c = cur.fetchone()
    if c and c[0] < c[1]:
        k = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(30))
        t = f"{datetime.datetime.now().strftime('%d/%m/%Y')} | {str(d.get('o','')).upper()} | {k}"
        cur.execute("UPDATE clientes SET acessos=acessos+1, historico_chaves=array_append(historico_chaves, %s) WHERE pin_hash=%s", (t, d['p']))
        conn.commit(); cur.close(); conn.close()
        return "OK"
    return "Err", 403

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))