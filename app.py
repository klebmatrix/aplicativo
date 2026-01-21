import os, secrets, string, psycopg2, datetime
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- CONEXÃO COM O BANCO ---
def get_db_connection():
    url = os.environ.get('DATABASE_URL')
    if not url: return None
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    try:
        return psycopg2.connect(url, sslmode='require')
    except Exception as e:
        print(f"Erro Conexão: {e}")
        return None

# --- HTML UNIFICADO (CLIENTE E ADMIN) ---
HTML_BASE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SISTEMA QUANTUM</title>
    <style>
        body { background: white !important; color: #1a1a1a; font-family: sans-serif; margin: 0; padding: 20px; }
        .container { max-width: 600px; margin: auto; border: 1px solid #ddd; padding: 30px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
        h1 { text-align: center; color: #000; }
        input { padding: 12px; border: 1px solid #ccc; width: 100%; box-sizing: border-box; margin-bottom: 15px; border-radius: 6px; font-size: 16px; }
        .btn { padding: 14px; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; width: 100%; font-size: 16px; transition: 0.3s; }
        .btn-black { background: #000; color: #fff; }
        .btn-blue { background: #2563eb; color: #fff; margin-top: 10px; }
        .btn-red { background: #e11d48; color: #fff; }
        .card { border: 1px solid #eee; padding: 15px; margin-top: 10px; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; background: #fafafa; }
        
        /* ESTILO CERTIFICADO A4 */
        .certificado-a4 { display: none; }
        @media print {
            .no-print { display: none !important; }
            body { padding: 0; margin: 0; }
            .certificado-a4.print-now { 
                display: flex !important; flex-direction: column; justify-content: center; align-items: center;
                width: 210mm; height: 297mm; border: 20px double #000 !important; text-align: center; padding: 20mm; box-sizing: border-box;
            }
        }
    </style>
</head>
<body>
    <div class="container no-print">
        {% if tipo == 'admin' %}
            <h1>PAINEL ADMINISTRATIVO</h1>
            <div style="background: #f1f5f9; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                <label>Nova Empresa:</label>
                <input type="text" id="nome_emp" placeholder="Nome da Empresa">
                <label>PIN de 6 dígitos:</label>
                <input type="text" id="pin_emp" placeholder="Ex: 123456" maxlength="6">
                <button class="btn btn-red" onclick="cadastrarCliente()">CADASTRAR CLIENTE</button>
            </div>
            <h3>Empresas Cadastradas</h3>
            <div id="lista_clientes">Carregando...</div>

        {% else %}
            <div id="login_area">
                <h1>ÁREA DO CLIENTE</h1>
                <p style="text-align:center;">Digite seu PIN de 6 dígitos para acessar</p>
                <input type="password" id="senha_cli" placeholder="PIN de Acesso" maxlength="6">
                <button class="btn btn-black" onclick="loginCliente()">ENTRAR</button>
            </div>

            <div id="dashboard" style="display:none;">
                <h2 id="emp_nome" style="color: #2563eb; text-align:center;"></h2>
                <div style="background: #f8fafc; padding: 15px; border-radius: 8px; border: 1px solid #e2e8f0;">
                    <label>Registrar Produto:</label>
                    <input type="text" id="obs" placeholder="Nome do Equipamento / Software">
                    <button class="btn btn-blue" onclick="gerarChave()">GERAR REGISTRO AGORA</button>
                </div>
                <h3>Meus Certificados</h3>
                <div id="historico_cliente"></div>
            </div>
        {% endif %}
    </div>

    <div id="area_certificados"></div>

    <script>
    // --- FUNÇÕES ADMIN ---
    async function carregarClientes() {
        const res = await fetch('/v1/admin/clientes');
        const dados = await res.json();
        let h = "";
        dados.forEach(c => {
            h += `<div class="card"><span><b>${c.empresa}</b><br><small>PIN: ${c.pin}</small></span></div>`;
        });
        document.getElementById('lista_clientes').innerHTML = h;
    }

    async function cadastrarCliente() {
        const emp = document.getElementById('nome_emp').value;
        const pin = document.getElementById('pin_emp').value;
        if(!emp || !pin) return alert("Preencha tudo!");
        await fetch('/v1/admin/cadastrar', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({empresa: emp, pin: pin})
        });
        location.reload();
    }

    // --- FUNÇÕES CLIENTE ---
    async function loginCliente() {
        const pin = document.getElementById('senha_cli').value;
        const res = await fetch('/v1/cliente/dados?pin=' + pin);
        if(!res.ok) return alert("PIN incorreto ou não cadastrado!");
        const d = await res.json();
        
        document.getElementById('login_area').style.display='none';
        document.getElementById('dashboard').style.display='block';
        document.getElementById('emp_nome').innerText = d.empresa;
        
        let h_t = ""; let h_c = "";
        [...d.hist].reverse().forEach((t, i) => {
            const pt = t.split(' | '); 
            h_t += `<div class="card"><span><b>${pt[1]}</b><br>${pt[0]}</span><button class="btn" style="width:100px; background:#000; color:#fff; font-size:12px;" onclick="imprimir(${i})">IMPRIMIR</button></div>`;
            h_c += `<div class="certificado-a4" id="cert-${i}"><h1>CERTIFICADO QUANTUM</h1><hr><p>VALIDAÇÃO ORIGINAL</p><div style="margin:60px 0; font-size:24px;"><b>${pt[1]}</b><br><small>Chave: ${pt[2]}</small></div><p>Data: ${pt[0]}</p></div>`;
        });
        document.getElementById('historico_cliente').innerHTML = h_t;
        document.getElementById('area_certificados').innerHTML = h_c;
    }

    async function gerarChave() {
        const pin = document.getElementById('senha_cli').value;
        const obs = document.getElementById('obs').value || "GERAL";
        await fetch('/v1/cliente/gerar', {
            method:'POST', headers:{'Content-Type':'application/json'}, 
            body:JSON.stringify({pin:pin, obs:obs})
        });
        loginCliente();
    }

    function imprimir(i) {
        document.querySelectorAll('.certificado-a4').forEach(c => c.classList.remove('print-now'));
        document.getElementById('cert-'+i).classList.add('print-now');
        window.print();
    }

    if(document.getElementById('lista_clientes')) carregarClientes();
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_BASE, tipo='cliente')

@app.route('/admin')
def admin():
    return render_template_string(HTML_BASE, tipo='admin')

@app.route('/v1/cliente/dados')
def get_dados():
    pin = request.args.get('pin')
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT empresa, historico_chaves FROM clientes WHERE pin_hash = %s", (pin,))
    c = cur.fetchone()
    cur.close(); conn.close()
    if c: return jsonify({"empresa": c[0], "hist": c[1]})
    return jsonify({"e": 404}), 404

@app.route('/v1/cliente/gerar', methods=['POST'])
def gen_key():
    d = request.json
    conn = get_db_connection(); cur = conn.cursor()
    nk = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(20))
    dt = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
    reg = f"{dt} | {d['obs'].upper()} | {nk}"
    cur.execute("UPDATE clientes SET historico_chaves=array_append(historico_chaves, %s) WHERE pin_hash=%s", (reg, d['pin']))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"ok": True})

@app.route('/v1/admin/clientes')
def list_clientes():
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT empresa, pin_hash FROM clientes")
    rows = cur.fetchall()
    cur.close(); conn.close()
    return jsonify([{"empresa": r[0], "pin": r[1]} for r in rows])

@app.route('/v1/admin/cadastrar', methods=['POST'])
def add_cliente():
    d = request.json
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("INSERT INTO clientes (empresa, pin_hash, historico_chaves) VALUES (%s, %s, %s)", 
                (d['empresa'], d['pin'], []))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"ok": True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))