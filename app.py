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

# --- HTML DA ÁREA DO CLIENTE ---
HTML_CLIENTE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>SISTEMA QUANTUM | CLIENTE</title>
    <style>
        body { background: white !important; color: #1a1a1a; font-family: sans-serif; padding: 20px; }
        .container { max-width: 800px; margin: auto; border: 1px solid #ddd; padding: 20px; border-radius: 10px; }
        input { padding: 12px; border: 1px solid #ccc; width: 100%; box-sizing: border-box; margin-bottom: 10px; }
        .btn { padding: 12px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; width: 100%; background: #000; color: #fff; }
        .hist-item { border: 1px solid #eee; padding: 15px; margin-top: 10px; display: flex; justify-content: space-between; align-items: center; }
        .certificado-a4 { display: none; }
        @media print {
            .no-print { display: none !important; }
            .certificado-a4.print-now { 
                display: flex !important; flex-direction: column; justify-content: center; align-items: center;
                width: 210mm; height: 297mm; border: 20px double #000 !important; text-align: center;
            }
        }
    </style>
</head>
<body>
    <div class="container no-print">
        <div id="login_area">
            <h1>ÁREA DO CLIENTE</h1>
            <input type="password" id="senha_cli" placeholder="PIN de 6 dígitos" maxlength="6">
            <button class="btn" onclick="entrar()">ENTRAR</button>
        </div>
        <div id="dashboard" style="display:none;">
            <h2 id="emp_nome"></h2>
            <input type="text" id="obs" placeholder="Nome do Produto">
            <button class="btn" onclick="gerar()" style="background:#2563eb; margin-top:10px;">REGISTRAR E GERAR CHAVE</button>
            <div id="lista_historico"></div>
        </div>
    </div>
    <div id="area_certificados"></div>
    <script>
    async function entrar() {
        const s = document.getElementById('senha_cli').value;
        const res = await fetch('/v1/cliente/dados?pin=' + s);
        if(!res.ok) return alert("PIN Inválido!");
        const d = await res.json();
        document.getElementById('login_area').style.display='none';
        document.getElementById('dashboard').style.display='block';
        document.getElementById('emp_nome').innerText = d.empresa;
        let h_t = ""; let h_c = "";
        [...d.hist].reverse().forEach((t, i) => {
            const pt = t.split(' | '); 
            h_t += `<div class="hist-item"><span><b>${pt[1]}</b><br>${pt[0]}</span><button class="btn" style="width:100px; background:#22c55e;" onclick="imprimir(${i})">IMPRIMIR</button></div>`;
            h_c += `<div class="certificado-a4" id="cert-${i}"><h1>CERTIFICADO</h1><p>ORIGINAL</p><div style="margin:50px 0;"><b>${pt[1]}</b><br>ID: ${pt[2]}</div><p>${pt[0]}</p></div>`;
        });
        document.getElementById('lista_historico').innerHTML = h_t;
        document.getElementById('area_certificados').innerHTML = h_c;
    }
    function imprimir(i) {
        document.querySelectorAll('.certificado-a4').forEach(c => c.classList.remove('print-now'));
        document.getElementById('cert-'+i).classList.add('print-now');
        window.print();
    }
    async function gerar() {
        const s = document.getElementById('senha_cli').value;
        await fetch('/v1/cliente/gerar', {
            method:'POST', headers:{'Content-Type':'application/json'}, 
            body:JSON.stringify({pin:s, obs:document.getElementById('obs').value || "PRODUTO"})
        });
        entrar();
    }
    </script>
</body>
</html>
"""

# --- HTML DA ÁREA DO ADMIN ---
HTML_ADMIN = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>SISTEMA QUANTUM | ADMIN</title>
    <style>
        body { background: white; font-family: sans-serif; padding: 20px; }
        .container { max-width: 600px; margin: auto; border: 1px solid #ddd; padding: 20px; }
        input { padding: 10px; width: 100%; margin-bottom: 10px; box-sizing: border-box; }
        .btn { padding: 10px; width: 100%; background: #e11d48; color: white; border: none; cursor: pointer; font-weight: bold; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
    </style>
</head>
<body>
    <div class="container">
        <h1>PAINEL ADMIN</h1>
        <div style="background: #f4f4f4; padding: 15px; border-radius: 5px;">
            <h3>Cadastrar Novo Cliente</h3>
            <input type="text" id="nome_emp" placeholder="Nome da Empresa">
            <input type="text" id="pin_emp" placeholder="PIN de 6 dígitos" maxlength="6">
            <button class="btn" onclick="cadastrar()">SALVAR CLIENTE</button>
        </div>
        <div id="lista_clientes"></div>
    </div>
    <script>
    async function carregar() {
        const res = await fetch('/v1/admin/clientes');
        const dados = await res.json();
        let html = "<table><tr><th>Empresa</th><th>PIN</th></tr>";
        dados.forEach(c => {
            html += `<tr><td>${c.empresa}</td><td>${c.pin}</td></tr>`;
        });
        document.getElementById('lista_clientes').innerHTML = html + "</table>";
    }
    async function cadastrar() {
        const emp = document.getElementById('nome_emp').value;
        const pin = document.getElementById('pin_emp').value;
        await fetch('/v1/admin/cadastrar', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({empresa: emp, pin: pin})
        });
        carregar();
    }
    carregar();
    </script>
</body>
</html>
"""

@app.route('/')
def index_cliente():
    return render_template_string(HTML_CLIENTE)

@app.route('/admin')
def index_admin():
    return render_template_string(HTML_ADMIN)

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