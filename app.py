import os, secrets, string, psycopg2, datetime
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Pega as chaves do Render
ADMIN_KEY = os.environ.get('admin_key') or os.environ.get('ADMIN_KEY')

def get_db_connection():
    url = os.environ.get('DATABASE_URL')
    if url and url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    try:
        return psycopg2.connect(url, sslmode='require')
    except:
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
        conn.commit()
        cur.close(); conn.close()

HTML_SISTEMA = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>SISTEMA QUANTUM 2026</title>
    <style>
        :root { --blue: #38bdf8; --dark: #0b1120; --card: #1e293b; }
        body { background: var(--dark); color: white; font-family: sans-serif; padding: 20px; }
        .container { max-width: 900px; margin: auto; background: var(--card); padding: 25px; border-radius: 15px; }
        input, select { padding: 10px; margin: 5px; background: #0f172a; border: 1px solid #334155; color: white; border-radius: 5px; }
        button { padding: 10px 15px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; color: white; }
        .btn-green { background: #22c55e; } .btn-blue { background: #0284c7; } .btn-red { background: #ef4444; }
        .hist-item { background: #0f172a; padding: 10px; margin: 5px 0; border-radius: 8px; display: flex; align-items: center; }
        .hist-item.selected { border: 1px solid var(--blue); background: #1e293b; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #334155; padding: 10px; text-align: left; }
        @media print {
            .no-print, button, input, h1 { display: none !important; }
            .hist-item:not(.selected) { display: none !important; }
            body { background: white; color: black; }
            .hist-item { border: 1px solid black; }
        }
    </style>
</head>
<body>
    <div class="container">
        {% if tipo == 'admin' %}
            <h1>PAINEL MASTER</h1>
            <input type="password" id="mk" placeholder="Chave Admin">
            <button class="btn-blue" onclick="listar()">ATUALIZAR LISTA</button>
            <hr>
            <h3>NOVO CLIENTE / EDITAR</h3>
            <input type="text" id="n" placeholder="Empresa">
            <input type="text" id="p" placeholder="PIN (6-8 dig)" maxlength="8">
            <input type="number" id="l" placeholder="Créditos" value="100">
            <button class="btn-green" onclick="add()">SALVAR/ATUALIZAR</button>
            <div id="lista_admin"></div>
        {% else %}
            <div id="login_box">
                <h1>QUANTUM LOGIN</h1>
                <input type="password" id="pin" placeholder="Seu PIN" maxlength="8">
                <button class="btn-blue" onclick="entrar()">ENTRAR</button>
            </div>
            <div id="dash" style="display:none;">
                <h2 id="c_nome"></h2>
                <p>Uso: <b id="uso"></b> / Limite: <b id="total"></b></p>
                <div class="no-print">
                    <input type="text" id="obs" placeholder="Observação">
                    <button class="btn-green" onclick="gerar()">GERAR CHAVE</button>
                    <button class="btn-blue" onclick="window.print()">🖨️ IMPRIMIR SELECIONADOS</button>
                    <button style="background:#475569" onclick="exportar()">📊 EXCEL</button>
                    <br><br>
                    <label><input type="checkbox" onclick="selTudo(this)"> Selecionar Todos</label>
                </div>
                <div id="hist_list"></div>
            </div>
        {% endif %}
    </div>

    <script>
    // --- ADMIN ---
    async function listar() {
        const k = document.getElementById('mk').value;
        const res = await fetch('/admin/listar?key=' + k);
        if(!res.ok) return alert("Erro de acesso");
        const dados = await res.json();
        let h = "<table><tr><th>Empresa</th><th>PIN</th><th>Uso/Limite</th><th>Ações</th></tr>";
        dados.forEach(c => {
            h += `<tr><td>${c.n}</td><td>${c.p}</td><td>${c.u}/${c.l}</td>
            <td><button class="btn-red" onclick="excluir('${c.p}')">Excluir</button></td></tr>`;
        });
        document.getElementById('lista_admin').innerHTML = h + "</table>";
    }
    async function add() {
        const k = document.getElementById('mk').value;
        await fetch('/admin/cadastrar', {
            method:'POST', headers:{'Content-Type':'application/json'},
            body: JSON.stringify({key:k, n:document.getElementById('n').value, p:document.getElementById('p').value, l:document.getElementById('l').value})
        });
        listar();
    }
    async function excluir(p) {
        if(!confirm("Deletar cliente?")) return;
        const k = document.getElementById('mk').value;
        await fetch('/admin/deletar', {method:'DELETE', headers:{'Content-Type':'application/json'}, body:JSON.stringify({key:k, pin:p})});
        listar();
    }

    // --- CLIENTE ---
    let pinAtivo = "";
    async function entrar() {
        pinAtivo = document.getElementById('pin').value;
        const res = await fetch('/v1/cliente/dados?pin=' + pinAtivo);
        if(!res.ok) return alert("PIN incorreto");
        const d = await res.json();
        document.getElementById('login_box').style.display='none';
        document.getElementById('dash').style.display='block';
        document.getElementById('c_nome').innerText = d.empresa;
        document.getElementById('uso').innerText = d.usadas;
        document.getElementById('total').innerText = d.limite;
        let h = "";
        d.hist.reverse().forEach((t, i) => {
            h += `<div class="hist-item" id="r-${i}">
                <input type="checkbox" class="ck" onchange="document.getElementById('r-${i}').classList.toggle('selected')">
                <span style="margin-left:10px">${t}</span>
            </div>`;
        });
        document.getElementById('hist_list').innerHTML = h;
    }
    async function gerar() {
        await fetch('/v1/cliente/gerar', {
            method:'POST', headers:{'Content-Type':'application/json'},
            body: JSON.stringify({pin:pinAtivo, obs:document.getElementById('obs').value})
        });
        entrar();
    }
    function selTudo(src) {
        document.querySelectorAll('.ck').forEach(c => {
            c.checked = src.checked;
            c.parentElement.classList.toggle('selected', src.checked);
        });
    }
    function exportar() {
        let csv = "DATA;LOTE;CHAVE\\n";
        document.querySelectorAll('.hist-item.selected span').forEach(s => {
            csv += s.innerText.replaceAll(" | ", ";") + "\\n";
        });
        const blob = new Blob([csv], {type:'text/csv'});
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = "relatorio.csv";
        a.click();
    }
    </script>
</body>
</html>
"""

@app.route('/')
def home(): return render_template_string(HTML_SISTEMA, tipo='login')

@app.route('/painel-secreto-kleber')
def admin_page(): return render_template_string(HTML_SISTEMA, tipo='admin')

@app.route('/admin/listar')
def list_adm():
    if request.args.get('key') != ADMIN_KEY: return "Erro", 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT nome_empresa, pin_hash, acessos, limite FROM clientes ORDER BY id DESC")
    r = cur.fetchall(); cur.close(); conn.close()
    return jsonify([{"n": x[0], "p": x[1], "u": x[2], "l": x[3]} for x in r])

@app.route('/admin/cadastrar', methods=['POST'])
def add_adm():
    d = request.json
    if d.get('key') != ADMIN_KEY: return "Erro", 403
    conn = get_db_connection(); cur = conn.cursor()
    # ON CONFLICT: Se o PIN já existir, ele atualiza o Limite (+Créditos)
    cur.execute('''INSERT INTO clientes (nome_empresa, pin_hash, limite) VALUES (%s, %s, %s)
                   ON CONFLICT (pin_hash) DO UPDATE SET limite = EXCLUDED.limite, nome_empresa = EXCLUDED.nome_empresa''', 
                (d['n'], d['p'], d['l']))
    conn.commit(); cur.close(); conn.close()
    return "OK"

@app.route('/admin/deletar', methods=['DELETE'])
def del_adm():
    d = request.json
    if d.get('key') != ADMIN_KEY: return "Erro", 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("DELETE FROM clientes WHERE pin_hash = %s", (d['pin'],))
    conn.commit(); cur.close(); conn.close()
    return "OK"

@app.route('/v1/cliente/dados')
def get_cli():
    pin = request.args.get('pin')
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT nome_empresa, acessos, limite, historico_chaves FROM clientes WHERE pin_hash = %s", (pin,))
    c = cur.fetchone(); cur.close(); conn.close()
    if c: return jsonify({"empresa": c[0], "usadas": c[1], "limite": c[2], "hist": c[3]})
    return "Erro", 401

@app.route('/v1/cliente/gerar', methods=['POST'])
def gen_key():
    d = request.json
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT acessos, limite FROM clientes WHERE pin_hash = %s", (d['pin'],))
    c = cur.fetchone()
    if c and c[0] < c[1]:
        nk = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(15))
        reg = f"{datetime.datetime.now().strftime('%d/%m/%Y %H:%M')} | {d.get('obs','GERAL').upper()} | {nk}"
        cur.execute("UPDATE clientes SET acessos=acessos+1, historico_chaves=array_append(historico_chaves, %s) WHERE pin_hash=%s", (reg, d['pin']))
        conn.commit(); cur.close(); conn.close()
        return "OK"
    return "Limite atingido", 403

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))