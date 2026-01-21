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
    return psycopg2.connect(url, sslmode='require')

# O erro estava aqui: certifique-se de que o bloco termina com aspas triplas no final
HTML_SISTEMA = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SISTEMA QUANTUM | REGISTRO</title>
    <style>
        body { background-color: #ffffff !important; color: #1a1a1a !important; font-family: sans-serif; margin: 0; padding: 20px; }
        .container { max-width: 800px; margin: auto; background: #ffffff; padding: 30px; border-radius: 10px; border: 1px solid #ddd; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
        input { padding: 12px; border: 1px solid #ccc; border-radius: 6px; width: 100%; box-sizing: border-box; margin-bottom: 15px; background: white !important; color: black !important; }
        .btn { padding: 12px; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; width: 100%; transition: 0.2s; }
        .btn-azul { background: #000; color: white; }
        .hist-item { border: 1px solid #eee; padding: 15px; margin-top: 10px; display: flex; justify-content: space-between; align-items: center; background: #fdfdfd; }
        
        .certificado-a4 { display: none; }

        @media print {
            @page { size: A4; margin: 0; }
            .no-print { display: none !important; }
            body { background: white !important; }
            .certificado-a4.print-now { 
                display: flex !important; flex-direction: column; justify-content: center; align-items: center;
                width: 210mm; height: 297mm; border: 20px double #000 !important; padding: 30mm; box-sizing: border-box; text-align: center;
            }
        }
    </style>
</head>
<body>
    <div class="container no-print">
        <div id="login_area">
            <h1>LOGIN CLIENTE</h1>
            <input type="password" id="senha_cli" placeholder="Digite sua senha de 6 dígitos" maxlength="6">
            <button class="btn btn-azul" onclick="entrar()">ENTRAR</button>
        </div>
        <div id="dashboard" style="display:none;">
            <h2 id="emp_nome"></h2>
            <div style="background:#f9f9f9; padding:15px; border-radius:8px;">
                <input type="text" id="obs" placeholder="Nome do Produto" style="margin:0;">
                <button class="btn btn-azul" style="margin-top:10px;" onclick="gerar()">GERAR REGISTRO</button>
            </div>
            <h3>Histórico</h3>
            <div id="lista_historico"></div>
        </div>
    </div>
    <div id="area_certificados"></div>

    <script>
    async function entrar() {
        const s = document.getElementById('senha_cli').value;
        const res = await fetch('/v1/cliente/dados?pin=' + s);
        if(!res.ok) return alert("Erro de acesso!");
        const d = await res.json();
        document.getElementById('login_area').style.display='none';
        document.getElementById('dashboard').style.display='block';
        document.getElementById('emp_nome').innerText = d.empresa;
        
        let h_tela = ""; let h_cert = "";
        [...d.hist].reverse().forEach((t, i) => {
            const pt = t.split(' | '); 
            h_tela += `<div class="hist-item"><span><b>${pt[1]}</b><br>${pt[0]}</span><button class="btn" style="width:100px; background:#22c55e; color:white;" onclick="imprimir(${i})">IMPRIMIR</button></div>`;
            h_cert += `<div class="certificado-a4" id="cert-${i}"><h1>CERTIFICADO</h1><p>AUTENTICIDADE ORIGINAL</p><hr><div style="margin:40px 0;">Produto: <b>${pt[1]}</b><br>Código: <b>${pt[2]}</b></div><p>Data: ${pt[0]}</p></div>`;
        });
        document.getElementById('lista_historico').innerHTML = h_tela;
        document.getElementById('area_certificados').innerHTML = h_cert;
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

@app.route('/')
def index():
    return render_template_string(HTML_SISTEMA, tipo='cliente')

@app.route('/v1/cliente/dados')
def get_dados():
    pin = request.args.get('pin')
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT empresa, historico_chaves FROM clientes WHERE pin_hash = %s", (pin,))
    c = cur.fetchone()
    cur.close(); conn.close()
    if c: return jsonify({"empresa": c[0], "hist": c[1]})
    return jsonify({"e": 404}), 404

@app.route('/v1/cliente/gerar', methods=['POST'])
def gen_key():
    d = request.json
    conn = get_db_connection(); cur = conn.cursor()
    nk = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(25))
    data_atual = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
    reg = f"{data_atual} | {d['obs'].upper()} | {nk}"
    cur.execute("UPDATE clientes SET acessos=acessos+1, historico_chaves=array_append(historico_chaves, %s) WHERE pin_hash=%s", (reg, d['pin']))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"ok": True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))