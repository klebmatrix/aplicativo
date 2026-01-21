import os, secrets, string, psycopg2, datetime
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- BUSCA OBRIGATÓRIA NO RENDER ---
def get_admin_key():
    # Agora busca EXCLUSIVAMENTE da variável de ambiente do Render
    # Se não existir no Render, retorna None e bloqueia o acesso
    return os.environ.get('ADMIN_KEY')

def get_db_connection():
    url = os.environ.get('DATABASE_URL')
    if not url: return None
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    try:
        return psycopg2.connect(url, sslmode='require')
    except:
        return None

# --- BANCO DE DADOS ---
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
                historico_chaves TEXT[] DEFAULT '{}',
                ativo BOOLEAN DEFAULT TRUE
            );
        ''')
        conn.commit()
        cur.close(); conn.close()

# --- INTERFACE TELA BRANCA ---
HTML_SISTEMA = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SISTEMA QUANTUM</title>
    <style>
        body { background: white; color: black; font-family: sans-serif; padding: 20px; }
        .container { max-width: 900px; margin: auto; border: 1px solid #ddd; padding: 20px; border-radius: 10px; }
        input { padding: 12px; margin: 5px; border: 1px solid #ccc; border-radius: 5px; }
        button { padding: 10px 15px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; color: white; }
        .btn-black { background: black; color: white; width: 100%; margin-top: 10px; }
        .btn-blue { background: #2563eb; }
        .btn-red { background: #dc2626; }
        .btn-green { background: #16a34a; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; color: black; }
        th, td { border: 1px solid #ddd; padding: 10px; text-align: center; }
        th { background: #f4f4f4; }
        .hist-item { border: 1px solid #eee; padding: 10px; margin-top: 5px; display: flex; justify-content: space-between; align-items: center; cursor: pointer; }
        .selected { background: #f0f7ff; border-color: #2563eb; border-width: 2px; }
        @media print { .no-print { display: none !important; } .print-only { display: block !important; border: 2px solid black; padding: 40px; text-align: center; } }
        .print-only { display: none; }
    </style>
</head>
<body>
    <div class="container no-print">
        {% if tipo == 'admin' %}
            <h1>PAINEL ADMINISTRATIVO</h1>
            <p style="font-size: 0.8em; color: gray;">Chave buscada das Variáveis de Ambiente do Render</p>
            <input type="password" id="mestre" placeholder="Digite a ADMIN_KEY do Render">
            <button class="btn-blue" onclick="listar()">ACESSAR E ATUALIZAR</button>

            <div style="margin-top:20px; padding:15px; border: 1px solid #eee; border-radius: 8px;">
                <h3>Cadastrar Cliente</h3>
                <input type="text" id="n" placeholder="Nome da Empresa">
                <input type="text" id="p" placeholder="Senha (6-8 dig)" minlength="6" maxlength="8">
                <input type="number" id="l" placeholder="Créditos" value="100">
                <button class="btn-green" onclick="cadastrar()">SALVAR</button>
            </div>
            <div id="lista_admin"></div>
        {% else %}
            <div id="login_area">
                <h1>SISTEMA QUANTUM</h1>
                <input type="password" id="pin" placeholder="Senha do Cliente" maxlength="8" style="width:100%; box-sizing:border-box;">
                <button class="btn-black" onclick="entrar()">ENTRAR</button>
            </div>
            <div id="dashboard" style="display:none;">
                <h2 id="emp_nome"></h2>
                <p>Status Créditos: <b id="uso"></b> / <b id="total"></b></p>
                <div style="margin-bottom: 20px;">
                    <input type="text" id="obs" placeholder="Referência/Lote do Equipamento" style="width:60%">
                    <button class="btn-green" onclick="gerar()">GERAR NOVA CHAVE</button>
                </div>
                <div id="lista_historico"></div>
                <button class="btn-black" onclick="window.print()" style="margin-top:20px">🖨️ IMPRIMIR SELECIONADO</button>
            </div>
        {% endif %}
    </div>
    <div id="cert_print" class="print-only"></div>

    <script>
    async function listar() {
        const k = document.getElementById('mestre').value;
        const res = await fetch('/admin/listar?key=' + k);
        if(!res.ok) return alert("Chave de Ambiente Inválida!");
        const dados = await res.json();
        let h = "<table><tr><th>Empresa</th><th>Senha</th><th>Consumo</th><th>Ação</th></tr>";
        dados.forEach(c => {
            h += `<tr><td>${c.n}</td><td>${c.p}</td><td>${c.u}/${c.l}</td>
                <td><button class="btn-red" onclick="del('${c.p}')">Remover</button></td></tr>`;
        });
        document.getElementById('lista_admin').innerHTML = h + "</table>";
    }

    async function cadastrar() {
        const p = document.getElementById('p').value;
        if(p.length < 6 || p.length > 8) return alert("A senha deve ter entre 6 e 8 dígitos!");
        const k = document.getElementById('mestre').value;
        await fetch('/admin/cadastrar', {
            method:'POST', headers:{'Content-Type':'application/json'},
            body: JSON.stringify({key:k, n:document.getElementById('n').value, p:p, l:document.getElementById('l').value})
        });
        listar();
    }

    async function del(p) {
        if(confirm("Excluir definitivamente?")) {
            await fetch('/admin/deletar', {method:'DELETE', headers:{'Content-Type':'application/json'}, body:JSON.stringify({key:document.getElementById('mestre').value, pin:p})});
            listar();
        }
    }

    async function entrar() {
        const p = document.getElementById('pin').value;
        const res = await fetch('/v1/cliente/dados?pin=' + p);
        if(!res.ok) return alert("Acesso negado!");
        const d = await res.json();
        document.getElementById('login_area').style.display='none';
        document.getElementById('dashboard').style.display='block';
        document.getElementById('emp_nome').innerText = d.empresa;
        document.getElementById('uso').innerText = d.usadas;
        document.getElementById('total').innerText = d.limite;
        let h = "";
        d.hist.reverse().forEach((t, i) => {
            const pt = t.split(' | ');
            h += `<div class="hist-item" onclick="prepararPrint('${t}', this)">
                <span><b>${pt[1]}</b><br>${pt[2]}</span>
                <small>${pt[0]}</small>
            </div>`;
        });
        document.getElementById('lista_historico').innerHTML = h;
    }

    function prepararPrint(texto, el) {
        document.querySelectorAll('.hist-item').forEach(i => i.classList.remove('selected'));
        el.classList.add('selected');
        const pt = texto.split(' | ');
        document.getElementById('cert_print').innerHTML = `<h1>QUANTUM - CERTIFICADO</h1><br><h2>${pt[1]}</h2><br><p>CHAVE DE ATIVAÇÃO:</p><h3>${pt[2]}</h3><p>DATA: ${pt[0]}</p>`;
    }

    async function gerar() {
        const p = document.getElementById('pin').value;
        const o = document.getElementById('obs').value || "PADRAO";
        const res = await fetch('/v1/cliente/gerar', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({pin:p, obs:o})});
        if(res.ok) { entrar(); document.getElementById('obs').value = ""; } else { alert("Créditos insuficientes!"); }
    }
    </script>
</body>
</html>
"""

@app.route('/')
def home(): return render_template_string(HTML_SISTEMA, tipo='cliente')

@app.route('/painel-secreto-kleber')
def admin_page(): return render_template_string(HTML_SISTEMA, tipo='admin')

@app.route('/admin/listar')
def list_adm():
    key = get_admin_key()
    if not key or request.args.get('key') != key: return jsonify([]), 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT nome_empresa, pin_hash, acessos, limite FROM clientes")
    r = cur.fetchall(); cur.close(); conn.close()
    return jsonify([{"n": x[0], "p": x[1], "u": x[2], "l": x[3]} for x in r])

@app.route('/admin/cadastrar', methods=['POST'])
def add_adm():
    d = request.json
    key = get_admin_key()
    if not key or d.get('key') != key: return jsonify({"e":403}), 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("INSERT INTO clientes (nome_empresa, pin_hash, limite) VALUES (%s, %s, %s)", (d['n'], d['p'], d['l']))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"ok": True})

@app.route('/admin/deletar', methods=['DELETE'])
def del_adm():
    d = request.json
    key = get_admin_key()
    if not key or d.get('key') != key: return jsonify({"e":403}), 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("DELETE FROM clientes WHERE pin_hash = %s", (d['pin'],))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"ok": True})

@app.route('/v1/cliente/dados')
def get_cli():
    pin = request.args.get('pin')
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT nome_empresa, acessos, limite, historico_chaves FROM clientes WHERE pin_hash = %s AND ativo = TRUE", (pin,))
    c = cur.fetchone(); cur.close(); conn.close()
    if c: return jsonify({"empresa": c[0], "usadas": c[1], "limite": c[2], "hist": c[3]})
    return jsonify({"e": 401}), 401

@app.route('/v1/cliente/gerar', methods=['POST'])
def gen_key():
    d = request.json
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT acessos, limite FROM clientes WHERE pin_hash = %s AND ativo = TRUE", (d['pin'],))
    c = cur.fetchone()
    if c and c[0] < c[1]:
        nk = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(20))
        reg = f"{datetime.datetime.now().strftime('%d/%m/%Y')} | {d['obs'].upper()} | {nk}"
        cur.execute("UPDATE clientes SET acessos=acessos+1, historico_chaves=array_append(historico_chaves, %s) WHERE pin_hash=%s", (reg, d['pin']))
        conn.commit(); cur.close(); conn.close()
        return jsonify({"ok": True})
    cur.close(); conn.close(); return jsonify({"e": "Erro"}), 403

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))