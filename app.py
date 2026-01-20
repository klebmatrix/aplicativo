import os
import secrets
import string
import psycopg2
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Variável de ambiente para segurança
ADMIN_KEY = os.environ.get('ADMIN_KEY', 'ADMIN123')

def get_db_connection():
    url = os.environ.get('DATABASE_URL')
    if url and url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return psycopg2.connect(url, sslmode='require')

def generate_quantum_key(length=30):
    chars = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))

HTML_SISTEMA = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KEYQUANTUM | SISTEMA OFICIAL 2026</title>
    <style>
        :root { --blue: #38bdf8; --dark: #0b1120; --card: #1e293b; --input: #0f172a; }
        body { background: var(--dark); color: white; font-family: 'Segoe UI', Tahoma, sans-serif; margin: 0; padding: 20px; }
        .container { max-width: 800px; margin: auto; background: var(--card); padding: 30px; border-radius: 20px; border: 1px solid #334155; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        h1 { color: var(--blue); text-align: center; letter-spacing: 2px; }
        
        input { padding: 12px; margin: 10px 0; background: var(--input); border: 1px solid #334155; color: white; border-radius: 8px; width: 90%; font-size: 1rem; }
        button { padding: 12px 20px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; transition: 0.3s; }
        
        .btn-green { background: #22c55e; width: 100%; font-size: 1.1rem; margin-top: 15px; }
        .btn-blue { background: #0284c7; }
        .btn-gray { background: #475569; font-size: 12px; }
        .btn-copy { background: #334155; padding: 5px 10px; font-size: 11px; }

        /* LISTA DE HISTÓRICO COM SELEÇÃO */
        .hist-item { 
            background: var(--input); padding: 15px; margin-top: 10px; border-radius: 10px; 
            display: flex; align-items: center; border: 2px solid transparent; transition: 0.2s;
        }
        .hist-item.selected { border-color: var(--blue); background: #1e293b; }
        .checkbox-item { width: 22px; height: 22px; margin-right: 15px; cursor: pointer; }

        .dashboard-header { display: flex; justify-content: space-between; align-items: center; background: var(--input); padding: 15px; border-radius: 12px; margin: 20px 0; border-left: 5px solid var(--blue); }
        
        .actions-bar { display: flex; justify-content: space-between; margin-bottom: 10px; padding: 0 5px; }

        /* REGRAS DE IMPRESSÃO */
        @media print {
            body { background: white !important; color: black !important; }
            .container { border: none; box-shadow: none; width: 100%; max-width: 100%; }
            button, input, .actions-bar, h1, .btn-green { display: none !important; }
            .hist-item { border: 1px solid #000 !important; color: black !important; margin-bottom: 5px; }
            .hist-item:not(.selected) { display: none !important; } /* SÓ IMPRIME MARCADOS */
            .checkbox-item { display: none !important; }
        }
    </style>
</head>
<body>
    <div class="container">
        {% if tipo == 'admin' %}
            <h1>ADMIN | PAINEL</h1>
            <input type="password" id="mestre" placeholder="Chave Mestra">
            <button class="btn-blue" onclick="listar()">LISTAR CLIENTES</button>
            <hr style="border:0; border-top: 1px solid #334155; margin: 25px 0;">
            <input type="text" id="n" placeholder="Nome da Empresa">
            <input type="text" id="p" placeholder="PIN (6 dígitos)" maxlength="6">
            <input type="number" id="l" placeholder="Limite de Créditos" value="10">
            <button class="btn-green" onclick="add()">CADASTRAR E ATIVAR</button>
            <div id="lista_admin"></div>
        {% else %}
            <div id="login_area">
                <h1>KEYQUANTUM</h1>
                <input type="text" id="pin" placeholder="DIGITE SEU PIN (6 DÍGITOS)" maxlength="6">
                <button class="btn-blue" style="width: 95%;" onclick="entrar()">ENTRAR NO SISTEMA</button>
            </div>

            <div id="dashboard" style="display:none;">
                <h2 id="empresa_nome" style="color: var(--blue); margin-bottom: 5px;"></h2>
                <div class="dashboard-header">
                    <div>Saldo: <b id="uso">0</b> / <b id="total">0</b></div>
                    <div>
                        <button class="btn-gray" onclick="window.print()">🖨️ IMPRIMIR SELECIONADOS</button>
                        <button class="btn-blue" style="font-size:12px;" onclick="exportarExcel()">📊 EXCEL (XLS)</button>
                    </div>
                </div>

                <input type="text" id="obs" placeholder="Observação/Referência da Chave">
                <button class="btn-green" onclick="gerar()">GERAR CHAVE QUANTUM</button>

                <h3 style="margin-top:30px; border-bottom: 1px solid #334155; padding-bottom: 10px;">HISTÓRICO DE CHAVES</h3>
                <div class="actions-bar">
                    <label style="font-size: 13px; cursor: pointer;">
                        <input type="checkbox" id="select_all" onclick="selecionarTudo(this)"> Selecionar Todas
                    </label>
                </div>
                <div id="lista_historico"></div>
            </div>
        {% endif %}
    </div>

    <script>
        let pinAtivo = "";

        // Validação rigorosa do PIN (Apenas 6 números)
        document.querySelectorAll('input[placeholder*="PIN"]').forEach(el => {
            el.oninput = () => el.value = el.value.replace(/[^0-9]/g, '').slice(0, 6);
        });

        async function entrar() {
            pinAtivo = document.getElementById('pin').value;
            if(pinAtivo.length !== 6) return alert("PIN deve ter 6 dígitos.");
            const res = await fetch('/v1/cliente/dados?pin=' + pinAtivo);
            if(res.ok) { atualizarUI(); } else { alert("Acesso negado."); }
        }

        async function atualizarUI() {
            const res = await fetch('/v1/cliente/dados?pin=' + pinAtivo);
            const d = await res.json();
            document.getElementById('login_area').style.display = 'none';
            document.getElementById('dashboard').style.display = 'block';
            document.getElementById('empresa_nome').innerText = d.empresa;
            document.getElementById('uso').innerText = d.usadas;
            document.getElementById('total').innerText = d.limite;
            
            let html = "";
            d.hist.reverse().forEach((txt, i) => {
                html += `
                <div class="hist-item" id="item-${i}">
                    <input type="checkbox" class="checkbox-item" onchange="toggleSelect(this, 'item-${i}')" data-info="${txt}">
                    <span style="flex-grow:1; font-size:13px;">${txt}</span>
                    <button class="btn-copy" onclick="copy('${txt.split(' | ')[2]}')">COPIAR</button>
                </div>`;
            });
            document.getElementById('lista_historico').innerHTML = html;
        }

        function toggleSelect(cb, id) {
            const el = document.getElementById(id);
            if(cb.checked) el.classList.add('selected'); else el.classList.remove('selected');
        }

        function selecionarTudo(source) {
            document.querySelectorAll('.checkbox-item').forEach(cb => {
                cb.checked = source.checked;
                toggleSelect(cb, cb.parentElement.id);
            });
        }

        function copy(t) { navigator.clipboard.writeText(t); alert("Copiado!"); }

        async function gerar() {
            const obs = document.getElementById('obs').value || "GERAL";
            const res = await fetch('/v1/cliente/gerar', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ pin: pinAtivo, obs: obs })
            });
            if(res.ok) { atualizarUI(); document.getElementById('obs').value = ""; } else { alert("Sem créditos!"); }
        }

        function exportarExcel() {
            const marcados = document.querySelectorAll('.checkbox-item:checked');
            if(marcados.length === 0) return alert("Selecione os itens primeiro!");
            let csv = "DATA | OBS | CHAVE\\n";
            marcados.forEach(m => csv += m.getAttribute('data-info') + "\\n");
            const blob = new Blob([csv], { type: 'text/csv' });
            const a = document.createElement('a');
            a.href = URL.createObjectURL(blob);
            a.download = `Relatorio_Quantum_${pinAtivo}.csv`;
            a.click();
        }

        // Funções Admin
        async function add() {
            const p = document.getElementById('p').value;
            if(p.length !== 6) return alert("O PIN deve ter 6 dígitos.");
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
            let h = "<table border='1' style='width:100%; margin-top:20px; border-collapse:collapse;'><tr><th>Empresa</th><th>PIN</th><th>Uso</th></tr>";
            dados.forEach(c => h += `<tr><td>${c.n}</td><td>${c.p}</td><td>${c.u}/${c.l}</td></tr>`);
            document.getElementById('lista_admin').innerHTML = h + "</table>";
        }
    </script>
</body>
</html>
"""

# --- ROTAS API --- (Não altere estas rotas para manter compatibilidade com o banco)
@app.route('/')
def home(): return render_template_string(HTML_SISTEMA, tipo='login')

@app.route('/painel-secreto-kleber')
def admin_page(): return render_template_string(HTML_SISTEMA, tipo='admin')

@app.route('/v1/cliente/dados')
def get_dados():
    pin = request.args.get('pin')
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT nome_empresa, acessos, limite, historico_chaves FROM clientes WHERE pin_hash = %s", (pin,))
    c = cur.fetchone(); cur.close(); conn.close()
    if c: return jsonify({"empresa": c[0], "usadas": c[1], "limite": c[2], "hist": c[3]})
    return jsonify({"erro": "n"}), 404

@app.route('/v1/cliente/gerar', methods=['POST'])
def gerar_api():
    data = request.json
    pin = data.get('pin')
    obs = data.get('obs', 'GERAL').upper()
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT acessos, limite FROM clientes WHERE pin_hash = %s", (pin,))
    c = cur.fetchone()
    if c and c[0] < c[1]:
        nk = generate_quantum_key(30)
        registro = f"{datetime.now().strftime('%d/%m/%Y %H:%M')} | {obs} | {nk}"
        cur.execute("UPDATE clientes SET acessos=acessos+1, historico_chaves=array_append(historico_chaves, %s) WHERE pin_hash=%s", (registro, pin))
        conn.commit(); cur.close(); conn.close()
        return jsonify({"key": nk})
    cur.close(); conn.close()
    return jsonify({"erro": "Full"}), 403

@app.route('/admin/cadastrar', methods=['POST'])
def add_cli():
    d = request.json
    if not ADMIN_KEY or d.get('key') != ADMIN_KEY: return jsonify({"erro": "Erro"}), 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("INSERT INTO clientes (nome_empresa, pin_hash, limite, historico_chaves) VALUES (%s, %s, %s, '{}')", (d['n'], d['p'], d['l']))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"msg": "OK"})

@app.route('/admin/listar')
def list_all():
    if not ADMIN_KEY or request.args.get('key') != ADMIN_KEY: return jsonify([]), 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT nome_empresa, pin_hash, COALESCE(acessos,0), COALESCE(limite,0) FROM clientes ORDER BY id DESC")
    r = cur.fetchall(); cur.close(); conn.close()
    return jsonify([{"n": x[0], "p": x[1], "u": x[2], "l": x[3]} for x in r])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))