import os
import psycopg2
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

ADMIN_KEY = os.environ.get('ADMIN_KEY', 'admin')

def get_db_connection():
    # Pega o link do Render
    url = os.environ.get('DATABASE_URL')
    if not url:
        raise Exception("Falta a variável DATABASE_URL no Render!")
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return psycopg2.connect(url, sslmode='require')

@app.route('/')
def home():
    return "<h1>SISTEMA ONLINE - AGUARDANDO PIN</h1>"

@app.route('/painel-secreto-kleber')
def admin():
    return render_template_string('''
        <body style="background:#111; color:white; text-align:center;">
            <h2>PAINEL DE DIAGNÓSTICO</h2>
            <input type="password" id="k" placeholder="Chave Mestre">
            <button onclick="testar()">TESTAR CONEXÃO E LISTAR</button>
            <div id="res"></div>
            <script>
                async function testar() {
                    const k = document.getElementById('k').value;
                    const r = document.getElementById('res');
                    r.innerHTML = "Tentando conectar...";
                    try {
                        const res = await fetch('/admin/listar?key=' + k);
                        const dados = await res.json();
                        if (res.status === 403) { r.innerHTML = "ERRO: Chave Mestre Errada!"; return; }
                        r.innerHTML = "CONECTADO! Itens no banco: " + JSON.stringify(dados);
                    } catch (e) {
                        r.innerHTML = "ERRO FATAL: " + e;
                    }
                }
            </script>
        </body>
    ''')

@app.route('/admin/listar')
def l():
    if request.args.get('key') != ADMIN_KEY:
        return jsonify({"erro": "Chave incorreta"}), 403
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # Tenta criar a tabela na hora da listagem se não existir
        cur.execute("CREATE TABLE IF NOT EXISTS clientes (nome_empresa TEXT, pin_hash TEXT)")
        cur.execute("SELECT nome_empresa, pin_hash FROM clientes")
        r = cur.fetchall()
        cur.close(); conn.close()
        return jsonify([{"n":x[0], "p":x[1]} for x in r])
    except Exception as e:
        return jsonify({"erro_de_banco": str(e)}), 500

@app.route('/v1/quantum-key', methods=['POST'])
def v():
    p = request.json.get('pin')
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT nome_empresa FROM clientes WHERE pin_hash=%s", (p,))
        f = cur.fetchone()
        cur.close(); conn.close()
        if f: return jsonify({"status":"Liberado", "empresa":f[0], "key": "OK-123"})
    except: pass
    return jsonify({"status":"Negado"}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))