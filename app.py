import os, psycopg2, datetime, random
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Tenta pegar a URL do banco das variáveis de ambiente
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    try:
        url = DATABASE_URL
        if url and url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return psycopg2.connect(url, sslmode='require')
    except Exception as e:
        print(f"Erro na conexão com DB: {e}")
        return None

@app.before_request
def setup_db():
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            # Tabela Unificada de Usuários
            cur.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                id SERIAL PRIMARY KEY, nome TEXT, pin TEXT UNIQUE, tipo TEXT, status TEXT DEFAULT 'Ativo')''')
            # Tabelas Escolares
            cur.execute('''CREATE TABLE IF NOT EXISTS professores (
                id SERIAL PRIMARY KEY, nome TEXT, disciplina TEXT, gestor_id INTEGER)''')
            cur.execute('''CREATE TABLE IF NOT EXISTS grade (
                id SERIAL PRIMARY KEY, dia TEXT, aula_num INTEGER, turma TEXT, prof_id INTEGER, gestor_id INTEGER)''')
            # Tabela Quantum Seed (Mantendo compatibilidade)
            cur.execute('''CREATE TABLE IF NOT EXISTS clientes (
                id SERIAL PRIMARY KEY, nome_empresa TEXT, pin_hash TEXT UNIQUE, limite INTEGER DEFAULT 0, acessos INTEGER DEFAULT 0, status TEXT, historico_chaves TEXT[])''')
            conn.commit()
            cur.close()
        except Exception as e:
            print(f"Erro ao criar tabelas: {e}")
        finally:
            conn.close()

# --- HTML UNIFICADO (ADMIN, GESTOR, PROFESSOR) ---
HTML_INTERFACE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NEXUS HUB - GESTÃO</title>
    <style>
        :root { --primary: #1a1a1a; --gold: #b38b4d; --bg: #f5f5f5; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: var(--bg); margin: 0; display: flex; }
        
        .sidebar { width: 260px; background: var(--primary); color: white; height: 100vh; padding: 20px; position: fixed; }
        .main { margin-left: 300px; padding: 40px; width: 100%; }
        
        .card { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-bottom: 20px; }
        h1, h2 { color: var(--primary); border-left: 5px solid var(--gold); padding-left: 15px; }
        
        input, select { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 6px; }
        .btn { background: var(--gold); color: white; border: none; padding: 12px 25px; border-radius: 6px; cursor: pointer; font-weight: bold; width: 100%; }
        
        .grade-grid { display: grid; grid-template-columns: 80px repeat(5, 1fr); gap: 8px; margin-top: 20px; }
        .cell { background: white; border: 1px solid #eee; padding: 10px; border-radius: 4px; min-height: 60px; font-size: 12px; text-align: center; }
        .header-cell { background: var(--primary); color: white; font-weight: bold; }
    </style>
</head>
<body>
    <div class="sidebar">
        <h2>NEXUS HUB</h2>
        <hr border="0" style="border-top:1px solid #333;">
        <div id="login-section">
            <p>Acesse com seu PIN:</p>
            <input type="password" id="pin" placeholder="PIN de Acesso">
            <button class="btn" onclick="login()">ENTRAR NO SISTEMA</button>
        </div>
        <div id="user-display" style="display:none; margin-top:20px;">
            <p style="color:var(--gold);">CONECTADO COMO:</p>
            <b id="user-name"></b><br>
            <small id="user-type"></small>
            <button class="btn" style="margin-top:20px; background:#444;" onclick="location.reload()">SAIR</button>
        </div>
    </div>

    <div class="main">
        <div id="view-admin" class="card" style="display:none;">
            <h2>Painel Master (Kleber)</h2>
            <p>Cadastrar novo Gestor ou Terapeuta:</p>
            <input type="text" id="adm-nome" placeholder="Nome Completo">
            <input type="text" id="adm-pin" placeholder="Definir PIN (Mín 6 dig)">
            <select id="adm-tipo">
                <option value="Gestor">Gestor Escolar</option>
                <option value="Terapeuta">Terapeuta Quantum</option>
            </select>
            <button class="btn" onclick="cadastrarUsuario()">CRIAR ACESSO</button>
        </div>

        <div id="view-gestor" class="card" style="display:none;">
            <h2>Gestão Escolar - Grade Horária</h2>
            <div class="grade-grid">
                <div class="cell header-cell">AULA</div>
                <div class="cell header-cell">SEG</div><div class="cell header-cell">TER</div><div class="cell header-cell">QUA</div><div class="cell header-cell">QUI</div><div class="cell header-cell">SEX</div>
                
                {% for a in range(1, 7) %}
                <div class="cell header-cell" style="display:flex; align-items:center; justify-content:center;">{{a}}ª</div>
                {% for d in ['Seg', 'Ter', 'Qua', 'Qui', 'Sex'] %}
                <div class="cell" id="c-{{d}}-{{a}}" onclick="setAula('{{d}}', {{a}})">
                    <span style="color:#ccc;">+ Definir</span>
                </div>
                {% endfor %}
                {% endfor %}
            </div>
        </div>

        <div id="view-terapeuta" class="card" style="display:none;">
            <h2>Quantum Seed - Portal 528Hz</h2>
            <input type="text" id="q-intencao" placeholder="Intenção Cósmica">
            <button class="btn">MANIFESTAR SINTONIA</button>
        </div>
    </div>

    <script>
        let userData = null;

        async function login() {
            const pin = document.getElementById('pin').value;
            if(pin === 'KLEBER_ADMIN') {
                showView('view-admin', 'Kleber', 'Super Admin');
                return;
            }
            const res = await fetch(`/api/login?p=${pin}`);
            if(res.ok) {
                const data = await res.json();
                userData = data;
                showView('view-' + data.tipo.toLowerCase(), data.nome, data.tipo);
            } else {
                alert("PIN Inválido");
            }
        }

        function showView(viewId, name, type) {
            document.querySelectorAll('.main > div').forEach(d => d.style.display = 'none');
            document.getElementById(viewId).style.display = 'block';
            document.getElementById('login-section').style.display = 'none';
            document.getElementById('user-display').style.display = 'block';
            document.getElementById('user-name').innerText = name;
            document.getElementById('user-type').innerText = type;
        }

        async function cadastrarUsuario() {
            const n = document.getElementById('adm-nome').value;
            const p = document.getElementById('adm-pin').value;
            const t = document.getElementById('adm-tipo').value;
            const res = await fetch('/api/admin/add', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({n, p, t})
            });
            if(res.ok) { alert("Sucesso!"); document.getElementById('adm-nome').value=''; }
        }

        function setAula(d, a) {
            const info = prompt("Professor / Turma:");
            if(info) document.getElementById(`c-${d}-${a}`).innerText = info;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_INTERFACE)

@app.route('/api/login')
def login_api():
    p = request.args.get('p')
    conn = get_db_connection()
    if not conn: return "Erro de Banco", 500
    cur = conn.cursor()
    cur.execute("SELECT nome, tipo FROM usuarios WHERE pin = %s", (p,))
    u = cur.fetchone(); cur.close(); conn.close()
    if u: return jsonify({"nome": u[0], "tipo": u[1]})
    return "Não encontrado", 404

@app.route('/api/admin/add', methods=['POST'])
def add_user_api():
    d = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO usuarios (nome, pin, tipo) VALUES (%s, %s, %s)", (d['n'], d['p'], d['t']))
    conn.commit(); cur.close(); conn.close()
    return "OK"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))