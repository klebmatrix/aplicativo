import os, secrets, string, psycopg2, datetime
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Função de conexão com log de erro para o Render
def get_db_connection():
    url = os.environ.get('DATABASE_URL')
    if not url:
        return None
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    try:
        return psycopg2.connect(url, sslmode='require', connect_timeout=5)
    except Exception as e:
        print(f"ERRO CRÍTICO DE CONEXÃO: {e}")
        return None

# Template único com CSS embutido para evitar falha de carregamento
HTML_SISTEMA = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>SISTEMA QUANTUM</title>
    <style>
        body { background: #ffffff !important; color: #1a1a1a; font-family: sans-serif; padding: 20px; }
        .box { max-width: 500px; margin: 40px auto; border: 1px solid #ddd; padding: 30px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
        input { width: 100%; padding: 12px; margin: 10px 0; box-sizing: border-box; border: 1px solid #ccc; border-radius: 6px; }
        .btn { width: 100%; padding: 12px; cursor: pointer; font-weight: bold; border: none; border-radius: 6px; transition: 0.2s; }
        .btn-black { background: #000; color: #fff; }
        .card { border: 1px solid #eee; padding: 12px; margin-top: 10px; display: flex; justify-content: space-between; align-items: center; border-radius: 6px; background: #f9f9f9; }
        @media print { .no-print { display: none !important; } .print-area { display: block !important; } }
        .print-area { display: none; text-align: center; border: 15px double #000; padding: 40px; height: 95vh; box-sizing: border-box; }
    </style>
</head>
<body>
    <div class="box no-print">
        {% if admin %}
            <h2 style="text-align:center;">PAINEL ADMIN</h2>
            <p>Cadastrar novo PIN de 6 dígitos:</p>
            <input type="text" id="n" placeholder="Nome da Empresa">
            <input type="text" id="p" placeholder="PIN de 6 dígitos" maxlength="6">
            <button class="btn btn-black" onclick="cadastrar()">CADASTRAR CLIENTE</button>
            <p style="font-size: 12px; color: gray; text-align: center; margin-top: 20px;">Acesse / para voltar ao login</p>
        {% else %}
            <div id="login-section">
                <h2 style="text-align:center;">ACESSO CLIENTE</h2>
                <input type="password" id="pin-val" placeholder="Digite seu PIN de 6 dígitos" maxlength="6">
                <button class="btn btn-black" onclick="fazerLogin()">ENTRAR</button>
                <p style="text-align:center; font-size:12px; margin-top:15px; color:#666;">Sistema Quantum v2.0</p>
            </div>
            <div id="dash-section" style="display:none;">
                <h3 id="empresa-nome" style="color: #2563eb;"></h3>
                <input type="text" id="prod-nome" placeholder="Nome do Produto/Equipamento">
                <button class="btn btn-black" onclick="gerar()">REGISTRAR E GERAR CHAVE</button>
                <div id="lista-chaves"></div>
            </div>
        {% endif %}
    </div>

    <div id="cert-area" class="print-area"></div>

    <script>
    async function cadastrar() {
        const n = document.getElementById('n').value;
        const p = document.getElementById('p').value;
        if(!n || !p) return alert("Preencha todos os campos");
        const res = await fetch('/v1/admin/cadastrar', {
            method:'POST', headers:{'Content-Type':'application/json'},
            body: JSON.stringify({empresa: n, pin: p})
        });
        if(res.ok) alert("Cliente registrado!");
        else alert("Erro ao registrar no banco.");
    }

    async function fazerLogin() {
        const pin = document.getElementById('pin-val').value;
        const res = await fetch('/v1/cliente/dados?pin=' + pin);
        if(!res.ok) return alert("PIN incorreto ou erro de conexão!");
        const d = await res.json();
        document.getElementById('login-section').style.display='none';
        document.getElementById('dash-section').style.display='block';
        document.getElementById('empresa-nome').innerText = d.empresa;
        renderizarLista(d.hist);
    }

    function renderizarLista(hist) {
        let html = "";
        [...hist].reverse().forEach(t => {
            const p = t.split(' | ');
            html += `<div class="card"><span><b>${p[1]}</b><br><small>${p[0]}</small></span><button class="btn" style="width:70px; background:#eee; color:#000;" onclick="imprimir('${t}')">IMPRIMIR</button></div>`;
        });
        document.getElementById('lista-chaves').innerHTML = html;
    }

    async function gerar() {
        const pin = document.getElementById('pin-val').value;
        const obs = document.getElementById('prod-nome').value || "PRODUTO";
        const res = await fetch('/v1/cliente/gerar', {
            method:'POST', headers:{'Content-Type':'application/json'},
            body: JSON.stringify({pin: pin, obs: obs})
        });
        if(res.ok) fazerLogin();
    }

    function imprimir(texto) {
        const p = texto.split(' | ');
        document.getElementById('cert-area').innerHTML = `
            <h1 style="font-size:40px;">CERTIFICADO</h1>
            <p style="letter-spacing:5px;">AUTENTICIDADE QUANTUM</p>
            <div style="margin:60px 0; border:1px solid #000; padding:20px;">
                <p>PRODUTO REGISTRADO:</p>
                <h2 style="font-size:30px;">${p[1]}</h2>
                <p>CHAVE ÚNICA DE IDENTIFICAÇÃO:</p>
                <h3 style="font-family:monospace;">${p[2]}</h3>
            </div>
            <p>DATA DO REGISTRO: ${p[0]}</p>
        `;
        window.print();
    }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_SISTEMA, admin=False)

@app.route('/admin')
def admin():
    return render_template_string(HTML_SISTEMA, admin=True)

@app.route('/v1/cliente/dados')
def get_dados():
    pin = request.args.get('pin')
    conn = get_db_connection()
    if not conn: return jsonify({"error": "DB Error"}), 500
    cur = conn.cursor()
    cur.execute("SELECT empresa, historico_chaves FROM clientes WHERE pin_hash = %s", (pin,))
    res = cur.fetchone()
    cur.close(); conn.close()
    if res: return jsonify({"empresa": res[0], "hist": res[1]})
    return jsonify({"error": "Not Found"}), 404

@app.route('/v1/cliente/gerar', methods=['POST'])
def gerar():
    d = request.json
    conn = get_db_connection()
    if not conn: return jsonify({"error": "DB Error"}), 500
    cur = conn.cursor()
    chave = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(16))
    data = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
    registro = f"{data} | {d['obs'].upper()} | {chave}"
    cur.execute("UPDATE clientes SET historico_chaves = array_append(historico_chaves, %s) WHERE pin_hash = %s", (registro, d['pin']))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"ok": True})

@app.route('/v1/admin/cadastrar', methods=['POST'])
def cadastrar():
    d = request.json
    conn = get_db_connection()
    if not conn: return jsonify({"error": "DB Error"}), 500
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO clientes (empresa, pin_hash, historico_chaves) VALUES (%s, %s, %s)", (d['empresa'], d['pin'], []))
        conn.commit()
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cur.close(); conn.close()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)