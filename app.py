import os, secrets, string, psycopg2, datetime
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Busca as chaves do Render
ADMIN_KEY = os.environ.get('admin_key') or os.environ.get('ADMIN_KEY')

def get_db_connection():
    url = os.environ.get('DATABASE_URL')
    if url and url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    try:
        return psycopg2.connect(url, sslmode='require')
    except:
        return None

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
        :root { --blue: #38bdf8; --dark: #0b1120; --card: #1e293b; }
        body { background: var(--dark); color: white; font-family: sans-serif; margin: 0; padding: 20px; }
        .no-print { max-width: 900px; margin: auto; background: var(--card); padding: 25px; border-radius: 15px; border: 1px solid #334155; }
        input { padding: 12px; margin: 5px; background: #0f172a; border: 1px solid #334155; color: white; border-radius: 8px; }
        button { padding: 12px 20px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; color: white; margin: 5px; }
        .btn-green { background: #22c55e; } .btn-blue { background: #0284c7; } .btn-red { background: #ef4444; }
        
        .hist-item { background: #0f172a; padding: 15px; margin: 10px 0; border-radius: 8px; display: flex; align-items: center; border: 1px solid #334155; }
        .hist-item.selected { border-color: var(--blue); background: #1e293b; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #334155; padding: 12px; text-align: left; }

        /* --- MODELO DO CERTIFICADO --- */
        #print_area { display: none; }
        @media print {
            @page { size: landscape; margin: 0; }
            body { background: white !important; color: black !important; }
            .no-print { display: none !important; }
            #print_area { display: block !important; }
            .certificado { 
                page-break-after: always; height: 95vh; display: flex; justify-content: center; align-items: center; 
            }
            .moldura { 
                border: 12px solid black; width: 85%; padding: 60px; text-align: center; position: relative;
            }
            .titulo { font-size: 32px; font-weight: bold; margin-bottom: 40px; text-transform: uppercase; }
            .faixa { 
                background: #f8f9fa !important; border: 1px solid #ddd; padding: 20px; 
                font-family: monospace; font-size: 26px; font-weight: bold; margin: 20px 0; 
            }
            .footer { font-size: 14px; margin-top: 30px; }
        }
    </style>
</head>
<body>

    <div class="no-print">
        {% if tipo == 'admin' %}
            <h1>PAINEL MASTER</h1>
            <input type="password" id="mk" placeholder="Chave Admin">
            <button class="btn-blue" onclick="listar()">ATUALIZAR LISTA</button>
            <hr style="border: 0.5px solid #334155; margin: 20px 0;">
            <h3>CADASTRAR / +CREDITOS</h3>
            <input type="text" id="n" placeholder="Nome da Empresa">
            <input type="text" id="p" placeholder="PIN (6-8 digitos)" maxlength="8">
            <input type="number" id="l" placeholder="Total de Créditos">
            <button class="btn-green" onclick="add()">SALVAR ALTERAÇÕES</button>
            <div id="lista_admin"></div>
        {% else %}
            <div id="login_box">
                <h1>SISTEMA QUANTUM</h1>
                <input type="password" id="pin" placeholder="SEU PIN">
                <button class="btn-blue" onclick="entrar()">ACESSAR PAINEL</button>
            </div>
            <div id="dash" style="display:none;">
                <h2 id="c_nome" style="color:var(--blue)"></h2>
                <p>USO: <b id="uso"></b> / LIMITE: <b id="total"></b></p>
                <input type="text" id="obs" placeholder="OBSERVAÇÃO">
                <button class="btn-green" onclick="gerar()">GERAR CHAVE</button>
                <button class="btn-blue" onclick="imprimir()">🖨️ IMPRIMIR SELECIONADOS</button>
                <button style="background:#475569" onclick="exportar()">📊 EXPORTAR EXCEL</button>
                <br><br>
                <label><input type="checkbox" onclick="selTudo(this)"> Selecionar Todos</label>
                <div id="hist_list"></div>
            </div>
        {% endif %}
    </div>

    <div id="print_area"></div>

    <script>
    let pinAtivo = "";

    // --- FUNÇÕES ADMIN ---
    async function listar() {
        const k = document.getElementById('mk').value;
        const res = await fetch('/admin/listar?key=' + k);
        if(!res.ok) return alert("Chave Admin Incorreta");
        const dados = await res.json();
        let h = "<table><tr><th>Empresa</th><th>PIN</th><th>Uso/Limite</th><th>Ação</th></tr>";
        dados.forEach(c => {
            h += `<tr><td>${c.n}</td><td>${c.p}</td><td>${c.u}/${c.l}</td>
            <td><button class="btn-red" onclick="excluir('${c.p}')">Excluir</button></td></tr>`;
        });
        document.getElementById('lista_admin').innerHTML = h + "</table>";
    }

    async function add() {
        const k = document.getElementById('mk').value;
        const n = document.getElementById('n').value;
        const p = document.getElementById('p').value;
        const l = document.getElementById('l').value;
        if(!n || !p || !l) return alert("Preencha todos os campos");
        
        await fetch('/admin/cadastrar', {
            method:'POST', headers:{'Content-Type':'application/json'},
            body: JSON.stringify({key:k, n:n, p:p, l:l})
        });
        alert("Dados salvos!");
        listar();
    }

    async function excluir(p) {
        if(!confirm("Deseja realmente excluir este cliente?")) return;
        const k = document.getElementById('mk').value;
        await fetch('/admin/deletar', {
            method:'DELETE', headers:{'Content-Type':'application/json'},
            body: JSON.stringify({key:k, pin:p})
        });
        listar();
    }

    // --- FUNÇÕES CLIENTE ---
    async function entrar() {
        pinAtivo = document.getElementById('pin').value;
        const res = await fetch('/v1/cliente/dados?pin=' + pinAtivo);
        if(!res.ok) return alert("PIN Inválido!");
        const d = await res.json();
        document.getElementById('login_box').style.display='none';
        document.getElementById('dash').style.display='block';
        document.getElementById('c_nome').innerText = d.empresa;
        document.getElementById('uso').innerText = d.usadas;
        document.getElementById('total').innerText = d.limite;
        
        let h = "";
        d.hist.reverse().forEach((t, i) => {
            let chave = t.split(' | ')[2];
            h += `<div class="hist-item" id="r-${i}">
                <input type="checkbox" class="ck" data-key="${chave}" data-full="${t}" onchange="this.parentElement.classList.toggle('selected')">
                <span style="margin-left:15px">${t}</span>
            </div>`;
        });
        document.getElementById('hist_list').innerHTML = h;
    }

    async function gerar() {
        const res = await fetch('/v1/cliente/gerar', {
            method:'POST', headers:{'Content-Type':'application/json'},
            body: JSON.stringify({pin:pinAtivo, obs:document.getElementById('obs').value})
        });
        if(!res.ok) return alert("Erro: Verifique seu limite de créditos.");
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
        if(selecionados.length === 0) return alert("Selecione as chaves para imprimir!");
        let html = "";
        selecionados.forEach(item => {
            const chave = item.getAttribute('data-key');
            html += `<div class="certificado"><div class="moldura">
                <div class="titulo">Certificado de Autenticidade</div>
                <div class="faixa">${chave}</div>
                <div class="footer">Este certificado garante a originalidade do software Quantum 2026</div>
            </div></div>`;
        });
        document.getElementById('print_area').innerHTML = html;
        window.print();
    }

    function exportar() {
        let csv = "DATA;LOTE;CHAVE\\n";
        document.querySelectorAll('.ck:checked').forEach(c => {
            csv += c.getAttribute('data-full').replaceAll(" | ", ";") + "\\n";
        });
        const blob = new Blob([csv], {type:'text/csv'});
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = "chaves_quantum.csv";
        a.click();
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
    # Atualiza o limite se o PIN já existir (+Créditos)
    cur.execute('''INSERT INTO clientes (nome_empresa, pin_hash, limite) VALUES (%s, %s, %s)
                   ON CONFLICT (pin_hash) DO UPDATE SET limite = EXCLUDED.limite, nome_empresa = EXCLUDED.nome_empresa''', 
                (d['n'], d['p'], d['l']))
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
        reg = f"{datetime.datetime.now().strftime('%d/%m/%Y')} | {d.get('obs','GERAL').upper()} | {nk}"
        cur.execute("UPDATE clientes SET acessos=acessos+1, historico_chaves=array_append(historico_chaves, %s) WHERE pin_hash=%s", (reg, d['pin']))
        conn.commit(); cur.close(); conn.close()
        return "OK"
    return "Erro", 403

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))