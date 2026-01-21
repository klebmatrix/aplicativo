import os, secrets, string, psycopg2
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- SEGURANÇA E BANCO ---
def get_admin_key():
    return (os.environ.get('ADMIN_KEY') or '').strip()

def get_db_connection():
    url = os.environ.get('DATABASE_URL')
    if not url: return None
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return psycopg2.connect(url, sslmode='require')

# --- INTERFACE HTML ---
HTML_SISTEMA = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QUANTUM | GESTÃO TOTAL</title>
    <style>
        :root { --blue: #38bdf8; --dark: #0b1120; --card: #1e293b; --red: #ef4444; --green: #22c55e; --gold: #fbbf24; }
        body { background: var(--dark); color: white; font-family: sans-serif; padding: 20px; }
        .container { max-width: 1100px; margin: auto; background: var(--card); padding: 30px; border-radius: 20px; border: 1px solid #334155; }
        input, select { padding: 12px; background: #0f172a; border: 1px solid #334155; color: white; border-radius: 8px; outline: none; }
        button { padding: 8px 12px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; color: white; transition: 0.2s; }
        
        /* Tabela e Badges */
        table { width: 100%; border-collapse: collapse; margin-top: 20px; background: #0f172a; }
        th, td { padding: 12px; border-bottom: 1px solid #334155; text-align: center; }
        .badge { padding: 4px 8px; border-radius: 5px; font-size: 11px; }
        .badge-sub { background: var(--gold); color: black; }
        .badge-cre { background: var(--blue); color: white; }

        /* Cliente */
        .progress-container { background: #0f172a; border-radius: 10px; height: 12px; margin: 15px 0; border: 1px solid #334155; overflow: hidden; }
        .progress-bar { height: 100%; background: var(--blue); width: 0%; transition: 0.5s; }
        .infinite-bar { background: linear-gradient(90deg, var(--blue), var(--gold), var(--blue)); background-size: 200%; animation: move 2s linear infinite; width: 100% !important; }
        @keyframes move { 0% {background-position: 0%} 100% {background-position: 200%} }
    </style>
</head>
<body>
    <div class="container">
        {% if tipo == 'admin' %}
            <h1 style="color:var(--blue)">NÚCLEO DE CONTROLE</h1>
            <input type="password" id="mestre" placeholder="Chave Admin">
            <button style="background:var(--blue)" onclick="listar()">CARREGAR SISTEMA</button>

            <div id="lista_admin" style="margin-top:20px;"></div>
        {% else %}
            <div id="login_area">
                <h1>LOGIN CLIENTE</h1>
                <input type="text" id="pin" placeholder="PIN de 6 dígitos" style="width:100%">
                <button style="background:var(--blue); width:100%; margin-top:10px;" onclick="entrar()">ENTRAR</button>
            </div>

            <div id="dashboard" style="display:none;">
                <h2 id="emp_nome" style="color:var(--blue)"></h2>
                <div id="info_assinatura"></div>
                <div class="progress-container"><div id="barra" class="progress-bar"></div></div>
                
                <div class="no-print" style="margin-bottom:20px;">
                    <input type="text" id="obs" placeholder="Observação do Lote" style="width:60%">
                    <button style="background:var(--green); width:35%" onclick="gerar()">GERAR CHAVE</button>
                </div>
                <div id="lista_historico"></div>
            </div>
        {% endif %}
    </div>

    <script>
    // ADMIN: FUNÇÕES DE ASSINATURA
    async function listar() {
        const k = document.getElementById('mestre').value;
        const res = await fetch('/admin/listar?key=' + k);
        const dados = await res.json();
        let h = "<table><tr><th>Empresa</th><th>Tipo</th><th>Saldo</th><th>Ações</th></tr>";
        dados.forEach(c => {
            const isSub = c.l === -1;
            h += `<tr>
                <td>${c.n}</td>
                <td><span class="badge ${isSub?'badge-sub':'badge-cre'}">${isSub?'ASSINANTE':'CRÉDITO'}</span></td>
                <td>${isSub?'∞ (Ilimitado)':c.u+' / '+c.l}</td>
                <td>
                    <button style="background:var(--gold); color:black" onclick="setSub('${c.p}')">Set Assinatura</button>
                    <button style="background:var(--blue)" onclick="addCr('${c.p}')">+ Créditos</button>
                    <button style="background:var(--red)" onclick="del('${c.p}')">X</button>
                </td>
            </tr>`;
        });
        document.getElementById('lista_admin').innerHTML = h + "</table>";
    }

    async function setSub(p) {
        if(confirm("Ativar Plano de Assinatura (Ilimitado) para este cliente?")) {
            await fetch('/admin/assinatura', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({key:document.getElementById('mestre').value, pin:p})});
            listar();
        }
    }

    async function addCr(p) {
        const q = prompt("Adicionar quantos créditos? (Isso muda para modo Crédito)");
        if(q) await fetch('/admin/credito', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({key:document.getElementById('mestre').value, pin:p, qtd:q})});
        listar();
    }

    // CLIENTE: LÓGICA DE EXIBIÇÃO
    async function entrar() {
        const p = document.getElementById('pin').value;
        const res = await fetch('/v1/cliente/dados?pin=' + p);
        if(!res.ok) return alert("Erro no PIN!");
        const d = await res.json();
        
        document.getElementById('login_area').style.display = 'none';
        document.getElementById('dashboard').style.display = 'block';
        document.getElementById('emp_nome').innerText = d.empresa;

        const barra = document.getElementById('barra');
        if(d.limite === -1) {
            document.getElementById('info_assinatura').innerHTML = "<b style='color:var(--gold)'>✨ PLANO ASSINATURA ATIVO (GERAÇÃO ILIMITADA)</b>";
            barra.classList.add('infinite-bar');
        } else {
            document.getElementById('info_assinatura').innerHTML = `Saldo de Créditos: ${d.usadas} / ${d.limite}`;
            barra.style.width = (d.usadas / d.limite * 100) + "%";
            barra.classList.remove('infinite-bar');
        }

        let h = "";
        d.hist.reverse().forEach(t => {
            const pt = t.split(' | ');
            h += `<div style="background:#0f172a; padding:10px; margin-top:5px; border-radius:8px; display:flex; justify-content:space-between;">
                <span>${pt[1]}</span><span style="font-family:monospace; color:var(--blue)">${pt[2]}</span>
            </div>`;
        });
        document.getElementById('lista_historico').innerHTML = h;
    }

    async function gerar() {
        const p = document.getElementById('pin').value;
        const res = await fetch('/v1/cliente/gerar', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({pin:p, obs:document.getElementById('obs').value || "QUANTUM"})});
        if(res.ok) entrar(); else alert("Sem saldo ou bloqueado!");
    }
    </script>
</body>
</html>
"""

# --- BACKEND COM LÓGICA DE LIMITE -1 ---
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

@app.route('/admin/assinatura', methods=['POST'])
def set_sub():
    d = request.json
    if d.get('key', '').strip() != get_admin_key(): return jsonify({"e":403}), 403
    conn = get_db_connection(); cur = conn.cursor()
    # Define limite como -1 para Assinatura
    cur.execute("UPDATE clientes SET limite = -1 WHERE pin_hash = %s", (d['pin'],))
    conn.commit(); cur.close(); conn.close(); return jsonify({"ok": True})

@app.route('/admin/credito', methods=['POST'])
def add_cre():
    d = request.json
    if d.get('key', '').strip() != get_admin_key(): return jsonify({"e":403}), 403
    conn = get_db_connection(); cur = conn.cursor()
    # Se estava em -1, resetamos para a quantidade nova. Se não, somamos.
    cur.execute("UPDATE clientes SET limite = CASE WHEN limite = -1 THEN %s ELSE limite + %s END WHERE pin_hash = %s", (int(d['qtd']), int(d['qtd']), d['pin']))
    conn.commit(); cur.close(); conn.close(); return jsonify({"ok": True})

@app.route('/v1/cliente/gerar', methods=['POST'])
def gen_key():
    d = request.json
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT acessos, limite, ativo FROM clientes WHERE pin_hash = %s", (d['pin'],))
    c = cur.fetchone()
    
    # Lógica: Se limite for -1 OU acessos < limite, permite gerar.
    if c and c[2] and (c