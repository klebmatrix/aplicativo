import os
import secrets
import string
import psycopg2
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

ADMIN_KEY = os.environ.get('ADMIN_KEY', 'ADMIN123')

def get_db_connection():
    url = os.environ.get('DATABASE_URL')
    if url and url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    try:
        return psycopg2.connect(url, sslmode='require')
    except Exception as e:
        print(f"Erro: {e}")
        return None

# --- HTML ATUALIZADO COM FUNÇÕES DE GESTÃO ---
HTML_SISTEMA = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>KEYQUANTUM | ADMIN 2026</title>
    <style>
        :root { --blue: #38bdf8; --dark: #0b1120; --card: #1e293b; --red: #ef4444; --green: #22c55e; }
        body { background: var(--dark); color: white; font-family: sans-serif; padding: 20px; }
        .container { max-width: 900px; margin: auto; background: var(--card); padding: 25px; border-radius: 15px; }
        input, select { padding: 10px; margin: 5px 0; background: #0f172a; border: 1px solid #334155; color: white; border-radius: 5px; }
        button { padding: 8px 15px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; color: white; margin: 2px; }
        
        table { width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 14px; }
        th, td { padding: 12px; border: 1px solid #334155; text-align: center; }
        th { background: #0f172a; color: var(--blue); }
        
        .status-ativo { color: var(--green); }
        .status-bloqueado { color: var(--red); }
        .badge { padding: 2px 8px; border-radius: 10px; font-size: 11px; background: #334155; }
    </style>
</head>
<body>
    <div class="container">
        {% if tipo == 'admin' %}
            <h1>GESTOR DE CLIENTES</h1>
            <input type="password" id="mestre" placeholder="Chave Mestra Admin">
            <button style="background:var(--blue)" onclick="listar()">ATUALIZAR LISTA</button>
            
            <div style="background:#0f172a; padding:15px; margin-top:20px; border-radius:10px;">
                <h3>Novo Cliente</h3>
                <input type="text" id="n" placeholder="Empresa">
                <input type="text" id="p" placeholder="PIN (6 dígitos)" maxlength="6">
                <input type="number" id="l" placeholder="Créditos Iniciais" value="10">
                <button style="background:var(--green)" onclick="add()">CADASTRAR</button>
            </div>

            <div id="lista_admin"></div>
        {% else %}
            <div id="login_area">
                <h1>KEYQUANTUM LOGIN</h1>
                <input type="text" id="pin" placeholder="PIN" maxlength="6">
                <button style="background:var(--blue); width:100%" onclick="entrar()">ENTRAR</button>
            </div>
            <div id="dashboard" style="display:none;">
                <h2 id="emp_nome"></h2>
                <p>Créditos: <b id="uso"></b> / <b id="total"></b></p>
                <div id="lista_historico"></div>
            </div>
        {% endif %}
    </div>

    <script>
    // --- FUNÇÕES ADMIN ---
    async function listar() {
        const k = document.getElementById('mestre').value;
        const res = await fetch('/admin/listar?key=' + k);
        const dados = await res.json();
        
        let h = `<table><tr>
            <th>Empresa</th><th>PIN</th><th>Saldo (Uso/Total)</th><th>Status</th><th>Ações</th>
        </tr>`;
        
        dados.forEach(c => {
            const statusTxt = c.ativo ? 'ATIVO' : 'BLOQUEADO';
            const statusClass = c.ativo ? 'status-ativo' : 'status-bloqueado';
            
            h += `<tr>
                <td>${c.n}</td>
                <td><code class="badge">${c.p}</code></td>
                <td>${c.u} / <b>${c.l}</b></td>
                <td class="${statusClass}">${statusTxt}</td>
                <td>
                    <button style="background:var(--blue)" onclick="addCredito('${c.p}')">+ Crédito</button>
                    <button style="background:orange" onclick="toggleStatus('${c.p}', ${c.ativo})">${c.ativo ? 'Bloquear' : 'Liberar'}</button>
                    <button style="background:var(--red)" onclick="apagar('${c.p}')">Excluir</button>
                </td>
            </tr>`;
        });
        document.getElementById('lista_admin').innerHTML = h + "</table>";
    }

    async function addCredito(pin) {
        const qtd = prompt("Quantas chaves deseja ADICIONAR?");
        if(!qtd) return;
        await fetch('/admin/adicionar-credito', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({key: document.getElementById('mestre').value, pin: pin, qtd: parseInt(qtd)})
        });
        listar();
    }

    async function toggleStatus(pin, atual) {
        await fetch('/admin/status', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({key: document.getElementById('mestre').value, pin: pin, ativo: !atual})
        });
        listar();
    }
    
    // Outras funções (add, apagar, entrar) permanecem iguais
    </script>
</body>
</html>
"""

# --- ROTAS DE GESTÃO NO BACKEND ---

@app.route('/admin/adicionar-credito', methods=['POST'])
def add_credito():
    d = request.json
    if d.get('key') != ADMIN_KEY: return jsonify({"e": 403}), 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("UPDATE clientes SET limite = limite + %s WHERE pin_hash = %s", (d['qtd'], d['pin']))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"m": "ok"})

@app.route('/admin/status', methods=['POST'])
def mudar_status():
    d = request.json
    if d.get('key') != ADMIN_KEY: return jsonify({"e": 403}), 403
    conn = get_db_connection(); cur = conn.cursor()
    # Assume que você tem a coluna 'ativo' no banco (BOOLEAN)
    cur.execute("UPDATE clientes SET ativo = %s WHERE pin_hash = %s", (d['ativo'], d['pin']))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"m": "ok"})

# No login do cliente, adicione a verificação:
@app.route('/v1/cliente/dados')
def get_dados():
    pin = request.args.get('pin')
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT nome_empresa, acessos, limite, historico_chaves, ativo FROM clientes WHERE pin_hash = %s", (pin,))
    c = cur.fetchone(); cur.close(); conn.close()
    if c:
        if not c[4]: return jsonify({"erro": "BLOQUEADO"}), 403
        return jsonify({"empresa": c[0], "usadas": c[1], "limite": c[2], "hist": c[3]})
    return jsonify({"erro": "404"}), 404