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
    <title>QUANTUM | INTERFACE</title>
    <style>
        :root { --blue: #38bdf8; --dark: #0b1120; --card: #1e293b; --red: #ef4444; --green: #22c55e; --neon: 0 0 15px rgba(56, 189, 248, 0.5); }
        body { background: var(--dark); color: white; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 20px; }
        .container { max-width: 1000px; margin: auto; background: var(--card); padding: 30px; border-radius: 20px; border: 1px solid #334155; box-shadow: var(--neon); }
        input { padding: 12px; margin: 5px; background: #0f172a; border: 1px solid #334155; color: white; border-radius: 8px; outline: none; transition: 0.3s; }
        input:focus { border-color: var(--blue); box-shadow: var(--neon); }
        button { padding: 12px 18px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; color: white; transition: 0.3s; }
        button:hover { transform: translateY(-2px); filter: brightness(1.2); }
        
        /* Barra de Progresso Quântica */
        .progress-container { background: #0f172a; border-radius: 20px; height: 12px; width: 100%; margin: 15px 0; overflow: hidden; border: 1px solid #334155; }
        .progress-bar { height: 100%; background: linear-gradient(90deg, #38bdf8, #818cf8); box-shadow: var(--neon); transition: width 0.5s ease-in-out; }

        /* Estilo das Chaves */
        .hist-item { background: #0f172a; padding: 15px; margin-top: 10px; border-radius: 12px; display: flex; align-items: center; border: 1px solid #1e293b; transition: 0.2s; }
        .hist-item:hover { border-color: var(--blue); background: #162e45; }
        .hist-item.selected { border-color: var(--blue); background: #1e3a5f; }
        .key-txt { font-family: 'Courier New', monospace; font-size: 15px; color: var(--blue); font-weight: bold; margin-left: 15px; }
        .btn-copy { background: transparent; border: 1px solid var(--blue); color: var(--blue); padding: 5px 10px; font-size: 11px; margin-left: 10px; }
        .btn-copy:hover { background: var(--blue); color: white; }

        @media print {
            .no-print, button, input, h1, .progress-container, .search-box { display: none !important; }
            body { background: white !important; color: black !important; }
            .container { border: none !important; box-shadow: none !important; background: white !important; }
            .hist-item { border: 1px solid black !important; display: none !important; }
            .hist-item.selected { display: flex !important; }
            .key-txt { color: black !important; }
        }
    </style>
</head>
<body>
    <div class="container">
        {% if tipo == 'admin' %}
            <h1 style="color:var(--blue)">NÚCLEO ADMINISTRATIVO</h1>
            <input type="password" id="mestre" placeholder="Chave Admin">
            <button style="background:var(--blue)" onclick="listar()">ATUALIZAR BANCO</button>
            <div id="lista_admin"></div>
        {% else %}
            <div id="login_area">
                <h1 style="text-align:center; letter-spacing: 3px;">QUANTUM LOGIN</h1>
                <input type="text" id="pin" placeholder="PIN de 6 dígitos" maxlength="6" style="width:100%; box-sizing:border-box; text-align:center; font-size:20px;">
                <button style="background:var(--blue); width:100%; margin-top:15px; font-size:18px;" onclick="entrar()">AUTENTICAR</button>
            </div>

            <div id="dashboard" style="display:none;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h2 id="emp_nome" style="color:var(--blue); margin:0;"></h2>
                    <button style="background:#475569" onclick="window.print()">🖨️ IMPRIMIR SELECIONADOS</button>
                </div>

                <div style="margin-top:20px;">
                    <div style="display:flex; justify-content:space-between; font-size:13px; color:#94a3b8;">
                        <span>Uso do Sistema Quântico</span>
                        <span id="txt_saldo">0/0</span>
                    </div>
                    <div class="progress-container"><div id="barra" class="progress-bar" style="width: 0%"></div></div>
                </div>
                
                <div class="no-print" style="background:#0f172a; padding:20px; border-radius:12px; margin-top:20px;">
                    <input type="text" id="obs" placeholder="Nome do Lote / Observação" style="width:65%">
                    <button id="btnGerar" style="background:var(--green); width:30%" onclick="gerar()">GERAR CHAVE</button>
                </div>

                <div class="search-box no-print" style="margin-top:20px;">
                    <input type="text" id="busca" placeholder="🔍 Filtrar histórico..." style="width:100%; box-sizing:border-box;" onkeyup="filtrar()">
                </div>

                <div id="lista_historico" style="margin-top:10px;"></div>
            </div>
        {% endif %}
    </div>

    <script>
    async function entrar() {
        const p = document.getElementById('pin').value;
        const res = await fetch('/v1/cliente/dados?pin=' + p);
        if(!res.ok) return alert("Acesso Negado!");
        const d = await res.json();
        
        document.getElementById('login_area').style.display='none';
        document.getElementById('dashboard').style.display='block';
        document.getElementById('emp_nome').innerText = d.empresa;
        document.getElementById('txt_saldo').innerText = `${d.usadas} / ${d.limite}`;
        
        const perc = (d.usadas / d.limite) * 100;
        document.getElementById('barra').style.width = perc + "%";
        if(perc > 80) document.getElementById('barra').style.background = "var(--red)";

        renderizarHist(d.hist);
    }

    function renderizarHist(hist) {
        let h = "";
        hist.reverse().forEach((t, i) => {
            const pt = t.split(' | ');
            h += `<div class="hist-item" id="row-${i}" onclick="toggleRow(${i})">
                <input type="checkbox" class="no-print" id="chk-${i}" style="pointer-events:none">
                <span style="margin-left:15px; font-weight:bold;">${pt[1]}</span>
                <span class="key-txt" id="key-${i}">${pt[2]}</span>
                <button class="btn-copy no-print" onclick="copiar(event, '${pt[2]}')">COPIAR</button>
            </div>`;
        });
        document.getElementById('lista_historico').innerHTML = h;
    }

    function toggleRow(i) {
        const row = document.getElementById('row-'+i);
        const chk = document.getElementById('chk-'+i);
        row.classList.toggle('selected');
        chk.checked = row.classList.contains('selected');
    }

    function copiar(e, txt) {
        e.stopPropagation();
        navigator.clipboard.writeText(txt);
        alert("Chave copiada!");
    }

    function filtrar() {
        const termo = document.getElementById('busca').value.toUpperCase();
        const itens = document.getElementsByClassName('hist-item');
        for (let item of itens) {
            item.style.display = item.innerText.toUpperCase().includes(termo) ? "flex" : "none";
        }
    }

    async function gerar() {
        const p = document.getElementById('pin').value;
        const o = document.getElementById('obs').value || "GERAL";
        const res = await fetch('/v1/cliente/gerar', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({pin:p, obs:o})});
        if(res.ok) { entrar(); document.getElementById('obs').value = ""; } else { alert("Sem saldo!"); }
    }

    // ADMIN permanece com todas as funções de cadastro e crédito
    async function listar() {
        const k = document.getElementById('mestre').value.trim();
        const res = await fetch('/admin/listar?key=' + k);
        if(!res.ok) return alert("Erro Admin!");
        const dados = await res.json();
        let h = "<table style='width:100%; margin-top:20px; border-collapse:collapse;'><tr><th>Empresa</th><th>Saldo</th><th>Ações</th></tr>";
        dados.forEach(c => {
            h += `<tr style='border-bottom:1px solid #334155'><td>${c.n}</td><td>${c.u}/${c.l}</td><td>
                <button style='background:var(--blue)' onclick="addCr('${c.p}')">+ Cr</button>
                <button style='background:var(--red)' onclick="del('${c.p}')">X</button>
            </td></tr>`;
        });
        document.getElementById('lista_admin').innerHTML = h + "</table>";
    }
    async function addCr(p) {
        const q = prompt("Qtd:");
        if(q) await fetch('/admin/credito', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({key:document.getElementById('mestre').value, pin:p, qtd:q})});
        listar();
    }
    async function del(p) {
        if(confirm("Excluir?")) await fetch('/admin/deletar', {method:'DELETE', headers:{'Content-Type':'application/json'}, body:JSON.stringify({key:document.getElementById('mestre').value, pin:p})});
        listar();
    }
    </script>
</body>
</html>
"""

# As rotas Python permanecem as mesmas das versões anteriores para manter a funcionalidade do banco.
@app.route('/')
def home(): return render_template_string(HTML_SISTEMA)

@app.route('/painel-secreto-kleber')
def admin_page(): return render_template_string(HTML_SISTEMA, tipo='admin')

@app.route('/admin/listar')
def list_adm():
    if request.args.get('key', '').strip() != get_admin_key(): return jsonify([]), 403
    conn = get_db_connection(); cur = conn.cursor(); cur.execute("SELECT nome_empresa, pin_hash, acessos, limite, ativo FROM clientes ORDER BY id DESC")
    r = cur.fetchall(); cur.close(); conn.close()
    return jsonify([{"n": x[0], "p": x[1], "u": x[2], "l": x[3], "a": x[4]} for x in r])

@app.route('/admin/credito', methods=['POST'])
def cr_adm():
    d = request.json
    if d.get('key', '').strip() != get_admin_key(): return jsonify({"e":403}), 403
    conn = get_db_connection(); cur = conn.cursor(); cur.execute("UPDATE clientes SET limite = limite + %s WHERE pin_hash = %s", (int(d['qtd']), d['pin']))
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
    conn = get_db_connection(); cur = conn.cursor(); cur.execute("SELECT nome_empresa, acessos, limite, historico_chaves, ativo FROM clientes WHERE pin_hash = %s", (pin,))
    c = cur.fetchone(); cur.close(); conn.close()
    if c and c[4]: return jsonify({"empresa": c[0], "usadas": c[1], "limite": c[2], "hist": c[3]})
    return jsonify({"e": 401}), 401

@app.route('/v1/cliente/gerar', methods=['POST'])
def gen_key():
    d = request.json
    conn = get_db_connection(); cur = conn.cursor(); cur.execute("SELECT acessos, limite, ativo FROM clientes WHERE pin_hash = %s", (d['pin'],))
    c = cur.fetchone()
    if c and c[0] < c[1] and c[2]:
        nk = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(30))
        reg = f"X | {d['obs'].upper()} | {nk}"
        cur.execute("UPDATE clientes SET acessos=acessos+1, historico_chaves=array_append(historico_chaves, %s) WHERE pin_hash=%s", (reg, d['pin']))
        conn.commit(); cur.close(); conn.close(); return jsonify({"ok": True})
    cur.close(); conn.close(); return jsonify({"e": "Erro"}), 403

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))