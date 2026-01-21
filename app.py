import os, secrets, string, psycopg2
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- SEGURANÇA ---
def get_admin_key():
    return (os.environ.get('ADMIN_KEY') or '').strip()

def get_db_connection():
    url = os.environ.get('DATABASE_URL')
    if not url: return None
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return psycopg2.connect(url, sslmode='require')

# --- INTERFACE ÚNICA ---
HTML_SISTEMA = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QUANTUM CONTROL</title>
    <style>
        :root { --blue: #38bdf8; --dark: #0b1120; --card: #1e293b; --red: #ef4444; --green: #22c55e; --gold: #fbbf24; }
        body { background: var(--dark); color: white; font-family: sans-serif; padding: 20px; }
        .container { max-width: 1100px; margin: auto; background: var(--card); padding: 30px; border-radius: 20px; border: 1px solid #334155; }
        input, select { padding: 12px; background: #0f172a; border: 1px solid #334155; color: white; border-radius: 8px; outline: none; margin: 5px; }
        button { padding: 10px 15px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; color: white; margin: 2px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; background: #0f172a; }
        th, td { padding: 12px; border: 1px solid #334155; text-align: center; }
        .badge { padding: 4px 8px; border-radius: 5px; font-size: 11px; font-weight: bold; }
        .badge-sub { background: var(--gold); color: black; }
        .badge-cre { background: var(--blue); color: white; }
        .progress-container { background: #0f172a; border-radius: 10px; height: 12px; margin: 15px 0; border: 1px solid #334155; overflow: hidden; }
        .progress-bar { height: 100%; background: var(--blue); width: 0%; transition: 0.5s; }
        .infinite-bar { background: linear-gradient(90deg, var(--blue), var(--gold), var(--blue)); background-size: 200%; animation: move 2s linear infinite; width: 100% !important; }
        @keyframes move { 0% {background-position: 0%} 100% {background-position: 200%} }
        .hist-item { background: #0f172a; padding: 12px; margin-top: 5px; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; border: 1px solid transparent; cursor: pointer; }
        .hist-item.selected { border-color: var(--blue); background: #1e3a8a; }
        @media print { .no-print { display: none !important; } .hist-item:not(.selected) { display: none !important; } body { background: white; color: black; } }
    </style>
</head>
<body>
    <div class="container">
        {% if tipo == 'admin' %}
            <h1 style="color:var(--blue)">PAINEL ADMINISTRATIVO</h1>
            <div class="no-print">
                <input type="password" id="mestre" placeholder="Chave Mestra">
                <button style="background:var(--blue)" onclick="listar()">ACESSAR DADOS</button>
            </div>
            <div id="form_add" style="margin-top:20px; padding:20px; background:#16213e; border-radius:12px;">
                <h3>Novo Cliente</h3>
                <input type="text" id="n" placeholder="Empresa">
                <input type="text" id="p" placeholder="PIN (6 dígitos)" maxlength="6">
                <input type="number" id="l" placeholder="Créditos (-1 = Assinatura)">
                <button style="background:var(--green)" onclick="cadastrar()">CRIAR CONTA</button>
            </div>
            <div id="lista_admin"></div>
        {% else %}
            <div id="login_area">
                <h1>LOGIN QUANTUM</h1>
                <input type="text" id="pin_cli" placeholder="Seu PIN de 6 dígitos" maxlength="6" style="width:100%">
                <button style="background:var(--blue); width:100%; margin-top:10px;" onclick="entrar()">ENTRAR</button>
            </div>
            <div id="dashboard" style="display:none;">
                <h2 id="emp_nome" style="color:var(--blue)"></h2>
                <div id="info_resumo"></div>
                <div class="progress-container"><div id="barra" class="progress-bar"></div></div>
                <div class="no-print" style="background:#16213e; padding:15px; border-radius:10px; margin:20px 0;">
                    <select id="qtd_massa"><option value="1">1 Chave</option><option value="5">5 Chaves</option><option value="10">10 Chaves</option></select>
                    <input type="text" id="obs" placeholder="Lote/Observação" style="width:50%">
                    <button style="background:var(--green)" onclick="gerar()">GERAR</button>
                    <button style="background:#475569" onclick="window.print()">IMPRIMIR</button>
                </div>
                <div id="lista_historico"></div>
            </div>
        {% endif %}
    </div>

    <script>
    // ADMIN
    async function listar() {
        const k = document.getElementById('mestre').value;
        const res = await fetch('/admin/listar?key=' + k);
        if(!res.ok) return alert("Chave Admin Inválida!");
        const dados = await res.json();
        let h = "<table><tr><th>Empresa</th><th>Tipo</th><th>Ações</th></tr>";
        dados.forEach(c => {
            const isSub = c.l === -1;
            h += `<tr><td>${c.n}<br><small>${c.p}</small></td>
                <td><span class="badge ${isSub?'badge-sub':'badge-cre'}">${isSub?'ASSINATURA':'CRÉDITOS: '+c.u+'/'+c.l}</span></td>
                <td>
                    <button style="background:var(--gold); color:black" onclick="setSub('${c.p}')">Sub</button>
                    <button style="background:var(--blue)" onclick="addCr('${c.p}')">+Cr</button>
                    <button style="background:var(--red)" onclick="del('${c.p}')">X</button>
                </td></tr>`;
        });
        document.getElementById('lista_admin').innerHTML = h + "</table>";
    }

    async function cadastrar() {
        const k = document.getElementById('mestre').value;
        const body = {key:k, n:document.getElementById('n').value, p:document.getElementById('p').value, l:document.getElementById('l').value};
        await fetch('/admin/cadastrar', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(body)});
        listar();
    }
    async function setSub(p) { await fetch('/admin/assinatura', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({key:document.getElementById('mestre').value, pin:p})}); listar(); }
    async function addCr(p) { const q = prompt("Qtd:"); if(q) await fetch('/admin/credito', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({key:document.getElementById('mestre').value, pin:p, qtd:q})}); listar(); }
    async function del(p) { if(confirm("Deletar?")) await fetch('/admin/deletar', {method:'DELETE', headers:{'Content-Type':'application/json'}, body:JSON.stringify({key:document.getElementById('mestre').value, pin:p})}); listar(); }

    // CLIENTE
    async function entrar() {
        const p = document.getElementById('pin_cli').value;
        const res = await fetch('/v1/cliente/dados?pin=' + p);
        if(!res.ok) return alert("PIN Errado!");
        const d = await res.json();
        document.getElementById('login_area').style.display='none';
        document.getElementById('dashboard').style.display='block';
        document.getElementById('emp_nome').innerText = d.empresa;
        const b = document.getElementById('barra');
        if(d.limite == -1) { b.classList.add('infinite-bar'); document.getElementById('info_resumo').innerText = "PLANO ILIMITADO ATIVO"; }
        else { b.style.width = (d.usadas/d.limite*100)+"%"; document.getElementById('info_resumo').innerText = `Saldo: ${d.usadas}/${d.limite}`; }
        let h = "";
        d.hist.reverse().forEach((t, i) => {
            const pt = t.split(' | ');
            h += `<div class="hist-item" id="r-${i}" onclick="this.classList.toggle('selected')">
                <b>${pt[1]}</b> <span style="font-family:monospace; color:var(--blue)">${pt[2]}</span>
            </div>`;
        });
        document.getElementById('lista_historico').innerHTML = h;
    }

    async function gerar() {
        const p = document.getElementById('pin_cli').value;
        const q = document.getElementById('qtd_massa').value;
        for(let i=0; i<q; i++) {
            await fetch('/v1/cliente/gerar', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({pin:p, obs:document.getElementById('obs').value || "QUANTUM"})});
        }
        entrar();
    }
    </script>
</body>
</html>
"""

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
    return jsonify([{"n": x[0], "p": x[1], "u": x[2], "l": x[3], "a": x[4]} for x in r])

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
    cur.execute("UPDATE clientes SET limite = CASE WHEN limite = -1 THEN %s ELSE limite + %s END WHERE pin_hash = %s", (int(d['qtd']), int(d['qtd']), d['pin']))
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
    if c and c[4]: return jsonify({"empresa": c[0], "usadas": c[1], "limite": c[2], "hist": c[3]})
    return jsonify({"e": 401}), 401

@app.route('/v1/cliente/gerar', methods=['POST'])
def gen_key():
    d = request.json
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT acessos, limite, ativo FROM clientes WHERE pin_hash = %s", (d['pin'],))
    c = cur.fetchone()
    if c and c[2] and (c[1] == -1 or c[0] < c[1]):
        nk = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(25))
        reg = f"X | {d['obs'].upper()} | {nk}"
        cur.execute("UPDATE clientes SET acessos=acessos+1, historico_chaves=array_append(historico_chaves, %s) WHERE pin_hash=%s", (reg, d['pin']))
        conn.commit(); cur.close(); conn.close(); return jsonify({"ok": True})
    cur.close(); conn.close(); return jsonify({"e": 403}), 403

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))