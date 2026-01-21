import os
import secrets
import string
import psycopg2
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Chave mestra definida no Render ou padrão 'ADMIN123'
ADMIN_KEY = os.environ.get('ADMIN_KEY', 'ADMIN123')

def get_db_connection():
    url = os.environ.get('DATABASE_URL')
    if url and url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    try:
        return psycopg2.connect(url, sslmode='require')
    except Exception as e:
        print(f"Erro de conexão: {e}")
        return None

def generate_quantum_key(length=30):
    chars = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))

HTML_SISTEMA = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>KEYQUANTUM | GESTÃO</title>
    <style>
        :root { --blue: #38bdf8; --dark: #0b1120; --card: #1e293b; --input: #0f172a; --red: #ef4444; }
        body { background: var(--dark); color: white; font-family: 'Segoe UI', sans-serif; padding: 20px; }
        .container { max-width: 850px; margin: auto; background: var(--card); padding: 25px; border-radius: 15px; border: 1px solid #334155; }
        
        input { padding: 12px; margin: 10px 0; background: var(--input); border: 1px solid #334155; color: white; border-radius: 8px; width: 90%; }
        button { padding: 10px 20px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; color: white; transition: 0.3s; }
        
        .btn-green { background: #22c55e; width: 100%; margin-top: 10px; font-size: 1.1rem; }
        .btn-blue { background: #0284c7; }
        .btn-red { background: var(--red); font-size: 11px; }

        /* LISTA SEM DATA E HORA - FOCO NA VISUALIZAÇÃO */
        .hist-item { 
            background: var(--input); padding: 15px; margin-top: 8px; border-radius: 10px; 
            display: flex; align-items: center; border: 2px solid transparent; 
        }
        .hist-item.selected { border-color: var(--blue); background: #162e45; }
        .marcador { width: 22px; height: 22px; margin-right: 15px; cursor: pointer; }
        
        .label-obs { color: var(--blue); font-weight: bold; margin-right: 15px; min-width: 120px; text-transform: uppercase; }
        .key-txt { font-family: 'Courier New', monospace; color: #cbd5e1; flex-grow: 1; letter-spacing: 1px; }

        table { width: 100%; margin-top: 20px; border-collapse: collapse; }
        th, td { padding: 12px; border: 1px solid #334155; text-align: left; }

        @media print {
            body { background: white !important; color: black !important; }
            button, input, .no-print, h1, .btn-green, .sel-area { display: none !important; }
            .hist-item:not(.selected) { display: none !important; }
            .hist-item { border: 1px solid #000 !important; color: black !important; }
            .marcador { display: none !important; }
            .label-obs { color: black !important; }
        }
    </style>
</head>
<body>
    <div class="container">
        {% if tipo == 'admin' %}
            <h1>PAINEL ADMIN SECRETO</h1>
            <input type="password" id="mestre" placeholder="Chave Mestra">
            <button class="btn-blue" onclick="listar()">LISTAR CLIENTES</button>
            <hr style="margin:25px 0; border:1px solid #334155;">
            <input type="text" id="n" placeholder="Nome da Empresa">
            <input type="text" id="p" placeholder="PIN (6 DÍGITOS)" maxlength="6">
            <input type="number" id="l" placeholder="Limite de Créditos" value="10">
            <button class="btn-green" onclick="add()">CADASTRAR CLIENTE</button>
            <div id="lista_admin"></div>
        {% else %}
            <div id="login_area">
                <h1>SISTEMA QUANTUM</h1>
                <input type="text" id="pin" placeholder="DIGITE SEU PIN DE 6 DÍGITOS" maxlength="6">
                <button class="btn-blue" style="width: 95%;" onclick="entrar()">ACESSAR PAINEL</button>
            </div>

            <div id="dashboard" style="display:none;">
                <h2 id="emp_nome" style="color: var(--blue); margin-top:0;"></h2>
                <div style="display:flex; justify-content:space-between; align-items:center; background:var(--input); padding:15px; border-radius:10px; margin-bottom:20px;">
                    <span>Saldo: <b id="uso">0</b> / <b id="total">0</b></span>
                    <div>
                        <button style="background:#475569; font-size:12px;" onclick="window.print()">🖨️ IMPRIMIR</button>
                        <button class="btn-blue" style="font-size:12px;" onclick="exportarExcel()">📊 EXCEL</button>
                    </div>
                </div>

                <input type="text" id="obs" placeholder="Observação (Ex: Lote, Cliente, Nota)">
                <button class="btn-green" onclick="gerar()">GERAR NOVA CHAVE</button>
                
                <div class="sel-area" style="margin-top:20px;">
                    <label style="cursor:pointer;"><input type="checkbox" onclick="selTudo(this)"> Selecionar Todas para Relatório</label>
                </div>
                <div id="lista_historico"></div>
            </div>
        {% endif %}
    </div>

    <script>
        let pinAtivo = "";

        document.querySelectorAll('input[placeholder*="PIN"]').forEach(el => {
            el.oninput = () => el.value = el.value.replace(/[^0-9]/g, '').slice(0,6);
        });

        async function entrar() {
            pinAtivo = document.getElementById('pin').value;
            if(pinAtivo.length !== 6) return alert("PIN de 6 dígitos!");
            const res = await fetch('/v1/cliente/dados?pin=' + pinAtivo);
            if(res.ok) { 
                document.getElementById('login_area').style.display='none';
                document.getElementById('dashboard').style.display='block';
                atualizar(); 
            } else { alert("Acesso negado."); }
        }

        async function atualizar() {
            const res = await fetch('/v1/cliente/dados?pin=' + pinAtivo);
            const d = await res.json();
            document.getElementById('emp_nome').innerText = d.empresa;
            document.getElementById('uso').innerText = d.usadas;
            document.getElementById('total').innerText = d.limite;
            
            let html = "";
            d.hist.reverse().forEach((txt, i) => {
                const partes = txt.split(' | ');
                const obs = partes[1] || "GERAL";
                const chave = partes[2] || "---";
                
                html += `
                <div class="hist-item" id="r-${i}">
                    <input type="checkbox" class="marcador" onchange="document.getElementById('r-${i}').classList.toggle('selected')" data-info="${obs};${chave}">
                    <span class="label-obs">${obs}</span>
                    <span class="key-txt">${chave}</span>
                </div>`;
            });
            document.getElementById('lista_historico').innerHTML = html;
        }

        function selTudo(s) {
            document.querySelectorAll('.marcador').forEach(cb => {
                cb.checked = s.checked;
                cb.parentElement.classList.toggle('selected', s.checked);
            });
        }

        async function gerar() {
            const o = document.getElementById('obs').value || "GERAL";
            await fetch('/v1/cliente/gerar', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ pin: pinAtivo, obs: o })
            });
            atualizar();
            document.getElementById('obs').value = "";
        }

        function exportarExcel() {
            const m = document.querySelectorAll('.marcador:checked');
            if(m.length === 0) return alert("Selecione os itens!");
            let csv = "OBSERVACAO;CHAVE\\n";
            m.forEach(i => csv += i.getAttribute('data-info') + "\\n");
            const blob = new Blob([csv], { type: 'text/csv' });
            const a = document.createElement('a');
            a.href = URL.createObjectURL(blob);
            a.download = "chaves_quantum.csv";
            a.click();
        }

        // ADMIN
        async function add() {
            const p = document.getElementById('p').value;
            await fetch('/admin/cadastrar', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({key: document.getElementById('mestre').value, n: document.getElementById('n').value, p: p, l: document.getElementById('l').value})
            });
            listar();
        }

        async function listar() {
            const res = await fetch('/admin/listar?key=' + document.getElementById('mestre').value);
            const dados = await res.json();
            let h = "<table><tr><th>Empresa</th><th>PIN</th><th>Ação</th></tr>";
            dados.forEach(c => {
                h += `<tr><td>${c.n}</td><td>${c.p}</td><td><button class="btn-red" onclick="apagar('${c.p}')">DELETAR</button></td></tr>`;
            });
            document.getElementById('lista_admin').innerHTML = h + "</table>";
        }

        async function apagar(p) {
            if(!confirm("Deletar cliente?")) return;
            await fetch('/admin/deletar', {
                method: 'DELETE',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({key: document.getElementById('mestre').value, pin: p})
            });
            listar();
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home(): return render_template_string(HTML_SISTEMA, tipo='login')

@app.route('/painel-secreto-kleber')
def admin_page(): return render_template_string(HTML_SISTEMA, tipo='admin')

@app.route('/v1/cliente/dados')
def get_dados():
    pin = request.args.get('pin')
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT nome_empresa, acessos, limite, historico_chaves FROM clientes WHERE pin_hash = %s", (pin,))
    c = cur.fetchone(); cur.close(); conn.close()
    if c: return jsonify({"empresa": c[0], "usadas": c[1], "limite": c[2], "hist": c[3]})
    return jsonify({"erro": "404"}), 404

@app.route('/v1/cliente/gerar', methods=['POST'])
def gerar_api():
    d = request.json
    pin = d.get('pin')
    obs = d.get('obs', 'GERAL').upper()
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT acessos, limite FROM clientes WHERE pin_hash = %s", (pin,))
    c = cur.fetchone()
    if c and c[0] < c[1]:
        nk = generate_quantum_key(30)
        reg = f"X | {obs} | {nk}"
        cur.execute("UPDATE clientes SET acessos=acessos+1, historico_chaves=array_append(historico_chaves, %s) WHERE pin_hash=%s", (reg, pin))
        conn.commit(); cur.close(); conn.close()
        return jsonify({"key": nk})
    return jsonify({"erro": "saldo"}), 403

@app.route('/admin/cadastrar', methods=['POST'])
def add_cli():
    d = request.json
    if d.get('key') != ADMIN_KEY: return jsonify({"e": "err"}), 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("INSERT INTO clientes (nome_empresa, pin_hash, limite, historico_chaves) VALUES (%s, %s, %s, '{}')", (d['n'], d['p'], d['l']))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"msg": "ok"})

@app.route('/admin/listar')
def list_all():
    if request.args.get('key') != ADMIN_KEY: return jsonify([]), 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT nome_empresa, pin_hash, acessos, limite FROM clientes ORDER BY id DESC")
    r = cur.fetchall(); cur.close(); conn.close()
    return jsonify([{"n": x[0], "p": x[1], "u": x[2], "l": x[3]} for x in r])

@app.route('/admin/deletar', methods=['DELETE'])
def deletar_cli():
    d = request.json
    if d.get('key') != ADMIN_KEY: return jsonify({"e": "err"}), 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("DELETE FROM clientes WHERE pin_hash = %s", (d.get('pin'),))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"msg": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))