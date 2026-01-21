import os, secrets, string, psycopg2
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Busca a chave quântica das variáveis de ambiente do Render
ADMIN_KEY = os.environ.get('ADMIN_KEY')

def get_db_connection():
    url = os.environ.get('DATABASE_URL')
    if not url: return None
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    try:
        return psycopg2.connect(url, sslmode='require', connect_timeout=10)
    except:
        return None

# O HTML foi atualizado com o botão "Limpar Histórico"
HTML_SISTEMA = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>SISTEMA QUANTUM | GESTÃO</title>
    <style>
        :root { --blue: #38bdf8; --dark: #0b1120; --card: #1e293b; --red: #ef4444; --green: #22c55e; }
        body { background: var(--dark); color: white; font-family: sans-serif; padding: 20px; }
        .container { max-width: 1000px; margin: auto; background: var(--card); padding: 25px; border-radius: 15px; border: 1px solid #334155; }
        input { padding: 10px; margin: 5px; background: #0f172a; border: 1px solid #334155; color: white; border-radius: 5px; }
        button { padding: 8px 12px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; color: white; margin: 2px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; background: #0f172a; }
        th, td { padding: 10px; border: 1px solid #334155; text-align: center; font-size: 13px; }
        .status-ativo { color: var(--green); } .status-bloqueado { color: var(--red); }
    </style>
</head>
<body>
    <div class="container">
        {% if tipo == 'admin' %}
            <h1>PAINEL DE CONTROLE</h1>
            <input type="password" id="mestre" placeholder="Chave Quântica Admin">
            <button style="background:var(--blue)" onclick="listar()">LISTAR DO BANCO</button>
            
            <div id="lista_admin"></div>
        {% else %}
            <div id="login_area">
                <h1>LOGIN QUANTUM</h1>
                <input type="text" id="pin" placeholder="PIN" maxlength="6">
                <button style="background:var(--blue); width:100%" onclick="entrar()">ENTRAR</button>
            </div>
            <div id="dashboard" style="display:none;">
                <h2 id="emp_nome"></h2>
                <div id="lista_historico"></div>
            </div>
        {% endif %}
    </div>

    <script>
    async function listar() {
        const k = document.getElementById('mestre').value;
        const res = await fetch('/admin/listar?key=' + k);
        if(!res.ok) return alert("Chave Admin Incorreta!");
        const dados = await res.json();
        let h = "<table><tr><th>Empresa</th><th>PIN</th><th>Uso/Total</th><th>Status</th><th>Ações</th></tr>";
        dados.forEach(c => {
            h += `<tr>
                <td>${c.n}</td><td>${c.p}</td><td>${c.u}/${c.l}</td>
                <td class="${c.a?'status-ativo':'status-bloqueado'}"><b>${c.a?'ATIVO':'BLOQUEADO'}</b></td>
                <td>
                    <button style="background:var(--blue)" onclick="addCr('${c.p}')">+ Crédito</button>
                    <button style="background:orange" onclick="altSt('${c.p}',${c.a})">Bloq/Lib</button>
                    <button style="background:#6366f1" onclick="limparHist('${c.p}')">Limpar Hist.</button>
                    <button style="background:var(--red)" onclick="del('${c.p}')">Remover</button>
                </td></tr>`;
        });
        document.getElementById('lista_admin').innerHTML = h + "</table>";
    }

    async function limparHist(p) {
        if(confirm("Deseja apagar TODAS as chaves geradas e zerar o consumo deste cliente?")) {
            const k = document.getElementById('mestre').value;
            await fetch('/admin/limpar_historico', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({key: k, pin: p})
            });
            listar();
        }
    }

    // ... (outras funções JS: addCr, altSt, del, entrar permanecem iguais) ...
    </script>
</body>
</html>
"""

# --- NOVAS ROTAS NO BACKEND ---

@app.route('/admin/limpar_historico', methods=['POST'])
def limpar_historico():
    d = request.json
    if d.get('key') != ADMIN_KEY: return jsonify({"e": 403}), 403
    conn = get_db_connection(); cur = conn.cursor()
    # Zera o contador de acessos e limpa o array de histórico
    cur.execute("UPDATE clientes SET acessos = 0, historico_chaves = '{}' WHERE pin_hash = %s", (d['pin'],))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"ok": True})

# ... (mantém as outras rotas: /admin/listar, /admin/cadastrar, etc.) ...