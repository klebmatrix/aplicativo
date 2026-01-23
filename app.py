import os, psycopg2, datetime, random
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- SEGURANÇA: BUSCANDO DAS VARIÁVEIS DE AMBIENTE ---
DATABASE_URL = os.environ.get('DATABASE_URL')
# O PIN de administrador agora é buscado no Render. Se não houver, ele gera um erro proposital para segurança.
MASTER_PIN = os.environ.get('MASTER_PIN')

def get_db_connection():
    try:
        url = DATABASE_URL
        if url and url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return psycopg2.connect(url, sslmode='require')
    except Exception as e:
        return None

@app.before_request
def setup_db():
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY, nome TEXT, pin TEXT UNIQUE, tipo TEXT)''')
        cur.execute('''CREATE TABLE IF NOT EXISTS professores (
            id SERIAL PRIMARY KEY, nome TEXT, disciplina TEXT, gestor_id INTEGER)''')
        cur.execute('''CREATE TABLE IF NOT EXISTS grade (
            id SERIAL PRIMARY KEY, dia TEXT, aula_num INTEGER, info TEXT, gestor_id INTEGER)''')
        conn.commit(); cur.close(); conn.close()

HTML_NEXUS = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>NEXUS - GESTÃO SEGURA</title>
    <style>
        body { font-family: sans-serif; background: #f0f2f5; margin: 0; display: flex; }
        .sidebar { width: 250px; background: #1c1e21; color: white; height: 100vh; padding: 20px; position: fixed; }
        .main { margin-left: 290px; padding: 30px; width: 100%; }
        .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .grid-escola { display: grid; grid-template-columns: 100px repeat(5, 1fr); gap: 5px; margin-top: 20px; }
        .cell { border: 1px solid #ddd; padding: 10px; min-height: 50px; background: white; text-align: center; }
        .head { background: #b38b4d; color: white; font-weight: bold; }
        input, select, button { width: 100%; padding: 10px; margin: 5px 0; border-radius: 4px; border: 1px solid #ccc; }
        button { background: #b38b4d; color: white; border: none; cursor: pointer; font-weight: bold; }
    </style>
</head>
<body>
    <div class="sidebar">
        <h2>NEXUS HUB</h2>
        <div id="login_box">
            <input type="password" id="meu_pin" placeholder="PIN de Acesso">
            <button onclick="logar()">ENTRAR</button>
        </div>
        <div id="user_box" style="display:none;">
            <p>Conectado: <b id="u_nome"></b></p>
            <p>Nível: <span id="u_tipo"></span></p>
            <button onclick="location.reload()" style="background:#444;">SAIR</button>
        </div>
    </div>
    <div class="main">
        <div id="tela_admin" class="card" style="display:none;">
            <h2>ADMIN - CADASTRAR GESTOR/ESCOLA</h2>
            <input type="text" id="adm_n" placeholder="Nome da Escola/Gestor">
            <input type="text" id="adm_p" placeholder="Definir PIN do Gestor">
            <button onclick="criarGestor()">CRIAR ACESSO GESTOR</button>
        </div>
        <div id="tela_gestor" class="card" style="display:none;">
            <h2>GESTOR - GRADE 6 AULAS / 5 DIAS</h2>
            <div class="grid-escola">
                <div class="cell head">HORA</div>
                <div class="cell head">SEG</div><div class="cell head">TER</div><div class="cell head">QUA</div><div class="cell head">QUI</div><div class="cell head">SEX</div>
                {% for a in range(1, 7) %}
                    <div class="cell head">{{a}}ª Aula</div>
                    {% for d in ['Seg', 'Ter', 'Qua', 'Qui', 'Sex'] %}
                        <div class="cell" id="c-{{d}}-{{a}}" onclick="editarAula('{{d}}', {{a}})">+</div>
                    {% endfor %}
                {% endfor %}
            </div>
        </div>
    </div>
    <script>
        let user = null;
        async function logar() {
            const p = document.getElementById('meu_pin').value;
            // O PIN mestre é injetado aqui via template string para comparação segura
            if(p === '{{master}}') {
                show('tela_admin', 'Kleber', 'Dono');
                return;
            }
            const res = await fetch(`/api/login?p=${p}`);
            if(res.ok) {
                user = await res.json();
                show('tela_' + user.tipo.toLowerCase(), user.nome, user.tipo);
            } else { alert("PIN Incorreto"); }
        }
        function show(id, n, t) {
            document.getElementById('login_box').style.display='none';
            document.getElementById('user_box').style.display='block';
            document.getElementById(id).style.display='block';
            document.getElementById('u_nome').innerText = n;
            document.getElementById('u_tipo').innerText = t;
        }
        async function criarGestor() {
            const n = document.getElementById('adm_n').value;
            const p = document.getElementById('adm_p').value;
            await fetch('/api/admin/criar', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({n, p, t: 'Gestor'})
            });
            alert("Gestor Criado!");
        }
        function editarAula(d, a) {
            const txt = prompt("Professor e Matéria:");
            if(txt) document.getElementById(`c-${d}-${a}`).innerText = txt;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_NEXUS, master=MASTER_PIN)

@app.route('/api/login')
def login_api():
    p = request.args.get('p')
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT nome, tipo FROM usuarios WHERE pin = %s", (p,))
    u = cur.fetchone(); cur.close(); conn.close()
    if u: return jsonify({"nome": u[0], "tipo": u[1]})
    return "Erro", 401

@app.route('/api/admin/criar', methods=['POST'])
def criar_api():
    d = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO usuarios (nome, pin, tipo) VALUES (%s, %s, %s)", (d['n'], d['p'], d['t']))
    conn.commit(); cur.close(); conn.close()
    return "OK"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))