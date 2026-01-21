import os, secrets, string, psycopg2, datetime
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- IMPORTAÇÃO DAS VARIÁVEIS DE AMBIENTE DO RENDER ---
# O sistema busca a chave 'ADMIN_KEY' configurada no seu painel do Render
ADMIN_KEY_RENDER = os.environ.get('ADMIN_KEY')

def get_db_connection():
    url = os.environ.get('DATABASE_URL')
    if not url: return None
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    try:
        return psycopg2.connect(url, sslmode='require')
    except:
        return None

@app.before_request
def init_db():
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
        conn.commit()
        cur.close(); conn.close()

HTML_SISTEMA = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>SISTEMA QUANTUM</title>
    <style>
        body { background: white; font-family: sans-serif; padding: 30px; text-align: center; }
        .box { max-width: 450px; margin: auto; border: 1px solid #ccc; padding: 25px; border-radius: 15px; }
        input { width: 90%; padding: 12px; margin: 10px 0; border: 1px solid #000; border-radius: 5px; }
        button { width: 95%; padding: 12px; background: black; color: white; border: none; cursor: pointer; font-weight: bold; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="box">
        <h2>PAINEL MASTER</h2>
        <p style="font-size: 12px; color: gray;">Validando chave via Ambiente Render</p>
        <input type="password" id="mestre" placeholder="Digite a ADMIN_KEY">
        <button onclick="acessar()">ENTRAR</button>
        
        <div id="resultado" style="display:none; margin-top:20px; text-align: left;">
            <hr>
            <h4>CADASTRAR CLIENTE</h4>
            <input type="text" id="n" placeholder="Nome Empresa">
            <input type="text" id="p" placeholder="PIN (6-8 dig)" maxlength="8">
            <button style="background: green;" onclick="salvar()">SALVAR</button>
            <div id="tabela" style="margin-top:20px;"></div>
        </div>
    </div>

    <script>
    async function acessar() {
        const k = document.getElementById('mestre').value;
        const res = await fetch('/admin/listar?key=' + k);
        if(!res.ok) return alert("Erro: Chave de Ambiente Inválida!");
        
        document.getElementById('resultado').style.display = 'block';
        const dados = await res.json();
        let h = "<table>";
        dados.forEach(c => {
            h += `<tr><td>${c.n}</td><td><b>${c.p}</b></td><td>${c.u}/${c.l}</td></tr>`;
        });
        document.getElementById('tabela').innerHTML = h + "</table>";
    }

    async function salvar() {
        const k = document.getElementById('mestre').value;
        const n = document.getElementById('n').value;
        const p = document.getElementById('p').value;
        if(p.length < 6) return alert("PIN deve ter 6-8 digitos!");
        await fetch('/admin/cadastrar', {
            method:'POST', headers:{'Content-Type':'application/json'},
            body: JSON.stringify({key:k, n:n, p:p})
        });
        acessar();
    }
    </script>
</body>
</html>
"""

@app.route('/')
def home(): return "SISTEMA ATIVO"

@app.route('/painel-secreto-kleber')
def admin_page(): return render_template_string(HTML_SISTEMA)

@app.route('/admin/listar')
def list_adm():
    # Verifica se a chave digitada é igual à importada do ambiente do Render
    key_digitada = request.args.get('key', '').strip()
    if not ADMIN_KEY_RENDER or key_digitada != ADMIN_KEY_RENDER:
        return jsonify({"erro": "Acesso Proibido"}), 403

    conn = get_db_connection()
    if not conn: return jsonify([]), 500
    cur = conn.cursor()
    cur.execute("SELECT nome_empresa, pin_hash, acessos, limite FROM clientes")
    r = cur.fetchall(); cur.close(); conn.close()
    return jsonify([{"n": x[0], "p": x[1], "u": x[2], "l": x[3]} for x in r])

@app.route('/admin/cadastrar', methods=['POST'])
def add_adm():
    d = request.json
    if d.get('key') != ADMIN_KEY_RENDER: return "Erro", 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("INSERT INTO clientes (nome_empresa, pin_hash, limite) VALUES (%s, %s, %s)", (d['n'], d['p'], 100))
    conn.commit(); cur.close(); conn.close()
    return "OK"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))