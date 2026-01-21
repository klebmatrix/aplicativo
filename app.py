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

# Interface com alertas de erro e correção de impressão
HTML_SISTEMA = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SISTEMA QUANTUM</title>
    <style>
        :root { --blue: #38bdf8; --dark: #0b1120; --card: #1e293b; --red: #ef4444; --green: #22c55e; }
        body { background: var(--dark); color: white; font-family: sans-serif; padding: 20px; }
        .container { max-width: 900px; margin: auto; background: var(--card); padding: 25px; border-radius: 15px; border: 1px solid #334155; }
        input { padding: 12px; margin: 5px; background: #0f172a; border: 1px solid #334155; color: white; border-radius: 8px; }
        button { padding: 10px 15px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; color: white; }
        
        .hist-item { background: #0f172a; padding: 15px; margin-top: 10px; border-radius: 10px; display: flex; align-items: center; border: 2px solid transparent; }
        .hist-item.selected { border-color: var(--blue); background: #162e45; }
        .key-txt { font-family: monospace; font-size: 16px; margin-left: auto; color: #38bdf8; }

        @media print {
            body { background: white !important; color: black !important; }
            .no-print, button, input, h1, .saldo-info { display: none !important; }
            .container { border: none !important; box-shadow: none !important; background: white !important; width: 100%; }
            .hist-item { border: 1px solid black !important; color: black !important; background: white !important; display: none; }
            .hist-item.selected { display: flex !important; }
            .key-txt { color: black !important; }
        }
    </style>
</head>
<body>
    <div class="container">
        {% if tipo == 'admin' %}
            <h1>ADMINISTRAÇÃO</h1>
            <input type="password" id="mestre" placeholder="Chave Admin">
            <button style="background:var(--blue)" onclick="listar()">LISTAR CLIENTES</button>
            <div id="lista_admin"></div>
        {% else %}
            <div id="login_area">
                <h1>LOGIN QUANTUM</h1>
                <input type="text" id="pin" placeholder="PIN de 6 dígitos" maxlength="6" style="width:100%; box-sizing:border-box;">
                <button style="background:var(--blue); width:100%; margin-top:10px;" onclick="entrar()">ACESSAR PAINEL</button>
            </div>

            <div id="dashboard" style="display:none;">
                <h2 id="emp_nome" style="color:var(--blue)"></h2>
                <div class="saldo-info" style="background:#0f172a; padding:15px; border-radius:10px; margin-bottom:15px; display:flex; justify-content:space-between; align-items:center;">
                    <span>Créditos: <b id="uso"></b> / <b id="total"></b></span>
                    <button style="background:#475569" onclick="window.print()">🖨️ IMPRIMIR MARCADOS</button>
                </div>
                <div class="no-print">
                    <input type="text" id="obs" placeholder="Obs (Ex: Lote A)" style="width:60%">
                    <button id="btnGerar" style="background:var(--green); width:35%" onclick="gerar()">GERAR NOVA CHAVE</button>
                </div>
                <div id="lista_historico"></div>
            </div>
        {% endif %}
    </div>

    <script>
    async function entrar() {
        const pin = document.getElementById('pin').value;
        const res = await fetch('/v1/cliente/dados?pin=' + pin);
        if(!res.ok) return alert("Erro: PIN inválido ou Empresa Bloqueada!");
        
        const d = await res.json();
        document.getElementById('login_area').style.display='none';
        document.getElementById('dashboard').style.display='block';
        document.getElementById('emp_nome').innerText = d.empresa;
        document.getElementById('uso').innerText = d.usadas;
        document.getElementById('total').innerText = d.limite;

        if(d.usadas >= d.limite) {
            document.getElementById('btnGerar').disabled = true;
            document.getElementById('btnGerar').style.opacity = '0.5';
            document.getElementById('btnGerar').innerText = "SEM SALDO";
        }

        let h = "";
        d.hist.reverse().forEach((t, i) => {
            const pt = t.split(' | ');
            h += `<div class="hist-item" id="row-${i}" onclick="toggleRow(${i})">
                <input type="checkbox" class="no-print" id="chk-${i}">
                <b style="margin-left:15px">${pt[1]}</b>
                <span class="key-txt">${pt[2]}</span>
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

    async function gerar() {
        const pin = document.getElementById('pin').value;
        const obs = document.getElementById('obs').value || "GERAL";
        const res = await fetch('/v1/cliente/gerar', {
            method:'POST', 
            headers:{'Content-Type':'application/json'}, 
            body:JSON.stringify({pin:pin, obs:obs})
        });
        
        const data = await res.json();
        if(data.ok) {
            entrar(); 
            document.getElementById('obs').value = "";
        } else {
            alert("ERRO: " + (data.e || "Verifique seu saldo ou status!"));
        }
    }

    // Funções Admin (Listar, Crédito, etc.) permanecem as mesmas...
    async function listar() {
        const k = document.getElementById('mestre').value;
        const res = await fetch('/admin/listar?key=' + k);
        if(!res.ok) return alert("Chave Admin Incorreta!");
        const dados = await res.json();
        let h = "<table><tr><th>Empresa</th><th>PIN</th><th>Saldo</th><th>Ações</th></tr>";
        dados.forEach(c => {
            h += `<tr><td>${c.n}</td><td>${c.p}</td><td>${c.u}/${c.l}</td><td>
                <button style="background:var(--blue)" onclick="addCr('${c.p}')">+ Cr</button>
            </td></tr>`;
        });
        document.getElementById('lista_admin').innerHTML = h + "</table>";
    }
    async function addCr(p) {
        const q = prompt("Qtd:");
        if(q) await fetch('/admin/credito', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({key:document.getElementById('mestre').value, pin:p, qtd:q})});
        listar();
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
    key = get_admin_key()
    if not key or request.args.get('key', '').strip() != key: return jsonify([]), 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT nome_empresa, pin_hash, acessos, limite, ativo FROM clientes ORDER BY id DESC")
    r = cur.fetchall(); cur.close(); conn.close()
    return jsonify([{"n": x[0], "p": x[1], "u": x[2], "l": x[3], "a": x[4]} for x in r])

@app.route('/admin/credito', methods=['POST'])
def cr_cli():
    d = request.json
    if not get_admin_key() or d.get('key', '').strip() != get_admin_key(): return jsonify({"e":403}), 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("UPDATE clientes SET limite = limite + %s WHERE pin_hash = %s", (int(d['qtd']), d['pin']))
    conn.commit(); cur.close(); conn.close(); return jsonify({"ok": True})

@app.route('/v1/cliente/dados')
def get_cli_dados():
    pin = request.args.get('pin')
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT nome_empresa, acessos, limite, historico_chaves, ativo FROM clientes WHERE pin_hash = %s", (pin,))
    c = cur.fetchone(); cur.close(); conn.close()
    if c:
        if not c[4]: return jsonify({"e": "Empresa Bloqueada"}), 403
        return jsonify({"empresa": c[0], "usadas": c[1], "limite": c[2], "hist": c[3]})
    return jsonify({"e": "PIN Inválido"}), 401

@app.route('/v1/cliente/gerar', methods=['POST'])
def gen_cli_key():
    d = request.json
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT acessos, limite, ativo FROM clientes WHERE pin_hash = %s", (d['pin'],))
    c = cur.fetchone()
    
    if not c:
        return jsonify({"ok": False, "e": "PIN não encontrado"}), 404
    if not c[2]:
        return jsonify({"ok": False, "e": "Sua conta está BLOQUEADA"}), 403
    if c[0] >= c[1]:
        return jsonify({"ok": False, "e": "Limite de créditos ESGOTADO"}), 403

    nk = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(30))
    reg = f"X | {d['obs'].upper()} | {nk}"
    cur.execute("UPDATE clientes SET acessos=acessos+1, historico_chaves=array_append(historico_chaves, %s) WHERE pin_hash=%s", (reg, d['pin']))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"ok": True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))