import os
import secrets
import string
import psycopg2
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

ADMIN_KEY = os.environ.get('ADMIN_KEY', 'CHAVE_MESTRA_123') # Defina no seu ambiente

def get_db_connection():
    url = os.environ.get('DATABASE_URL')
    if url and url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return psycopg2.connect(url, sslmode='require')

def generate_quantum_key(length=30):
    chars = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))

# --- TEMPLATE HTML INTEGRADO ---
HTML_SISTEMA = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>KEYQUANTUM | 2026</title>
    <style>
        body { background: #0b1120; color: white; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; text-align: center; padding: 20px; }
        .container { background: #1e293b; padding: 30px; border-radius: 20px; display: inline-block; width: 95%; max-width: 700px; border: 1px solid #334155; box-shadow: 0 10px 25px rgba(0,0,0,0.3); }
        h1 { color: #38bdf8; letter-spacing: 2px; }
        input { padding: 12px; margin: 10px 0; background: #0f172a; border: 1px solid #334155; color: white; border-radius: 8px; width: 85%; font-size: 1rem; }
        button { padding: 12px 20px; background: #0284c7; border: none; color: white; cursor: pointer; border-radius: 8px; font-weight: bold; transition: 0.3s; }
        button:hover { background: #0369a1; }
        .btn-main { background: #22c55e; width: 90%; font-size: 1.1rem; margin-top: 15px; }
        .card { background: #0f172a; padding: 20px; border-radius: 15px; text-align: left; margin-top: 20px; border-top: 4px solid #38bdf8; }
        .key-display { background: #ffffff; color: #0f172a; padding: 15px; font-family: monospace; border-radius: 8px; margin: 15px 0; word-break: break-all; font-weight: bold; text-align: center; font-size: 1.2rem; border: 2px solid #38bdf8; }
        .hist-item { background: #1e293b; padding: 12px; margin-top: 10px; border-radius: 8px; font-size: 12px; border: 1px solid #334155; display: flex; justify-content: space-between; align-items: center; }
        table { width: 100%; margin-top: 20px; border-collapse: collapse; font-size: 13px; }
        th, td { border: 1px solid #334155; padding: 10px; text-align: left; }
        
        /* Estilo de Impressão */
        @media print {
            body { background: white; color: black; }
            .container { border: none; box-shadow: none; width: 100%; max-width: 100%; }
            button, input, h1, .btn-main { display: none !important; }
            .hist-item { color: black; border: 1px solid #000; }
            .card { border: none; }
        }
    </style>
</head>
<body>
    <div class="container">
        {% if tipo == 'admin' %}
            <h2 style="color:#38bdf8">ADMIN | KEYQUANTUM</h2>
            <input type="password" id="mestre" placeholder="Chave Mestre">
            <button onclick="listar()">LISTAR CLIENTES</button>
            <hr style="border:0; border-top:1px solid #334155; margin:30px 0;">
            <h3>CADASTRAR NOVO CLIENTE</h3>
            <input type="text" id="n" placeholder="Nome da Empresa">
            <input type="text" id="p" placeholder="PIN (6 dígitos numéricos)" maxlength="6">
            <input type="number" id="l" placeholder="Limite de Créditos" value="10">
            <button onclick="add()" style="background:#22c55e; width: 85%;">ATIVAR ACESSO</button>
            <div id="lista_admin"></div>
        {% else %}
            <h1>KEYQUANTUM</h1>
            <div id="login_area">
                <input type="text" id="pin" placeholder="DIGITE SEU PIN DE 6 DÍGITOS" maxlength="6">
                <button onclick="entrar_painel()" style="width:85%">ENTRAR NO PAINEL</button>
            </div>
            
            <div id="cliente_dashboard" style="display:none;">
                <div class="card">
                    <h2 id="msg_boas_vindas" style="margin:0; color:#38bdf8"></h2>
                    <p>Uso de Créditos: <b id="uso">0</b> / <b id="total">0</b></p>
                    <input type="text" id="obs_input" placeholder="Observação (Ex: Lote 01, Setor A)" style="width:90%">
                    <button class="btn-main" onclick="gerar_chave()">GERAR CHAVE QUANTUM</button>
                    <div id="area_chave_nova"></div>
                    
                    <div style="margin-top:25px; display: flex; justify-content: space-between; align-items: center;">
                        <h4 style="color:#94a3b8; margin:0;">HISTÓRICO:</h4>
                        <div>
                            <button onclick="window.print()" style="background:#475569; font-size: 11px;">🖨️ IMPRIMIR</button>
                            <button onclick="exportarCSV()" style="background:#15803d; font-size: 11px;">📊 EXCEL (CSV)</button>
                        </div>
                    </div>
                    <div id="historico_lista"></div>
                </div>
            </div>
        {% endif %}
    </div>

    <script>
    let pin_atual = "";

    // Impede letras nos campos de PIN
    document.querySelectorAll('input[placeholder*="PIN"]').forEach(el => {
        el.addEventListener('input', function() { this.value = this.value.replace(/[^0-9]/g, ''); });
    });

    async function entrar_painel() {
        pin_atual = document.getElementById('pin').value;
        if(pin_atual.length !== 6) return alert("O PIN deve ter 6 dígitos.");
        const res = await fetch('/v1/cliente/dados?pin=' + pin_atual);
        if(res.ok) { atualizar_dados_cliente(); } else { alert("PIN Inválido!"); }
    }

    async function atualizar_dados_cliente() {
        const res = await fetch('/v1/cliente/dados?pin=' + pin_atual);
        const d = await res.json();
        document.getElementById('login_area').style.display = 'none';
        document.getElementById('cliente_dashboard').style.display = 'block';
        document.getElementById('msg_boas_vindas').innerText = "Olá, " + d.empresa;
        document.getElementById('uso').innerText = d.usadas;
        document.getElementById('total').innerText = d.limite;
        
        let histHtml = "";
        d.hist.slice().reverse().forEach(h => {
            histHtml += `<div class="hist-item"><span>${h}</span> <button onclick="copy('${h.split(' | ')[2]}')">COPIAR</button></div>`;
        });
        document.getElementById('historico_lista').innerHTML = histHtml;
    }

    function copy(t) { navigator.clipboard.writeText(t); alert("Chave copiada!"); }

    async function gerar_chave() {
        const obs = document.getElementById('obs_input').value || "WEB-APP";
        const res = await fetch('/v1/cliente/gerar', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ pin: pin_atual, obs: obs })
        });
        if(res.ok) {
            const d = await res.json();
            document.getElementById('area_chave_nova').innerHTML = `<div class="key-display">${d.key}</div>`;
            atualizar_dados_cliente();
        } else { alert("Sem créditos ou erro no servidor."); }
    }

    function exportarCSV() {
        const empresa = document.getElementById('msg_boas_vindas').innerText;
        let csv = "Data/Hora;Observacao;Chave\\n";
        document.querySelectorAll('.hist-item span').forEach(el => {
            csv += el.innerText.replaceAll(" | ", ";") + "\\n";
        });
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `Relatorio_Chaves_${pin_atual}.csv`;
        a.click();
    }

    // --- FUNÇÕES ADMIN ---
    async function add() {
        const p = document.getElementById('p').value;
        if(p.length !== 6) return alert("Erro: O PIN deve ter 6 dígitos.");
        const res = await fetch('/admin/cadastrar', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                key: document.getElementById('mestre').value,
                n: document.getElementById('n').value,
                p: p,
                l: document.getElementById('l').value
            })
        });
        const d = await res.json(); alert(d.msg || d.erro); listar();
    }

    async function listar() {
        const res = await fetch('/admin/listar?key=' + document.getElementById('mestre').value);
        if(!res.ok) return alert("Chave Mestre Incorreta");
        const dados = await res.json();
        let html = "<table><tr><th>Empresa</th><th>PIN</th><th>Uso</th><th>Ação</th></tr>";
        dados.forEach(c => {
            html += `<tr><td>${c.n}</td><td>${c.p}</td><td>${c.u}/${c.l}</td><td><button onclick="apagar('${c.p}')" style="background:red">DEL</button></td></tr>`;
        });
        document.getElementById('lista_admin').innerHTML = html + "</table>";
    }

    async function apagar(p) {
        if(!confirm("Deseja excluir este cliente?")) return;
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

# --- ROTAS API ---

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
def gerar():
    data = request.json
    pin = data.get('pin')
    obs = data.get('obs', 'S/ OBS').upper()
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
    if not ADMIN_KEY or d.get('key') != ADMIN_KEY: return jsonify({"erro": "Chave Mestra Inválida"}), 403
    
    pin = str(d.get('p', ''))
    if len(pin) != 6 or not pin.isdigit():
        return jsonify({"erro": "O PIN deve ter exatamente 6 dígitos numéricos."}), 400

    conn = get_db_connection(); cur = conn.cursor()
    try:
        cur.execute("INSERT INTO clientes (nome_empresa, pin_hash, limite, historico_chaves) VALUES (%s, %s, %s, '{}')", (d['n'], pin, d['l']))
        conn.commit()
        return jsonify({"msg": "Cliente cadastrado!"})
    except:
        return jsonify({"erro": "Erro (PIN duplicado?)"}), 400
    finally:
        cur.close(); conn.close()

@app.route('/admin/listar')
def list_all():
    if not ADMIN_KEY or request.args.get('key') != ADMIN_KEY: return jsonify([]), 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT nome_empresa, pin_hash, COALESCE(acessos,0), COALESCE(limite,0) FROM clientes ORDER BY id DESC")
    r = cur.fetchall(); cur.close(); conn.close()
    return jsonify([{"n": x[0], "p": x[1], "u": x[2], "l": x[3]} for x in r])

@app.route('/admin/deletar', methods=['DELETE'])
def deletar_cli():
    d = request.json
    if not ADMIN_KEY or d.get('key') != ADMIN_KEY: return jsonify({"erro": "Erro"}), 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("DELETE FROM clientes WHERE pin_hash = %s", (d.get('pin'),))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"msg": "OK"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))