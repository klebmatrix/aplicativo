import os, secrets, string, psycopg2, datetime
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

ADMIN_KEY = os.environ.get('admin_key') or os.environ.get('ADMIN_KEY')

def get_db_connection():
    url = os.environ.get('DATABASE_URL')
    if url and url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    try: return psycopg2.connect(url, sslmode='require')
    except: return None

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
                historico_chaves TEXT[] DEFAULT '{}'
            );
        ''')
        conn.commit(); cur.close(); conn.close()

HTML_SISTEMA = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>SISTEMA QUANTUM</title>
    <style>
        :root { --blue: #38bdf8; --dark: #0b1120; }
        body { background: var(--dark); color: white; font-family: sans-serif; margin: 0; padding: 20px; }
        .no-print { max-width: 900px; margin: auto; background: #1e293b; padding: 25px; border-radius: 15px; }
        input { padding: 10px; margin: 5px; background: #0f172a; border: 1px solid #334155; color: white; border-radius: 5px; }
        button { padding: 10px 15px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; color: white; margin: 5px; }
        .btn-green { background: #22c55e; } .btn-blue { background: #0284c7; } .btn-red { background: #ef4444; }
        
        /* Estilo da Lista no Navegador */
        .hist-item { background: #0f172a; padding: 15px; margin: 10px 0; border-radius: 8px; display: flex; align-items: center; border: 1px solid #334155; }
        .hist-item.selected { border-color: var(--blue); background: #1e293b; }

        /* --- MODELO DO CERTIFICADO (PARA IMPRESSÃO) --- */
        .certificado-container { display: none; } /* Esconde no navegador */

        @media print {
            @page { size: landscape; margin: 0; }
            body { background: white !important; padding: 0; margin: 0; }
            .no-print { display: none !important; }
            
            .certificado-container { 
                display: block !important;
                page-break-after: always;
                height: 90vh;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                padding: 40px;
            }

            .moldura {
                border: 10px solid black;
                width: 90%;
                height: 250px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                position: relative;
            }

            .cert-titulo {
                font-size: 24px;
                font-weight: bold;
                color: black;
                margin-bottom: 30px;
                text-transform: uppercase;
            }

            .cert-faixa {
                background: #f0f0f0 !important;
                width: 100%;
                padding: 15px 0;
                text-align: center;
                font-family: monospace;
                font-size: 22px;
                font-weight: bold;
                color: black;
                letter-spacing: 2px;
            }

            .cert-subtitulo {
                font-size: 14px;
                color: black;
                margin-top: 20px;
            }
        }
    </style>
</head>
<body>

    <div class="no-print">
        {% if tipo == 'admin' %}
            <h1>PAINEL MASTER</h1>
            <input type="password" id="mk" placeholder="Chave Admin">
            <button class="btn-blue" onclick="listar()">LISTAR</button>
            <hr>
            <input type="text" id="n" placeholder="Empresa">
            <input type="text" id="p" placeholder="PIN (6-8 dig)" maxlength="8">
            <input type="number" id="l" placeholder="Créditos">
            <button class="btn-green" onclick="add()">SALVAR</button>
            <div id="lista_admin"></div>
        {% else %}
            <div id="login_box">
                <h1>QUANTUM LOGIN</h1>
                <input type="password" id="pin" placeholder="Seu PIN" maxlength="8">
                <button class="btn-blue" onclick="entrar()">ENTRAR</button>
            </div>
            <div id="dash" style="display:none;">
                <h2 id="c_nome"></h2>
                <p>Status: <b id="uso"></b> / <b id="total"></b></p>
                <input type="text" id="obs" placeholder="Observação do Certificado">
                <button class="btn-green" onclick="gerar()">GERAR NOVA CHAVE</button>
                <button class="btn-blue" onclick="imprimir()">🖨️ IMPRIMIR CERTIFICADO (PDF)</button>
                <br><br>
                <label><input type="checkbox" onclick="selTudo(this)"> Selecionar Todos</label>
                <div id="hist_list"></div>
            </div>
        {% endif %}
    </div>

    <div id="print_area"></div>

    <script>
    let pinAtivo = "";

    async function entrar() {
        pinAtivo = document.getElementById('pin').value;
        const res = await fetch('/v1/cliente/dados?pin=' + pinAtivo);
        if(!res.ok) return alert("PIN Inválido");
        const d = await res.json();
        document.getElementById('login_box').style.display='none';
        document.getElementById('dash').style.display='block';
        document.getElementById('c_nome').innerText = d.empresa;
        document.getElementById('uso').innerText = d.usadas;
        document.getElementById('total').innerText = d.limite;
        
        let h = "";
        d.hist.reverse().forEach((t, i) => {
            let chaveOnly = t.split(' | ')[2];
            h += `<div class="hist-item" id="r-${i}">
                <input type="checkbox" class="ck" data-key="${chaveOnly}" onchange="this.parentElement.classList.toggle('selected')">
                <span style="margin-left:15px">${t}</span>
            </div>`;
        });
        document.getElementById('hist_list').innerHTML = h;
    }

    async function gerar() {
        await fetch('/v1/cliente/gerar', {
            method:'POST', headers:{'Content-Type':'application/json'},
            body: JSON.stringify({pin:pinAtivo, obs:document.getElementById('obs').value})
        });
        entrar();
    }

    function selTudo(src) {
        document.querySelectorAll('.ck').forEach(c => {
            c.checked = src.checked;
            c.parentElement.classList.toggle('selected', src.checked);
        });
    }

    function imprimir() {
        const selecionados = document.querySelectorAll('.ck:checked');
        if(selecionados.length === 0) return alert("Selecione ao menos uma chave!");

        let htmlFinal = "";
        selecionados.forEach(item => {
            const chave = item.getAttribute('data-key');
            htmlFinal += `
                <div class="certificado-container">
                    <div class="moldura">
                        <div class="cert-titulo">Certificado de Autenticidade</div>
                        <div class="cert-faixa">------- ${chave} .........</div>
                        <div class="cert-subtitulo">Assinatura Digital de 30 Caracteres</div>
                    </div>
                </div>
            `;
        });

        document.getElementById('print_area').innerHTML = htmlFinal;
        window.print();
    }

    // --- ADMIN ---
    async function listar() {
        const k = document.getElementById('mk').value;
        const res = await fetch('/admin/listar?key=' + k);
        const dados = await res.json();
        let h = "<table>";
        dados.forEach(c => {
            h += `<tr><td>${c.n}</td><td>${c.p}</td><td>${c.u}/${c.l}</td>
            <td><button class="btn-red" onclick="excluir('${c.p}')">Excluir</button></td></tr>`;
        });
        document.getElementById('lista_admin').innerHTML = h + "</table>";
    }

    async function add() {
        await fetch('/admin/cadastrar', {
            method:'POST', headers:{'Content-Type':'application/json'},
            body: JSON.stringify({key:document.getElementById('mk').value, n:document.getElementById('n').value, p:document.getElementById('p').value, l:document.getElementById('l').value})
        });
        listar();
    }

    async function excluir(p) {
        if(confirm("Excluir?")) {
            await fetch('/admin/deletar', {method:'DELETE', headers:{'Content-Type':'application/json'}, body:JSON.stringify({key:document.getElementById('mk').value, pin:p})});
            listar();
        }
    }
    </script>
</body>
</html>
"""

@app.route('/')
def home(): return render_template_string(HTML_SISTEMA, tipo='login')

@app.route('/painel-secreto-kleber')
def admin_page(): return render_template_string(HTML_SISTEMA, tipo='admin')

@app.route('/admin/listar')
def list_adm():
    if request.args.get('key') != ADMIN_KEY: return "Erro", 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT nome_empresa, pin_hash, acessos, limite FROM clientes ORDER BY id DESC")
    r = cur.fetchall(); cur.close(); conn.close()
    return jsonify([{"n": x[0], "p": x[1], "u": x[2], "l": x[3]} for x in r])

@app.route('/admin/cadastrar', methods=['POST'])
def add_adm():
    d = request.json
    if d.get('key') != ADMIN_KEY: return "Erro", 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute('''INSERT INTO clientes (nome_empresa, pin_hash, limite) VALUES (%s, %s, %s)
                   ON CONFLICT (pin_hash) DO UPDATE SET limite = EXCLUDED.limite''', (d['n'], d['p'], d['l']))
    conn.commit(); cur.close(); conn.close()
    return "OK"

@app.route('/admin/deletar', methods=['DELETE'])
def del_adm():
    d = request.json
    if d.get('key') != ADMIN_KEY: return "Erro", 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("DELETE FROM clientes WHERE pin_hash = %s", (d['pin'],))
    conn.commit(); cur.close(); conn.close()
    return "OK"

@app.route('/v1/cliente/dados')
def get_cli():
    pin = request.args.get('pin')
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT nome_empresa, acessos, limite, historico_chaves FROM clientes WHERE pin_hash = %s", (pin,))
    c = cur.fetchone(); cur.close(); conn.close()
    if c: return jsonify({"empresa": c[0], "usadas": c[1], "limite": c[2], "hist": c[3]})
    return "Erro", 401

@app.route('/v1/cliente/gerar', methods=['POST'])
def gen_key():
    d = request.json
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT acessos, limite FROM clientes WHERE pin_hash = %s", (d['pin'],))
    c = cur.fetchone()
    if c and c[0] < c[1]:
        nk = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(30))
        reg = f"{datetime.datetime.now().strftime('%d/%m/%Y')} | {d.get('obs','').upper()} | {nk}"
        cur.execute("UPDATE clientes SET acessos=acessos+1, historico_chaves=array_append(historico_chaves, %s) WHERE pin_hash=%s", (reg, d['pin']))
        conn.commit(); cur.close(); conn.close()
        return "OK"
    return "Erro", 403

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))