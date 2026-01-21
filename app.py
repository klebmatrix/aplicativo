import os, secrets, string, psycopg2
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- SEGURANÇA E CONEXÃO ---
def get_admin_key():
    return (os.environ.get('ADMIN_KEY') or '').strip()

def get_db_connection():
    url = os.environ.get('DATABASE_URL')
    if not url: return None
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return psycopg2.connect(url, sslmode='require')

# --- INTERFACE VISUAL ---
HTML_SISTEMA = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QUANTUM | SISTEMA DE AUTENTICAÇÃO</title>
    <style>
        :root { --blue: #38bdf8; --dark: #0b1120; --card: #1e293b; --gold: #fbbf24; --green: #22c55e; --red: #ef4444; }
        body { background: var(--dark); color: white; font-family: 'Segoe UI', sans-serif; padding: 20px; margin: 0; }
        .container { max-width: 1000px; margin: auto; background: var(--card); padding: 25px; border-radius: 15px; border: 1px solid #334155; }
        
        /* ADMIN TABLE */
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th { background: #0f172a; color: var(--blue); padding: 12px; text-align: left; }
        td { padding: 12px; border-bottom: 1px solid #334155; }
        .btn { padding: 8px 12px; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; color: white; margin: 2px; }
        
        /* CLIENTE DASHBOARD */
        .box-gerar { background: #0f172a; padding: 20px; border-radius: 12px; border: 1px solid var(--blue); margin: 20px 0; }
        input { padding: 12px; background: #1e293b; border: 1px solid #334155; color: white; border-radius: 8px; margin-right: 10px; }
        .hist-item { background: #16213e; padding: 15px; margin-top: 10px; border-radius: 10px; display: flex; justify-content: space-between; align-items: center; border: 1px solid transparent; cursor: pointer; }
        .hist-item.selected { border-color: var(--gold); background: #1e3a8a; }

        /* CERTIFICADO IMPRESSÃO */
        .certificado { display: none; }
        @media print {
            .no-print { display: none !important; }
            body { background: white !important; color: black !important; }
            .certificado { 
                display: block !important; border: 8px double #000; padding: 40px; text-align: center; 
                margin-bottom: 50px; page-break-inside: avoid; background: white;
            }
            .cert-code { font-family: monospace; font-size: 26px; border: 2px solid #000; padding: 10px; display: inline-block; margin: 20px 0; }
        }
    </style>
</head>
<body>
    <div class="container">
        {% if tipo == 'admin' %}
            <h1 style="color:var(--blue)">NÚCLEO ADMINISTRADOR</h1>
            <div class="no-print">
                <input type="password" id="mestre" placeholder="Chave Mestra Admin">
                <button class="btn" style="background:var(--blue)" onclick="listar()">CARREGAR BANCO</button>
            </div>
            
            <div id="form_add" class="no-print" style="margin-top:20px; padding:15px; background:#0f172a; border-radius:10px;">
                <h3>Cadastrar Novo Cliente</h3>
                <input type="text" id="n" placeholder="Nome Empresa">
                <input type="text" id="p" placeholder="PIN 6 dígitos" maxlength="6">
                <input type="number" id="l" placeholder="Créditos (Ex: 20)">
                <button class="btn" style="background:var(--green)" onclick="cadastrar()">CRIAR CONTA</button>
            </div>

            <div id="lista_admin"></div>

        {% else %}
            <div id="login_area" style="text-align:center; padding: 50px 0;">
                <h1>PAINEL DE AUTENTICAÇÃO</h1>
                <input type="text" id="pin_cli" placeholder="PIN DE 6 DÍGITOS" maxlength="6" style="width:280px; text-align:center; font-size:20px;">
                <br><br>
                <button class="btn" style="background:var(--blue); width:305px; height:50px;" onclick="entrar()">ENTRAR NO SISTEMA</button>
            </div>

            <div id="dashboard" style="display:none;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h2 id="emp_nome" style="color:var(--blue); margin:0;"></h2>
                    <button class="btn no-print" style="background:var(--gold); color:black" onclick="window.print()">🖨️ IMPRIMIR SELECIONADOS</button>
                </div>

                <div id="box_gerar" class="box-gerar no-print">
                    <p style="margin-top:0"><b>Gerar Novo Código de Autenticação:</b></p>
                    <input type="text" id="obs" placeholder="Referência (Ex: Lote 01)" style="width:50%">
                    <button class="btn" style="background:var(--green); width:30%" onclick="gerar()">GERAR AGORA</button>
                </div>

                <div id="lista_historico"></div>
            </div>
        {% endif %}
    </div>

    <script>
    // --- LÓGICA ADMIN ---
    async function listar() {
        const k = document.getElementById('mestre').value;
        const res = await fetch('/admin/listar?key=' + k);
        if(!res.ok) return alert("Acesso Negado!");
        const dados = await res.json();
        let h = `<table><tr><th>Empresa</th><th>PIN</th><th>Plano</th><th>Ações</th></tr>`;
        dados.forEach(c => {
            const isVip = c.l === -1;
            h += `<tr>
                <td><b>${c.n}</b></td>
                <td style="font-family:monospace">${c.p}</td>
                <td><span style="color:${isVip?'var(--gold)':'var(--blue)'}">${isVip?'ASSINANTE VIP':c.u+' / '+c.l}</span></td>
                <td>
                    <button class="btn" style="background:var(--gold); color:black" onclick="setVip('${c.p}')">VIP</button>
                    <button class="btn" style="background:var(--blue)" onclick="addCr('${c.p}')">Créditos</button>
                    <button class="btn" style="background:var(--red)" onclick="del('${c.p}')">X</button>
                </td>
            </tr>`;
        });
        document.getElementById('lista_admin').innerHTML = h + "</table>";
    }

    async function cadastrar() {
        const k = document.getElementById('mestre').value;
        const body = {key:k, n:document.getElementById('n').value, p:document.getElementById('p').value, l:document.getElementById('l').value};
        await fetch('/admin/cadastrar', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(body)});
        listar();
    }
    async function setVip(p) { await fetch('/admin/assinatura', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({key:document.getElementById('mestre').value, pin:p})}); listar(); }
    async function addCr(p) { const q=prompt("Qual o novo limite total?"); if(q) await fetch('/admin/credito', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({key:document.getElementById('mestre').value, pin:p, qtd:q})}); listar(); }
    async function del(p) { if(confirm("Deletar cliente?")) await fetch('/admin/deletar', {method:'DELETE', headers:{'Content-Type':'application/json'}, body:JSON.stringify({key:document.getElementById('mestre').value, pin:p})}); listar(); }

    // --- LÓGICA CLIENTE ---
    async function entrar() {
        const p = document.getElementById('pin_cli').value;
        const res = await fetch('/v1/cliente/dados?pin=' + p);
        if(!res.ok) return alert("PIN Inválido!");
        const d = await res.json();
        
        document.getElementById('login_area').style.display='none';
        document.getElementById('dashboard').style.display='block';
        document.getElementById('emp_nome').innerText = d.empresa;
        
        let h_tela = ""; let h_cert = "";
        [...d.hist].reverse().forEach((t, i) => {
            const pt = t.split(' | ');
            h_tela += `<div class="hist-item" id="row-${i}" onclick="this.classList.toggle('selected')">
                <span><b>${pt[1]}</b></span> <span style="font-family:monospace; color:var(--blue)">${pt[2]}</span>
            </div>`;
            h_cert += `<div class="certificado">
                <h1>CERTIFICADO DE AUTENTICAÇÃO</h1>
                <p>Referência: ${pt[1]}</p>
                <div class="cert-code">${pt[2]}</div>
                <p>Validação Oficial Quantum - ${new Date().toLocaleDateString()}</p>
                <div style="margin-top:50px; border-top:1px solid #000; width:250px; margin-left:auto; margin-right:auto;">Assinatura do Responsável</div>
            </div>`;
        });
        document.getElementById('lista_historico').innerHTML = h_tela + h_cert;
    }

    async function gerar() {
        const p = document.getElementById('pin_cli').value;
        const res = await fetch('/v1/cliente/gerar', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({pin:p, obs:document.getElementById('obs').value || "GERAL"})});
        if(res.ok) entrar(); else alert("Sem saldo ou bloqueado!");
    }
    </script>
</body>
</html>
"""

# --- BACKEND PYTHON ---
@app.route('/')
def home(): return render_template_string(HTML_SISTEMA)

@app.route('/painel-secreto-kleber')
def admin_page(): return render_template_string(HTML_SISTEMA, tipo='admin')

@app.route('/admin/listar')
def list_adm():
    if request.args.get('key', '').strip() != get_admin_key(): return jsonify([]), 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT nome_empresa, pin_hash, acessos, limite FROM clientes ORDER BY id DESC")
    r = cur.fetchall(); cur.close(); conn.close()
    return jsonify([{"n": x[0], "p": x[1], "u": x[2], "l": x[3]} for x in r])

@app.route('/admin/cadastrar', methods=['POST'])
def add_adm():
    d = request.json
    if d.get('key', '').strip() != get_admin_key(): return jsonify({"e":403}), 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("INSERT INTO clientes (nome_empresa, pin_hash, limite, historico_chaves, ativo, acessos) VALUES (%s, %s, %s, '{}', TRUE, 0)", (d['n'], d['p'], d['l']))
    conn.commit(); cur.close(); conn.close(); return jsonify({"ok": True})

@app.route('/admin/assinatura', methods=['POST'])
def sub_adm():
    d = request.json
    if d.get('key', '').strip() != get_admin_key(): return jsonify({"e":403}), 403
    conn = get_db_connection(); cur = conn.cursor(); cur.execute("UPDATE clientes SET limite = -1 WHERE pin_hash = %s", (d['pin'],))
    conn.commit(); cur.close(); conn.close(); return jsonify({"ok": True})

@app.route('/admin/credito', methods=['POST'])
def cr_adm():
    d = request.json
    if d.get('key', '').strip() != get_admin_key(): return jsonify({"e":403}), 403
    conn = get_db_connection(); cur = conn.cursor(); cur.execute("UPDATE clientes SET limite = %s WHERE pin_hash = %s", (int(d['qtd']), d['pin']))
    conn.commit(); cur.close(); conn.close(); return jsonify({"ok": True})

@app.route('/admin/deletar', methods=['DELETE'])
def del_adm():
    d = request.json
    if d.get('key', '').strip() != get_admin_key(): return jsonify({"e":403}), 403
    conn = get_db_connection(); cur = conn.cursor(); cur.execute("DELETE FROM clientes WHERE pin_hash = %s", (d['pin'],))
    conn.commit(); cur.close(); conn.close(); return jsonify({"ok": True})

@app.route('/v1/cliente/dados')
def get_cli():
    pin = request.args.get('pin')
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT nome_empresa, acessos, limite, historico_chaves FROM clientes WHERE pin_hash = %s", (pin,))
    c = cur.fetchone(); cur.close(); conn.close()
    if c: return jsonify({"empresa": c[0], "usadas": c[1], "limite": c[2], "hist": c[3]})
    return jsonify({"e": 401}), 401

@app.route('/v1/cliente/gerar', methods=['POST'])
def gen_key():
    d = request.json
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT acessos, limite, ativo FROM clientes WHERE pin_hash = %s", (d['pin'],))
    c = cur.fetchone()
    if c and (c[1] == -1 or c[0] < c[1]):
        nk = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(25))
        reg = f"X | {d['obs'].upper()} | {nk}"
        cur.execute("UPDATE clientes SET acessos=acessos+1, historico_chaves=array_append(historico_chaves, %s) WHERE pin_hash=%s", (reg, d['pin']))
        conn.commit(); cur.close(); conn.close(); return jsonify({"ok": True})
    cur.close(); conn.close(); return jsonify({"e": 403}), 403

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))