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

@app.before_request
def create_tables():
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
    <title>SISTEMA QUANTUM</title>
    <style>
        /* TELA BRANCA TOTAL */
        html, body { background-color: #ffffff !important; color: #1a1a1a !important; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        
        .container { max-width: 500px; margin: 50px auto; padding: 30px; background-color: #ffffff !important; border: 1px solid #eeeeee; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); }
        
        h2, h3 { color: #000000; text-align: center; margin-bottom: 25px; font-weight: 600; }
        
        input { width: 100%; padding: 14px; margin: 10px 0; box-sizing: border-box; border: 1px solid #dddddd; border-radius: 8px; background-color: #ffffff !important; font-size: 16px; outline: none; }
        input:focus { border-color: #000000; }
        
        .btn { width: 100%; padding: 14px; cursor: pointer; font-weight: bold; border: none; border-radius: 8px; font-size: 16px; transition: all 0.3s ease; margin-top: 10px; }
        .btn-black { background-color: #000000; color: #ffffff; }
        .btn-black:hover { opacity: 0.8; }
        .btn-blue { background-color: #2563eb; color: #ffffff; }
        
        .card { border-bottom: 1px solid #f0f0f0; padding: 15px 0; display: flex; justify-content: space-between; align-items: center; }
        .card:last-child { border-bottom: none; }
        .card span { font-size: 14px; color: #444; line-height: 1.4; }
        .card b { color: #000; font-size: 15px; }
        
        .btn-ver { background: #f4f4f5; color: #000; padding: 6px 12px; border-radius: 4px; font-size: 12px; border: 1px solid #e4e4e7; width: auto; margin: 0; }

        /* AREA DE IMPRESSÃO */
        .print-area { display: none; background: white !important; }
        @media print { 
            .no-print { display: none !important; } 
            .print-area { 
                display: flex !important; flex-direction: column; justify-content: center; align-items: center;
                width: 210mm; height: 297mm; border: 15px double #000; padding: 40px; box-sizing: border-box; text-align: center; 
            } 
        }
    </style>
</head>
<body>
    <div class="container no-print">
        {% if admin %}
            <h2>PAINEL ADMIN</h2>
            <input type="text" id="n" placeholder="Nome da Empresa">
            <input type="text" id="p" placeholder="PIN de 6 dígitos" maxlength="6">
            <button class="btn btn-black" onclick="cadastrar()">CADASTRAR CLIENTE</button>
            <p style="text-align:center; font-size:12px; color: #999; margin-top:20px;">Área Restrita</p>
        {% else %}
            <div id="login">
                <h2>SISTEMA QUANTUM</h2>
                <input type="password" id="pin" placeholder="PIN de Acesso" maxlength="6">
                <button class="btn btn-black" onclick="entrar()">ACESSAR</button>
            </div>
            <div id="dash" style="display:none;">
                <h3 id="nome_e"></h3>
                <div style="margin-bottom: 30px;">
                    <input type="text" id="prod" placeholder="Nome do Equipamento">
                    <button class="btn btn-blue" onclick="gerar()">GERAR NOVO REGISTRO</button>
                </div>
                <div id="lista"></div>
            </div>
        {% endif %}
    </div>
    
    <div id="cert" class="print-area"></div>

    <script>
    async function cadastrar() {
        const n = document.getElementById('n').value;
        const p = document.getElementById('p').value;
        if(!n || !p) return alert("Preencha os campos!");
        const res = await fetch('/v1/admin/cadastrar', {
            method:'POST', headers:{'Content-Type':'application/json'},
            body: JSON.stringify({empresa: n, pin: p})
        });
        if(res.ok) {
            alert("Cliente cadastrado com sucesso!");
            document.getElementById('n').value = "";
            document.getElementById('p').value = "";
        } else {
            alert("Erro ao salvar. Verifique o banco.");
        }
    }

    async function entrar() {
        const pin = document.getElementById('pin').value;
        if(!pin) return;
        const res = await fetch('/v1/cliente/dados?pin=' + pin);
        if(!res.ok) return alert("PIN incorreto ou inexistente.");
        const d = await res.json();
        document.getElementById('login').style.display='none';
        document.getElementById('dash').style.display='block';
        document.getElementById('nome_e').innerText = d.empresa;
        
        let h = "";
        [...d.hist].reverse().forEach(t => {
            const p = t.split(' | ');
            h += `<div class="card"><span>${p[0]}<br><b>${p[1]}</b></span><button class="btn btn-ver" onclick="imprimir('${t}')">VER CERTIFICADO</button></div>`;
        });
        document.getElementById('lista').innerHTML = h;
    }

    async function gerar() {
        const pin = document.getElementById('pin').value;
        const prod = document.getElementById('prod').value;
        if(!prod) return alert("Informe o nome do produto.");
        const res = await fetch('/v1/cliente/gerar', {
            method:'POST', headers:{'Content-Type':'application/json'},
            body: JSON.stringify({pin: pin, obs: prod})
        });
        if(res.ok) {
            document.getElementById('prod').value = "";
            entrar();
        }
    }

    function imprimir(texto) {
        const p = texto.split(' | ');
        document.getElementById('cert').innerHTML = `
            <div style="border: 2px solid #000; padding: 20px; width: 100%;">
                <h1 style="font-size: 45px; margin-bottom: 10px;">CERTIFICADO</h1>
                <p style="font-size: 18px; letter-spacing: 4px;">AUTENTICIDADE E GARANTIA</p>
                <div style="margin: 80px 0;">
                    <p style="font-size: 20px;">PRODUTO / SOFTWARE:</p>
                    <h2 style="font-size: 35px; text-transform: uppercase;">${p[1]}</h2>
                    <br>
                    <p style="font-size: 18px;">CHAVE DE SEGURANÇA:</p>
                    <h3 style="font-family: monospace; font-size: 24px;">${p[2]}</h3>
                </div>
                <p style="font-size: 16px;">Data do Registro: ${p[0]}</p>
                <div style="margin-top: 50px; border-top: 1px solid #000; width: 250px; display: inline-block; padding-top: 10px;">
                    Assinatura Digital Quantum
                </div>
            </div>
        `;
        window.print();
    }
    </script>
</body>
</html>
"""

@app.route('/')
def home(): return render_template_string(HTML_SISTEMA, admin=False)

@app.route('/admin')
def admin_pg(): return render_template_string(HTML_SISTEMA, admin=True)

@app.route('/v1/cliente/dados')
def dados():
    pin = request.args.get('pin')
    conn = get_db_connection()
    if not conn: return jsonify({"e": "db"}), 500
    cur = conn.cursor()
    cur.execute("SELECT empresa, historico_chaves FROM clientes WHERE pin_hash = %s", (pin,))
    res = cur.fetchone()
    cur.close(); conn.close()
    if res: return jsonify({"empresa": res[0], "hist": res[1]})
    return jsonify({}), 404

@app.route('/v1/cliente/gerar', methods=['POST'])
def gerar_api():
    d = request.json
    conn = get_db_connection(); cur = conn.cursor()
    ch = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(14))
    info = f"{datetime.datetime.now().strftime('%d/%m/%Y %H:%M')} | {d['obs'].upper()} | {ch}"
    cur.execute("UPDATE clientes SET historico_chaves = array_append(historico_chaves, %s) WHERE pin_hash = %s", (info, d['pin']))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"ok": True})

@app.route('/v1/admin/cadastrar', methods=['POST'])
def add_api():
    d = request.json
    conn = get_db_connection(); cur = conn.cursor()
    try:
        cur.execute("INSERT INTO clientes (empresa, pin_hash, historico_chaves) VALUES (%s, %s, %s)", (d['empresa'], d['pin'], []))
        conn.commit()
        return jsonify({"ok": True})
    except:
        return jsonify({"ok": False}), 400
    finally:
        cur.close(); conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))