import os, psycopg2, datetime, time, random
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Extração de segurança das variáveis do Render
MASTER_KEY = os.environ.get('ADMIN_KEY') or os.environ.get('admin_key')

def get_db_connection():
    url = os.environ.get('DATABASE_URL')
    if url and url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    try:
        return psycopg2.connect(url, sslmode='require')
    except:
        return None

@app.before_request
def setup_db():
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id SERIAL PRIMARY KEY,
                nome_empresa TEXT NOT NULL,
                pin_hash TEXT UNIQUE NOT NULL,
                limite INTEGER DEFAULT 100,
                acessos INTEGER DEFAULT 0,
                historico_chaves TEXT[] DEFAULT '{}'
            );
        ''')
        conn.commit(); cur.close(); conn.close()

# --- INTERFACE HTML COM IQ E GESTÃO DE SALDO ---
HTML_SISTEMA = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>SISTEMA QUANTUM - GESTÃO</title>
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Montserrat:wght@400;600&display=swap" rel="stylesheet">
    <style>
        :root { --gold: #c5a059; --red: #ff4d4d; --green: #2ecc71; --bg: #05070a; }
        body { background: var(--bg); color: white; font-family: 'Montserrat', sans-serif; padding: 20px; }
        .container { max-width: 900px; margin: auto; background: #0f172a; padding: 25px; border-radius: 15px; border: 1px solid var(--gold); }
        h1 { font-family: 'Cinzel', serif; color: var(--gold); text-align: center; }
        input { width: 100%; padding: 10px; margin: 10px 0; border-radius: 5px; border: 1px solid #334155; background: #1e293b; color: white; }
        .btn { padding: 10px 20px; cursor: pointer; border-radius: 5px; border: none; font-weight: bold; transition: 0.3s; }
        .btn-add { background: var(--gold); color: black; width: 100%; }
        .btn-del { background: var(--red); color: white; }
        .btn-edit { background: #3498db; color: white; margin-left: 5px; }
        
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th { border-bottom: 2px solid var(--gold); padding: 10px; text-align: left; }
        td { padding: 12px; border-bottom: 1px solid rgba(255,255,255,0.1); }
        
        /* IQ Status Label */
        .iq-tag { padding: 2px 8px; border-radius: 10px; font-size: 10px; font-weight: bold; text-transform: uppercase; }
        .iq-active { background: var(--green); color: black; }
        .iq-expired { background: var(--red); color: white; }
    </style>
</head>
<body>
    <div class="container">
        {% if modo == 'admin' %}
            <h1>PAINEL DE CONTROLE MASTER</h1>
            <input type="password" id="ak" placeholder="DIGITE SUA ADMIN_KEY">
            <button class="btn btn-add" onclick="listar()">SINCRONIZAR GESTÃO</button>
            
            <div id="lista_admin"></div>

            <hr style="margin:30px 0; opacity:0.2">
            <h3>CADASTRAR / RENOVAR ASSINATURA</h3>
            <input type="text" id="n" placeholder="Nome do Cliente">
            <input type="text" id="p" placeholder="PIN (6-8 dígitos)">
            <input type="number" id="l" placeholder="Créditos de Saldo">
            <button class="btn btn-add" onclick="salvar()">ATIVAR / ATUALIZAR SALDO</button>
        {% else %}
            <div id="login">
                <h1>ACESSO CLIENTE</h1>
                <input type="password" id="pin" placeholder="Seu PIN">
                <button class="btn btn-add" onclick="logar()">ENTRAR</button>
            </div>
            <div id="dash" style="display:none">
                <h2 id="nome_cli"></h2>
                <div id="historico_iq"></div>
            </div>
        {% endif %}
    </div>

    <script>
    async function listar() {
        const k = document.getElementById('ak').value;
        const res = await fetch(`/api/admin/list?k=${k}`);
        if(!res.ok) return alert("Chave Inválida");
        const data = await res.json();
        
        let h = "<table><tr><th>Cliente / PIN</th><th>Saldo</th><th>Ações</th></tr>";
        data.forEach(c => {
            h += `<tr>
                <td><b>${c.n}</b><br><small>${c.p}</small></td>
                <td>${c.u} / ${c.l}</td>
                <td>
                    <button class="btn btn-del" onclick="remover('${c.p}')">Excluir</button>
                    <button class="btn btn-edit" onclick="prepararEdicao('${c.n}','${c.p}','${c.l}')">Add Crédito</button>
                </td>
            </tr>`;
        });
        document.getElementById('lista_admin').innerHTML = h + "</table>";
    }

    function prepararEdicao(nome, pin, limite) {
        document.getElementById('n').value = nome;
        document.getElementById('p').value = pin;
        document.getElementById('l').value = limite;
        window.scrollTo(0, document.body.scrollHeight);
    }

    async function salvar() {
        const k = document.getElementById('ak').value;
        const payload = { 
            k: k, 
            n: document.getElementById('n').value, 
            p: document.getElementById('p').value, 
            l: parseInt(document.getElementById('l').value) 
        };
        const res = await fetch('/api/admin/save', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload) });
        if(res.ok) { alert("Saldo/Assinatura Atualizada!"); listar(); }
    }

    async function remover(pin) {
        const k = document.getElementById('ak').value;
        if(confirm("Excluir assinatura e histórico deste cliente?")) {
            await fetch('/api/admin/delete', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({k:k, p:pin}) });
            listar();
        }
    }

    // Lógica do IQ (Índice Quântico) no Cliente
    function calcularIQ(dataValidade) {
        const hoje = new Date();
        const [dia, mes, ano] = dataValidade.split('/');
        const validade = new Date(ano, mes - 1, dia);
        return hoje <= validade ? '<span class="iq-tag iq-active">Ativo</span>' : '<span class="iq-tag iq-expired">Expirado</span>';
    }
    </script>
</body>
</html>
"""

# --- ROTAS DE GESTÃO (CRUD) ---

@app.route('/api/admin/list')
def api_l():
    k = request.args.get('k')
    if not MASTER_KEY or k != MASTER_KEY: return "Err", 403
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT nome_empresa, pin_hash, acessos, limite FROM clientes ORDER BY id DESC")
    r = cur.fetchall(); cur.close(); conn.close()
    return jsonify([{"n": x[0], "p": x[1], "u": x[2], "l": x[3]} for x in r])

@app.route('/api/admin/save', methods=['POST'])
def api_s():
    d = request.json
    if not MASTER_KEY or d.get('k') != MASTER_KEY: return "Err", 403
    conn = get_db_connection()
    cur = conn.cursor()
    # ON CONFLICT UPDATE permite que você apenas "salve por cima" para dar créditos
    cur.execute('''
        INSERT INTO clientes (nome_empresa, pin_hash, limite) VALUES (%s, %s, %s) 
        ON CONFLICT (pin_hash) DO UPDATE SET limite = EXCLUDED.limite, nome_empresa = EXCLUDED.nome_empresa
    ''', (d['n'], d['p'], d['l']))
    conn.commit(); cur.close(); conn.close()
    return "OK"

@app.route('/api/admin/delete', methods=['POST'])
def api_delete():
    d = request.json
    if not MASTER_KEY or d.get('k') != MASTER_KEY: return "Err", 403
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM clientes WHERE pin_hash = %s", (d['p'],))
    conn.commit(); cur.close(); conn.close()
    return "OK"

# ... (Manter as outras rotas /api/cli/info e /api/cli/generate do código anterior)

@app.route('/painel-secreto-kleber')
def r_a(): return render_template_string(HTML_SISTEMA, modo='admin')

@app.route('/')
def r_h(): return render_template_string(HTML_SISTEMA, modo='cliente')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))