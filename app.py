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

# Criação automática da tabela caso não exista
@app.before_request
def init_db():
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
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
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QUANTUM AUTH</title>
    <style>
        /* TELA BRANCA TOTAL */
        :root { --blue: #2563eb; --border: #e2e8f0; --bg: #ffffff; --text: #1e293b; }
        
        body { background: var(--bg) !important; color: var(--text) !important; font-family: 'Segoe UI', system-ui, sans-serif; margin: 0; padding: 20px; }
        
        .container { max-width: 600px; margin: 40px auto; background: #fff; padding: 30px; border-radius: 12px; border: 1px solid var(--border); box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
        
        h1, h2 { text-align: center; color: #000; margin-bottom: 20px; }
        
        input { width: 100%; padding: 12px; margin-bottom: 15px; border: 1px solid var(--border); border-radius: 8px; box-sizing: border-box; font-size: 16px; background: #fff; color: #000; }
        
        .btn { padding: 12px 20px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; width: 100%; transition: 0.2s; font-size: 16px; }
        .btn-black { background: #000; color: #fff; }
        .btn-blue { background: var(--blue); color: #fff; }
        .btn-outline { background: #fff; color: #000; border: 1px solid var(--border); margin-top: 10px; }

        /* LISTA DE REGISTROS */
        .hist-item { border-bottom: 1px solid var(--border); padding: 15px 0; display: flex; justify-content: space-between; align-items: center; }
        .hist-item b { display: block; color: #000; }
        .hist-item small { color: #64748b; }

        /* CERTIFICADO A4 */
        .certificado-a4 { display: none; }

        @media print {
            .no-print { display: none !important; }
            body { background: white !important; margin: 0; padding: 0; }
            .certificado-a4.print-now { 
                display: flex !important; flex-direction: column; justify-content: center; align-items: center;
                width: 210mm; height: 297mm; border: 20px double #000; padding: 40mm; box-sizing: border-box; text-align: center; 
            }
            .cert-title { font-size: 50px; font-weight: bold; text-transform: uppercase; border-bottom: 5px solid #000; margin-bottom: 10px; }
            .cert-body { font-size: 22px; margin: 60px 0; line-height: 1.6; }
            .auth-box { border: 2px solid #000; padding: 20px; font-family: monospace; font-size: 28px; font-weight: bold; letter-spacing: 3px; }
        }
    </style>
</head>
<body>
    <div class="container no-print">
        {% if tipo == 'admin' %}
            <h2>PAINEL ADMINISTRATIVO</h2>
            <div id="form-admin">
                <input type="text" id="adm_nome" placeholder="Nome da Empresa">
                <input type="text" id="adm_pin" placeholder="PIN de Acesso (6 dígitos)" maxlength="6">
                <button class="btn btn-black" onclick="cadastrar()">CADASTRAR NOVO CLIENTE</button>
            </div>
            <div id="lista_admin" style="margin-top:30px;"></div>

        {% else %}
            <div id="login_area">
                <h1>QUANTUM AUTH</h1>
                <p style="text-align:center; color:#64748b;">Acesse com seu PIN</p>
                <input type="password" id="pin_cli" placeholder="PIN de 6 dígitos" maxlength="6" style="text-align:center; font-size:24px;">
                <button class="btn btn-black" onclick="entrar()">ENTRAR NO SISTEMA</button>
            </div>

            <div id="dashboard" style="display:none;">
                <h2 id="emp_nome" style="color:var(--blue)"></h2>
                <div style="background:#f8fafc; padding:20px; border-radius:10px; border:1px solid var(--border);">
                    <input type="text" id="obs" placeholder="Nome do Produto / Lote">
                    <button class="btn btn-blue" onclick="gerar()">GERAR NOVO CERTIFICADO</button>
                </div>
                <div id="lista_historico"></div>
            </div>
        {% endif %}
    </div>

    <div id="area_certificados"></div>

    <script>
    async function entrar() {
        const p = document.getElementById('pin_cli').value;
        const res = await fetch('/v1/cliente/dados?pin=' + p);
        if(!res.ok) return alert("PIN Inválido!");
        const d = await res.json();
        
        document.getElementById('login_area').style.display='none';
        document.getElementById('dashboard').style.display='block';
        document.getElementById('emp_nome').innerText = d.empresa;
        
        let h_t = ""; let h_c = "";
        [...d.hist].reverse().forEach((t, i) => {
            const pt = t.split(' | ');
            h_t += `<div class="hist-item">
                        <span><b>${pt[1]}</b><small>${pt[0]}</small></span>
                        <button class="btn btn-outline" style="width:100px; margin:0;" onclick="imprimir(${i})">IMPRIMIR</button>
                    </div>`;
            h_c += `<div class="certificado-a4" id="cert-${i}">
                        <div class="cert-title">Certificado</div>
                        <div style="letter-spacing:8px; margin-bottom:40px;">AUTENTICIDADE QUANTUM</div>
                        <div class="cert-body">
                            Certificamos que o produto/software<br>
                            <strong style="font-size:30px;">${pt[1]}</strong><br>
                            foi devidamente registrado e autenticado em nossa base.
                        </div>
                        <div class="auth-box">${pt[2]}</div>
                        <div style="margin-top:40px;">Data: ${pt[0]}</div>
                    </div>`;
        });
        document.getElementById('lista_historico').innerHTML = h_t;
        document.getElementById('area_certificados').innerHTML = h_c;
    }

    async function gerar() {
        const p = document.getElementById('pin_cli').value;
        const o = document.getElementById('obs').value || "PRODUTO";
        await fetch('/v1/cliente/gerar', {
            method:'POST', headers:{'Content-Type':'application/json'},
            body:JSON.stringify({pin:p, obs:o})
        });
        entrar();
    }

    function imprimir(i) {
        document.querySelectorAll('.certificado-a4').forEach(c => c.classList.remove('print-now'));
        document.getElementById('cert-'+i).classList.add('print-now');
        window.print();
    }

    async function cadastrar() {
        const n = document.getElementById('adm_nome').value;
        const p = document.getElementById('adm_pin').value;
        const res = await fetch('/admin/cadastrar', {
            method:'POST', headers:{'Content-Type':'application/json'},
            body:JSON.stringify({empresa:n, pin:p})
        });
        if(res.ok) { alert("Cadastrado!"); location.reload(); }
    }
    </script>
</body>
</html>
"""

@app.route('/')
def index(): return render_template_string(HTML_SISTEMA, tipo='cliente')

@app.route('/admin')
def admin(): return render_template_string(HTML_SISTEMA, tipo='admin')

@app.route('/v1/cliente/dados')
def get_dados():
    pin = request.args.get('pin')
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT empresa, historico_chaves FROM clientes WHERE pin_hash = %s", (pin,))
    res = cur.fetchone()
    cur.close(); conn.close()
    if res: return jsonify({"empresa": res[0], "hist": res[1]})
    return jsonify({}), 404

@app.route('/v1/cliente/gerar', methods=['POST'])
def gen():
    d = request.json
    conn = get_db_connection(); cur = conn.cursor()
    ch = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(16))
    dt = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
    cur.execute("UPDATE clientes SET historico_chaves = array_append(historico_chaves, %s) WHERE pin_hash = %s", 
                (f"{dt} | {d['obs'].upper()} | {ch}", d['pin']))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"ok": True})

@app.route('/admin/cadastrar', methods=['POST'])
def add():
    d = request.json
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("INSERT INTO clientes (empresa, pin_hash, historico_chaves) VALUES (%s, %s, %s)", 
                (d['empresa'], d['pin'], []))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"ok": True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))