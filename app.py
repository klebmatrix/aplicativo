import os, secrets, string, psycopg2, datetime
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# IMPORTAÇÃO DO RENDER
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
    # RESET DE TABELA PARA CORRIGIR O ERRO DE COLUNA
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        # Se a coluna não existe, vamos recriar a tabela do jeito certo
        try:
            cur.execute("SELECT nome_empresa FROM clientes LIMIT 1;")
        except:
            conn.rollback()
            print("Recriando tabela para corrigir colunas...")
            cur.execute("DROP TABLE IF EXISTS clientes;")
            cur.execute('''
                CREATE TABLE clientes (
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
<html>
<head>
    <meta charset="UTF-8">
    <title>QUANTUM MASTER</title>
    <style>
        body { font-family: sans-serif; text-align: center; padding: 40px; background: #f4f4f4; }
        .box { background: white; max-width: 400px; margin: auto; padding: 30px; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
        input { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 8px; box-sizing: border-box; }
        button { width: 100%; padding: 12px; background: #000; color: #fff; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; }
        .cli-row { text-align: left; background: #f9f9f9; padding: 10px; margin-top: 10px; border-radius: 5px; font-size: 14px; }
    </style>
</head>
<body>
    <div class="box">
        <h2>PAINEL ADMIN</h2>
        <input type="password" id="mestre" placeholder="Digite a ADMIN_KEY do Render">
        <button onclick="listar()">ENTRAR</button>
        
        <div id="resultado" style="display:none; margin-top:20px;">
            <hr>
            <h4>CADASTRAR NOVO</h4>
            <input type="text" id="n" placeholder="Nome da Empresa">
            <input type="text" id="p" placeholder="Senha (6 a 8 dígitos)" maxlength="8">
            <button style="background: #16a34a;" onclick="salvar()">SALVAR</button>
            <div id="lista" style="margin-top:20px;"></div>
        </div>
    </div>

    <script>
    async function listar() {
        const k = document.getElementById('mestre').value;
        const res = await fetch('/admin/listar?key=' + k);
        if(!res.ok) return alert("Chave incorreta ou erro no servidor!");
        
        document.getElementById('resultado').style.display = 'block';
        const dados = await res.json();
        let h = "<h4>CLIENTES:</h4>";
        dados.forEach(c => {
            h += `<div class="cli-row"><b>${c.n}</b> - PIN: ${c.p} <br> Uso: ${c.u}/${c.l}</div>`;
        });
        document.getElementById('lista').innerHTML = h;
    }

    async function salvar() {
        const k = document.getElementById('mestre').value;
        const n = document.getElementById('n').value;
        const p = document.getElementById('p').value;
        if(p.length < 6) return alert("O PIN deve ter no mínimo 6 dígitos!");
        
        await fetch('/admin/cadastrar', {
            method:'POST', headers:{'Content-Type':'application/json'},
            body: JSON.stringify({key:k, n:n, p:p})
        });
        listar();
    }
    </script>
</body>
</html>
"""

@app.route('/')
def home(): return "SISTEMA ONLINE"

@app.route('/painel-secreto-kleber')
def admin_page(): return render_template_string(HTML_SISTEMA)

@app.route('/admin/listar')
def list_adm():
    key_user = request.args.get('key', '').strip()
    if not ADMIN_KEY_RENDER or key_user != ADMIN_KEY_RENDER:
        return "Acesso Negado", 403

    conn = get_db_connection()
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