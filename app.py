import os, secrets, string, psycopg2
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def get_admin_key():
    return (os.environ.get('ADMIN_KEY') or '').strip()

def get_db_connection():
    url = os.environ.get('DATABASE_URL')
    if not url: return None
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return psycopg2.connect(url, sslmode='require')

HTML_SISTEMA = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SISTEMA QUANTUM | ADMIN</title>
    <style>
        :root { --blue: #38bdf8; --dark: #0b1120; --card: #1e293b; --red: #ef4444; --green: #22c55e; --gold: #fbbf24; }
        body { background: var(--dark); color: white; font-family: 'Segoe UI', sans-serif; padding: 20px; }
        .container { max-width: 1100px; margin: auto; background: var(--card); padding: 30px; border-radius: 15px; border: 1px solid #334155; }
        
        /* FORMULÁRIO ADMIN */
        .admin-box { background: #0f172a; padding: 20px; border-radius: 12px; margin-bottom: 25px; border-left: 5px solid var(--blue); }
        input, select { padding: 10px; background: #1e293b; border: 1px solid #334155; color: white; border-radius: 6px; outline: none; margin-right: 5px; }
        
        /* TABELA PROFISSIONAL */
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th { background: #334155; color: var(--blue); padding: 12px; text-align: left; font-size: 13px; text-transform: uppercase; }
        td { padding: 12px; border-bottom: 1px solid #334155; font-size: 14px; }
        tr:hover { background: rgba(56, 189, 248, 0.05); }

        button { padding: 8px 12px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; color: white; transition: 0.2s; font-size: 12px; }
        button:hover { opacity: 0.8; transform: translateY(-1px); }
        
        .badge { padding: 3px 8px; border-radius: 4px; font-size: 10px; font-weight: bold; }
        .badge-vip { background: var(--gold); color: black; }
        .badge-cr { background: var(--blue); color: white; }

        /* IMPRESSÃO DO CERTIFICADO */
        .certificado { display: none; }
        @media print {
            .no-print { display: none !important; }
            body { background: white !important; color: black !important; }
            .certificado { display: block !important; border: 10px double #000; padding: 40px; text-align: center; page-break-inside: avoid; margin-bottom: 50px; }
            .c-code { font-family: monospace; font-size: 24px; font-weight: bold; border: 2px solid #000; padding: 10px; display: inline-block; margin: 20px 0; }
        }
    </style>
</head>
<body>
    <div class="container">
        {% if tipo == 'admin' %}
            <h1 style="color:var(--blue); margin-top:0;">GERENCIADOR DE ACESSOS</h1>
            
            <div class="no-print">
                <input type="password" id="mestre" placeholder="ADMIN_KEY" style="width:200px">
                <button style="background:var(--blue)" onclick="listar()">CONECTAR AO BANCO</button>
            </div>

            <div class="admin-box no-print" style="margin-top:20px;">
                <h3 style="margin-top:0">Cadastrar Novo Cliente</h3>
                <input type="text" id="n" placeholder="Nome da Empresa">
                <input type="text" id="p" placeholder="PIN (6 dígitos)" maxlength="6">
                <input type="number" id="l" placeholder="Créditos (Ex: 20)">
                <button style="background:var(--green)" onclick="cadastrar()">CRIAR CONTA</button>
            </div>

            <div id="lista_admin">
                <p style="color:#94a3b8">Digite a ADMIN_KEY e clique em Conectar.</p>
            </div>

        {% else %}
            <div id="login_area" style="text-align:center">
                <h1>AUTENTICADOR QUANTUM</h1>
                <input type="text" id="pin_cli" placeholder="PIN de 6 dígitos" maxlength="6" style="width:300px; text-align:center; font-size:20px;">
                <br><br>
                <button style="background:var(--blue); width:320px; height:50px;" onclick="entrar()">ENTRAR NO SISTEMA</button>
            </div>

            <div id="dashboard" style="display:none;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h2 id="emp_nome" style="color:var(--blue)"></h2>
                    <button style="background:var(--gold); color:black" onclick="window.print()">🖨️ IMPRIMIR SELECIONADOS</button>
                </div>
                <div id="lista_historico"></div>
            </div>
        {% endif %}
    </div>

    <script>
    // FUNÇÕES DO ADMIN
    async function listar() {
        const k = document.getElementById('mestre').value;
        const res = await fetch('/admin/listar?key=' + k);
        if(!res.ok) return alert("Erro de Acesso!");
        const dados = await res.json();
        let h = `<table><tr><th>Empresa</th><th>PIN</th><th>Plano / Consumo</th><th>Ações</th></tr>`;
        dados.forEach(c => {
            const isVip = c.l === -1;
            h += `<tr>
                <td><b>${c.n}</b></td>
                <td style="font-family:monospace">${c.p}</td>
                <td><span class="badge ${isVip?'badge-vip':'badge-cr'}">${isVip?'ASSINANTE':'LIMITE: '+c.l}</span><br>
                    <small>Usado: ${c.u}</small></td>
                <td>
                    <button style="background:var(--gold); color:black" onclick="setVip('${c.p}')">Set VIP</button>
                    <button style="background:var(--blue)" onclick="addCr('${c.p}')">+ Crédito</button>
                    <button style="background:var(--red)" onclick="del('${c.p}')">Excluir</button>
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
    async function addCr(p) { const q=prompt("Quantos Créditos?"); if(q) await fetch('/admin/credito', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({key:document.getElementById('mestre').value, pin:p, qtd:q})}); listar(); }
    async function del(p) { if(confirm("Deletar cliente?")) await fetch('/admin/deletar', {method:'DELETE', headers:{'Content-Type':'application/json'}, body:JSON.stringify({key:document.getElementById('mestre').value, pin:p})}); listar(); }

    // FUNÇÕES DO CLIENTE
    async function entrar() {
        const p = document.getElementById('pin_cli').value;
        const res = await fetch('/v1/cliente/dados?pin=' + p);
        const d = await res.json();
        document.getElementById('login_area').style.display='none';
        document.getElementById('dashboard').style.display='block';
        document.getElementById('emp_nome').innerText = d.empresa;
        
        let h_tela = ""; let h_cert = "";
        [...d.hist].reverse().forEach((t, i) => {
            const pt = t.split(' | ');
            h_tela += `<div class="hist-item" id="row-${i}" style="background:#0f172a; padding:15px; margin-top:10px; border-radius:8px; display:flex; justify-content:space-between; cursor:pointer;" onclick="this.classList.toggle('selected')">
                <span><b>${pt[1]}</b></span> <span style="font-family:monospace; color:var(--blue)">${pt[2]}</span>
            </div>`;
            h_cert += `<div class="certificado">
                <h2>CERTIFICADO DE AUTENTICAÇÃO</h2>
                <p>Módulo: ${pt[1]}</p>
                <div class="c-code">${pt[2]}</div>
                <p>Validação Original Sistema Quantum</p>
                <div style="margin-top:40px; border-top:1px solid #000; width:200px; margin-left:auto; margin-right:auto;">Assinatura</div>
            </div>`;
        });
        document.getElementById('lista_historico').innerHTML = h_tela + h_cert;
    }
    </script>
</body>
</html>
"""

# --- BACKEND (ROTAS ADMIN E CLIENTE) ---
@app.route('/')
def home(): return render_template_string(HTML_SISTEMA)

@app.route('/painel-secreto-kleber')
def admin_page(): return render_template_string(HTML_SISTEMA, tipo='admin')

@app.route('/admin/listar')
def list_adm():
    if request.args.get('key', '').strip() != get_admin_key(): return jsonify([]), 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT nome_empresa, pin_hash, acessos, limite, ativo FROM clientes ORDER BY id DESC")
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
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("UPDATE clientes SET limite = %s WHERE pin_hash = %s", (int(d['qtd']), d['pin']))
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
    cur.execute("SELECT nome_empresa, acessos, limite, historico_chaves, ativo FROM clientes WHERE pin_hash = %s", (pin,))
    c = cur.fetchone(); cur.close(); conn.close()
    if c: return jsonify({"empresa": c[0], "usadas": c[1], "limite": c[2], "hist": c[3]})
    return jsonify({"e": 401}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))