import os, secrets, string, psycopg2, datetime
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def get_db_connection():
    url = os.environ.get('DATABASE_URL')
    if not url: return None
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    try:
        return psycopg2.connect(url, sslmode='require')
    except:
        return None

# --- ESSA FUNÇÃO RESOLVE SEU ERRO DE COLUNA ---
@app.before_request
def init_db():
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        # Se a coluna 'empresa' não existir, vamos recriar a tabela
        try:
            cur.execute("SELECT empresa FROM clientes LIMIT 1;")
        except:
            conn.rollback() # Limpa o erro da tentativa anterior
            cur.execute('DROP TABLE IF EXISTS clientes CASCADE;')
            cur.execute('''
                CREATE TABLE clientes (
                    id SERIAL PRIMARY KEY,
                    empresa TEXT NOT NULL,
                    pin_hash TEXT UNIQUE NOT NULL,
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
        body { background: white !important; color: black; font-family: sans-serif; padding: 20px; }
        .container { max-width: 500px; margin: auto; border: 1px solid #ddd; padding: 20px; border-radius: 10px; }
        input { width: 100%; padding: 12px; margin: 10px 0; box-sizing: border-box; border: 1px solid #ccc; }
        .btn { width: 100%; padding: 12px; border: none; font-weight: bold; cursor: pointer; border-radius: 5px; }
        .btn-black { background: black; color: white; }
        .card { border: 1px solid #eee; padding: 10px; margin-top: 10px; display: flex; justify-content: space-between; }
        @media print { .no-print { display: none; } .print-now { display: block !important; } }
        .print-now { display: none; text-align: center; border: 10px double #000; padding: 40px; }
    </style>
</head>
<body>
    <div class="container no-print">
        {% if admin %}
            <h2>PAINEL ADMIN (BRANCO)</h2>
            <input type="text" id="n" placeholder="Nome da Empresa">
            <input type="text" id="p" placeholder="PIN de 6 dígitos" maxlength="6">
            <button class="btn btn-black" onclick="cadastrar()">CADASTRAR CLIENTE</button>
        {% else %}
            <div id="login">
                <h2>ACESSO CLIENTE</h2>
                <input type="password" id="pin" placeholder="Seu PIN de 6 dígitos" maxlength="6">
                <button class="btn btn-black" onclick="entrar()">ENTRAR</button>
            </div>
            <div id="dash" style="display:none;">
                <h3 id="nome_e"></h3>
                <input type="text" id="prod" placeholder="Referência do Produto">
                <button class="btn btn-black" onclick="gerar()">GERAR CERTIFICADO</button>
                <div id="lista"></div>
            </div>
        {% endif %}
    </div>
    <div id="cert" class="print-now"></div>

    <script>
    async function cadastrar() {
        const res = await fetch('/admin/cadastrar', {
            method:'POST', headers:{'Content-Type':'application/json'},
            body: JSON.stringify({empresa: document.getElementById('n').value, pin: document.getElementById('p').value})
        });
        if(res.ok) alert("Sucesso!"); else alert("Erro ao salvar.");
    }

    async function entrar() {
        const pin = document.getElementById('pin').value;
        const res = await fetch('/v1/cliente/dados?pin=' + pin);
        if(!res.ok) return alert("PIN não existe.");
        const d = await res.json();
        document.getElementById('login').style.display='none';
        document.getElementById('dash').style.display='block';
        document.getElementById('nome_e').innerText = d.empresa;
        let h = "";
        d.hist.reverse().forEach(t => {
            const p = t.split(' | ');
            h += `<div class="card"><span>${p[1]}</span><button onclick="imprimir('${t}')">VER</button></div>`;
        });
        document.getElementById('lista').innerHTML = h;
    }

    async function gerar() {
        const pin = document.getElementById('pin').value;
        await fetch('/v1/cliente/gerar', {
            method:'POST', headers:{'Content-Type':'application/json'},
            body: JSON.stringify({pin: pin, obs: document.getElementById('prod').value})
        });
        entrar();
    }

    function imprimir(texto) {
        const p = texto.split(' | ');
        document.getElementById('cert').innerHTML = `<h1>CERTIFICADO</h1><br><h2>${p[1]}</h2><br><p>Chave: ${p[2]}</p><p>${p[0]}</p>`;
        window.print();
    }
    </script>
</body>
</html>
"""

@app.route('/')
def home(): return render_template_string(HTML_SISTEMA, admin=False)

@app.route('/painel-secreto-kleber')
@app.route('/admin')
def admin_pg(): return render_template_string(HTML_SISTEMA, admin=True)

@app.route('/v1/cliente/dados')
def dados():
    pin = request.args.get('pin')
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT empresa, historico_chaves FROM clientes WHERE pin_hash = %s", (pin,))
    res = cur.fetchone()
    cur.close(); conn.close()
    return jsonify({"empresa": res[0], "hist": res[1]}) if res else (jsonify({}), 404)

@app.route('/v1/cliente/gerar', methods=['POST'])
def gerar_api():
    d = request.json
    conn = get_db_connection(); cur = conn.cursor()
    ch = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(12))
    info = f"{datetime.datetime.now().strftime('%d/%m/%Y')} | {d['obs'].upper()} | {ch}"
    cur.execute("UPDATE clientes SET historico_chaves = array_append(historico_chaves, %s) WHERE pin_hash = %s", (info, d['pin']))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"ok": True})

@app.route('/admin/cadastrar', methods=['POST'])
def add_api():
    d = request.json
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("INSERT INTO clientes (empresa, pin_hash, historico_chaves) VALUES (%s, %s, %s)", (d['empresa'], d['pin'], []))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"ok": True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))