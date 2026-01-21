import os, secrets, string, psycopg2, datetime
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def get_db_connection():
    url = os.environ.get('DATABASE_URL')
    if not url: return None
    # Correção para o Render que usa postgres:// mas o Python pede postgresql://
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    try:
        return psycopg2.connect(url, sslmode='require')
    except Exception as e:
        print(f"ERRO DE CONEXÃO: {e}")
        return None

# --- HTML UNIFICADO ---
HTML_SISTEMA = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>SISTEMA QUANTUM</title>
    <style>
        body { background: white; font-family: sans-serif; padding: 20px; color: #1a1a1a; }
        .container { max-width: 600px; margin: auto; border: 1px solid #ddd; padding: 20px; border-radius: 8px; }
        input { padding: 12px; width: 100%; margin-bottom: 10px; box-sizing: border-box; border: 1px solid #ccc; }
        .btn { padding: 12px; width: 100%; cursor: pointer; border: none; font-weight: bold; border-radius: 4px; }
        .btn-black { background: #000; color: #fff; }
        .btn-blue { background: #2563eb; color: #fff; margin-top: 10px; }
        .card { border: 1px solid #eee; padding: 10px; margin-top: 10px; display: flex; justify-content: space-between; align-items: center; }
        @media print { .no-print { display: none; } .print-area { display: block !important; } }
        .print-area { display: none; text-align: center; padding: 50px; border: 10px double #000; height: 90vh; }
    </style>
</head>
<body>
    <div class="container no-print">
        {% if admin %}
            <h1>PAINEL ADMIN</h1>
            <input type="text" id="n" placeholder="Nome da Empresa">
            <input type="text" id="p" placeholder="PIN de 6 dígitos" maxlength="6">
            <button class="btn btn-black" onclick="salvar()">CADASTRAR CLIENTE</button>
            <div id="lista"></div>
        {% else %}
            <div id="login">
                <h1>ACESSO CLIENTE</h1>
                <input type="password" id="pin" placeholder="Digite seu PIN" maxlength="6">
                <button class="btn btn-black" onclick="entrar()">ENTRAR</button>
            </div>
            <div id="dash" style="display:none;">
                <h2 id="cliente_nome"></h2>
                <input type="text" id="prod" placeholder="Nome do Produto">
                <button class="btn btn-blue" onclick="gerar()">GERAR REGISTRO</button>
                <div id="hist"></div>
            </div>
        {% endif %}
    </div>
    <div id="cert" class="print-area"></div>

    <script>
    async function salvar() {
        const res = await fetch('/v1/admin/cadastrar', {
            method:'POST', headers:{'Content-Type':'application/json'},
            body: JSON.stringify({empresa: document.getElementById('n').value, pin: document.getElementById('p').value})
        });
        if(res.ok) { alert("Cadastrado!"); location.reload(); }
    }

    async function entrar() {
        const pin = document.getElementById('pin').value;
        const res = await fetch('/v1/cliente/dados?pin=' + pin);
        if(!res.ok) return alert("PIN Inválido!");
        const d = await res.json();
        document.getElementById('login').style.display='none';
        document.getElementById('dash').style.display='block';
        document.getElementById('cliente_nome').innerText = d.empresa;
        let h = "";
        d.hist.reverse().forEach((t, i) => {
            const p = t.split(' | ');
            h += `<div class="card"><span>${p[0]}<br><b>${p[1]}</b></span><button onclick="imprimir('${t}')">IMPRIMIR</button></div>`;
        });
        document.getElementById('hist').innerHTML = h;
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
        document.getElementById('cert').innerHTML = `<h1>CERTIFICADO</h1><br><h2>${p[1]}</h2><br><p>Chave: ${p[2]}</p><br><p>${p[0]}</p>`;
        window.print();
    }
    </script>
</body>
</html>
"""

@app.route('/')
def home(): return render_template_string(HTML_SISTEMA, admin=False)

@app.route('/admin')
def admin_page(): return render_template_string(HTML_SISTEMA, admin=True)

@app.route('/v1/cliente/dados')
def dados():
    pin = request.args.get('pin')
    conn = get_db_connection()
    if not conn: return jsonify({"error": "Falha no banco"}), 500
    cur = conn.cursor()
    cur.execute("SELECT empresa, historico_chaves FROM clientes WHERE pin_hash = %s", (pin,))
    res = cur.fetchone()
    cur.close(); conn.close()
    return jsonify({"empresa": res[0], "hist": res[1]}) if res else (jsonify({}), 404)

@app.route('/v1/cliente/gerar', methods=['POST'])
def gerar():
    d = request.json
    conn = get_db_connection(); cur = conn.cursor()
    chave = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(15))
    info = f"{datetime.datetime.now().strftime('%d/%m/%Y')} | {d['obs'].upper()} | {chave}"
    cur.execute("UPDATE clientes SET historico_chaves = array_append(historico_chaves, %s) WHERE pin_hash = %s", (info, d['pin']))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"ok": True})

@app.route('/v1/admin/cadastrar', methods=['POST'])
def cadastrar():
    d = request.json
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("INSERT INTO clientes (empresa, pin_hash, historico_chaves) VALUES (%s, %s, %s)", (d['empresa'], d['pin'], []))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"ok": True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))