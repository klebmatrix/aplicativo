import os
import secrets
import psycopg2
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Chave mestre vinda do Render ou padrão 'admin'
ADMIN_KEY = os.environ.get('ADMIN_KEY', 'admin')

def get_db_connection():
    url = os.environ.get('DATABASE_URL')
    if not url:
        print("ALERTA: DATABASE_URL NÃO CONFIGURADA NO RENDER!")
        return None
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return psycopg2.connect(url, sslmode='require')

# Teste de conexão imediato ao ligar o servidor
try:
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id SERIAL PRIMARY KEY,
                nome_empresa TEXT NOT NULL,
                pin_hash TEXT UNIQUE NOT NULL,
                ultimo_acesso TIMESTAMP,
                ultimo_ip TEXT
            )
        ''')
        conn.commit()
        print("CONEXÃO COM POSTGRESQL: SUCESSO!")
        cur.close(); conn.close()
except Exception as e:
    print(f"ERRO FATAL NA CONEXÃO DO BANCO: {e}")

# --- HTML IGUAL AO ANTERIOR ---
HTML_ADMIN = """
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>ADMIN</title></head>
<body style="background:#0f172a; color:white; font-family:sans-serif; padding:20px;">
    <div style="max-width:600px; margin:auto; background:#1e293b; padding:20px; border-radius:10px;">
        <h3>PAINEL DE CONTROLE</h3>
        <input type="password" id="mestre" placeholder="Chave Mestre" style="padding:10px; width:90%"><br><br>
        <input type="text" id="nome" placeholder="Nome Cliente" style="padding:10px;">
        <input type="text" id="pin" placeholder="PIN 6 digitos" style="padding:10px;">
        <button onclick="salvar()" style="padding:10px; background:#22c55e; border:none; cursor:pointer;">CADASTRAR</button>
        <button onclick="listar()" style="padding:10px; background:#38bdf8; border:none; cursor:pointer;">LISTAR</button>
        <table style="width:100%; margin-top:20px; border:1px solid #334155;">
            <thead><tr><th>Nome</th><th>PIN</th></tr></thead>
            <tbody id="lista"></tbody>
        </table>
    </div>
    <script>
        async function salvar() {
            const res = await fetch('/admin/cadastrar', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    admin_key: document.getElementById('mestre').value,
                    nome: document.getElementById('nome').value,
                    pin: document.getElementById('pin').value
                })
            });
            const d = await res.json();
            alert(d.msg || d.erro);
            listar();
        }
        async function listar() {
            const m = document.getElementById('mestre').value;
            const res = await fetch('/admin/listar?key=' + m);
            const dados = await res.json();
            const lista = document.getElementById('lista');
            lista.innerHTML = "";
            if(dados.length === 0) { lista.innerHTML = "<tr><td colspan='2'>Vazio ou Chave Errada</td></tr>"; return; }
            dados.forEach(c => {
                lista.innerHTML += `<tr><td>\${c.nome}</td><td>\${c.pin}</td></tr>`;
            });
        }
    </script>
</body></html>
"""

# --- ROTAS CORRIGIDAS ---

@app.route('/')
def home(): return "<h1>KLEBMATRIX ONLINE</h1>"

@app.route('/painel-secreto-kleber')
def admin_page(): return render_template_string(HTML_ADMIN)

@app.route('/admin/cadastrar', methods=['POST'])
def cadastrar():
    d = request.json
    if d.get('admin_key') != ADMIN_KEY:
        return jsonify({"erro": "Chave Mestre Incorreta"}), 403
    
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO clientes (nome_empresa, pin_hash) VALUES (%s, %s)', 
                   (d.get('nome').strip(), d.get('pin').strip()))
        conn.commit()
        cur.close(); conn.close()
        return jsonify({"msg": "Sucesso Real! Gravado no Banco."})
    except Exception as e:
        if conn: conn.close()
        print(f"ERRO AO CADASTRAR NO BANCO: {e}")
        return jsonify({"erro": f"Erro de Banco: {str(e)}"}), 500

@app.route('/admin/listar')
def listar():
    if request.args.get('key') != ADMIN_KEY:
        return jsonify([])
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT nome_empresa, pin_hash FROM clientes')
        rows = cur.fetchall()
        cur.close(); conn.close()
        return jsonify([{"nome": r[0], "pin": r[1]} for r in rows])
    except Exception as e:
        print(f"ERRO AO LISTAR DO BANCO: {e}")
        return jsonify([])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))