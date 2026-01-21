import os, secrets, string, psycopg2
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- CONFIGURAÇÕES DE AMBIENTE ---
def get_admin_key():
    return (os.environ.get('ADMIN_KEY') or '').strip()

def get_db_connection():
    url = os.environ.get('DATABASE_URL')
    if not url: return None
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return psycopg2.connect(url, sslmode='require')

# --- INTERFACE HTML UNIFICADA ---
HTML_SISTEMA = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SISTEMA QUANTUM | CERTIFICADOS</title>
    <style>
        :root { --blue: #38bdf8; --dark: #0b1120; --card: #1e293b; --red: #ef4444; --green: #22c55e; --gold: #fbbf24; }
        body { background: var(--dark); color: white; font-family: 'Segoe UI', sans-serif; padding: 20px; }
        .container { max-width: 1000px; margin: auto; background: var(--card); padding: 30px; border-radius: 20px; border: 1px solid #334155; }
        
        input, select { padding: 12px; background: #0f172a; border: 1px solid #334155; color: white; border-radius: 8px; outline: none; margin-bottom: 5px; }
        button { padding: 10px 15px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; color: white; transition: 0.2s; }
        
        /* Barra de Progresso e Estilos de Tela */
        .progress-container { background: #0f172a; border-radius: 10px; height: 12px; margin: 15px 0; border: 1px solid #334155; overflow: hidden; }
        .progress-bar { height: 100%; background: var(--blue); width: 0%; transition: 0.5s; }
        .infinite-bar { background: linear-gradient(90deg, var(--blue), var(--gold), var(--blue)); background-size: 200%; animation: move 2s linear infinite; width: 100% !important; }
        @keyframes move { 0% {background-position: 0%} 100% {background-position: 200%} }

        .hist-item { background: #0f172a; padding: 15px; margin-top: 10px; border-radius: 10px; display: flex; justify-content: space-between; align-items: center; cursor: pointer; border: 1px solid transparent; }
        .hist-item.selected { border-color: var(--gold); background: #1e3a8a; }
        .key-view { font-family: monospace; color: var(--blue); font-weight: bold; }

        /* --- ESTILO DO CERTIFICADO (PRINT) --- */
        .certificado { display: none; }

        @media print {
            .no-print, button, input, select, h1, h2, .progress-container, .hist-item, label { display: none !important; }
            body { background: white !important; color: black !important; padding: 0; }
            .container { border: none !important; background: white !important; width: 100%; max-width: 100%; }
            
            .certificado { 
                display: block !important;
                border: 15px double #1e293b;
                padding: 50px;
                margin-bottom: 100px;
                text-align: center;
                position: relative;
                page-break-inside: avoid;
                background: white;
            }
            .cert-header { font-size: 32px; font-weight: bold; border-bottom: 3px solid #1e293b; padding-bottom: 10px; margin-bottom: 20px; }
            .cert-body { font-size: 22px; line-height: 1.6; margin-bottom: 40px; }
            .cert-key { font-family: monospace; font-size: 28px; background: #eee; padding: 20px; border: 2px dashed #000; display: block; margin: 20px 0; }
            .cert-footer { font-size: 14px; margin-top: 50px; color: #555; }
            .selo { position: absolute; bottom: 40px; right: 50px; border: 5px solid #fbbf24; border-radius: 50%; width: 120px; height: 120px; display: flex; align-items: center; justify-content: center; transform: rotate(-15deg); color: #fbbf24; font-weight: bold; text-align: center; font-size: 14px; }
        }
    </style>
</head>
<body>
    <div class="container">
        {% if tipo == 'admin' %}
            <h1 style="color:var(--blue)">CENTRAL DE COMANDO</h1>
            <div class="no-print">
                <input type="password" id="mestre" placeholder="ADMIN_KEY">
                <button style="background:var(--blue)" onclick="listar()">CARREGAR CLIENTES</button>
            </div>
            <div id="lista_admin" style="margin-top:20px;"></div>

        {% else %}
            <div id="login_area">
                <h1 style="text-align:center">QUANTUM AUTH</h1>
                <input type="text" id="pin" placeholder="Digite seu PIN de 6 dígitos" maxlength="6" style="width:100%; text-align:center;">
                <button style="background:var(--blue); width:100%; margin-top:10px;" onclick="entrar()">ACESSAR PAINEL</button>
            </div>

            <div id="dashboard" style="display:none;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h2 id="emp_nome" style="color:var(--blue); margin:0;"></h2>
                    <button class="no-print" style="background:var(--gold); color:black" onclick="window.print()">🖨️ IMPRIMIR CERTIFICADOS</button>
                </div>
                
                <div class="progress-container"><div id="barra" class="progress-bar"></div></div>
                <p id="txt_status" style="font-size:12px; color:#94a3b8; text-align:right"></p>

                <div class="no-print" style="background:#16213e; padding:20px; border-radius:12px; margin:20px 0;">
                    <label>Lote/Obs:</label>
                    <input type="text" id="obs" placeholder="Ex: Venda Direta" style="width:40%">
                    <label>Qtd:</label>
                    <select id="qtd_m">
                        <option value="1">1x</option><option value="5">5x</option><option value="10">10x</option>
                    </select>
                    <button style="background:var(--green); width:20%" onclick="gerar()">GERAR</button>
                </div>

                <div id="lista_historico"></div>
            </div>
        {% endif %}
    </div>

    <script>
    // --- ADMIN ---
    async function listar() {
        const k = document.getElementById('mestre').value;
        const res = await fetch('/admin/listar?key=' + k);
        const dados = await res.json();
        let h = "<table><tr><th>Empresa / PIN</th><th>Tipo</th><th>Ações</th></tr>";
        dados.forEach(c => {
            const isSub = c.l === -1;
            h += `<tr><td>${c.n}<br><small>${c.p}</small></td>
                <td><span style="color:${isSub?'var(--gold)':'white'}">${isSub?'ASSINANTE':'CRÉDITOS: '+c.u+'/'+c.l}</span></td>
                <td>
                    <button style="background:var(--gold); color:black" onclick="setSub('${c.p}')">Assinatura</button>
                    <button style="background:var(--blue)" onclick="addCr('${c.p}')">+Cr</button>
                    <button style="background:var(--red)" onclick="del('${c.p}')">X</button>
                </td></tr>`;
        });
        document.getElementById('lista_admin').innerHTML = h + "</table>";
    }
    async function setSub(p) { await fetch('/admin/assinatura', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({key:document.getElementById('mestre').value, pin:p})}); listar(); }
    async function addCr(p) { const q=prompt("Qtd:"); if(q) await fetch('/admin/credito', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({key:document.getElementById('mestre').value, pin:p, qtd:q})}); listar(); }
    async function del(p) { if(confirm("Deletar?")) await fetch('/admin/deletar', {method:'DELETE', headers:{'Content-Type':'application/json'}, body:JSON.stringify({key:document.getElementById('mestre').value, pin:p})}); listar(); }

    // --- CLIENTE ---
    async function entrar() {
        const p = document.getElementById('pin').value;
        const res = await fetch('/v1/cliente/dados?pin=' + p);
        if(!res.ok) return alert("Acesso Negado!");
        const d = await res.json();
        
        document.getElementById('login_area').style.display='none';
        document.getElementById('dashboard').style.display='block';
        document.getElementById('emp_nome').innerText = d.empresa;
        
        const b = document.getElementById('barra');
        if(d.limite == -1) {
            b.classList.add('infinite-bar');
            document.getElementById('txt_status').innerText = "CONTA ASSINANTE - USO ILIMITADO";
        } else {
            b.style.width = (d.usadas / d.limite * 100) + "%";
            document.getElementById('txt_status').innerText = `CRÉDITOS: ${d.usadas} / ${d.limite}`;
        }

        renderizar(d.hist);
    }

    function renderizar(hist) {
        let h_tela = "";
        let h_cert = "";
        [...hist].reverse().forEach((t, i) => {
            const pt = t.split(' | ');
            h_tela += `
                <div class="hist-item" id="row-${i}" onclick="toggleCert(${i})">
                    <span><b>${pt[1]}</b></span>
                    <span class="key-view">${pt[2]}</span>
                </div>`;
            
            h_cert += `
                <div class="certificado" id="cert-${i}">
                    <div class="cert-header">CERTIFICADO DE AUTENTICIDADE</div>
                    <div class="cert-body">
                        Certificamos que a licença de uso para o módulo <b>${pt[1]}</b><br>
                        foi gerada com sucesso através do Sistema Quantum.<br><br>
                        CHAVE DE ACESSO:
                        <span class="cert-key">${pt[2]}</span>
                    </div>
                    <div class="cert-footer">Emissão: ${new Date().toLocaleDateString()} | Identificador: #Q${hist.length - i}</div>
                    <div class="selo">GARANTIA<br>QUANTUM<br>ORIGINAL</div>
                </div>`;
        });
        document.getElementById('lista_historico').innerHTML = h_tela + h_cert;
    }

    function toggleCert(i) {
        document.getElementById('row-'+i).classList.toggle('selected');
        const c = document.getElementById('cert-'+i);
        c.style.display = (c.style.display === 'block') ? 'none' : 'block';
    }

    async function gerar() {
        const p = document.getElementById('pin').value;
        const q = document.getElementById('qtd_m').value;
        const o = document.getElementById('obs').value || "GERAL";
        for(let i=0; i<q; i++) {
            await fetch('/v1/cliente/gerar', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({pin:p, obs:o})});
        }
        entrar();
    }
    </script>
</body>
</html>
"""

# --- ROTAS DE SERVIDOR (IDÊNTICAS ÀS ANTERIORES PARA FUNCIONAR COM O BANCO) ---
@app.route('/')
def home(): return render_template_string(HTML_SISTEMA)

@app.route('/painel-secreto-kleber')
def admin_page(): return render_template_string(HTML_SISTEMA, tipo='admin')

@app.route('/admin/listar')
def list_adm():
    if request.args.get('key', '').strip() != get_admin_key(): return jsonify([]), 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT nome_empresa, pin_hash, acessos, limite, ativo FROM clientes ORDER BY id DESC")
    r = cur.fetchall(); cur.close(); conn.close()
    return jsonify([{"n": x[0], "p": x[1], "u": x[2], "l": x[3], "a": x[4]} for x in r])

@app.route('/admin/assinatura', methods=['POST'])
def sub_adm():
    d = request.json
    if d.get('key', '').strip() != get_admin_key(): return jsonify({"e":403}), 403
    conn = get_db_connection(); cur = conn.cursor(); cur.execute("UPDATE clientes SET limite = -1 WHERE pin_hash = %s", (d['pin'],))
    conn.commit(); cur.close(); conn.close(); return jsonify({"ok": True})

@app.route('/admin/credito', methods=['POST'])
def cr_adm():
    d = request.json
    if d.get('key', '').strip() != get_admin_key(): return jsonify({"e":403}), 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("UPDATE clientes SET limite = CASE WHEN limite = -1 THEN %s ELSE limite + %s END WHERE pin_hash = %s", (int(d['qtd']), int(d['qtd']), d['pin']))
    conn.commit(); cur.close(); conn.close(); return jsonify({"ok": True})

@app.route('/admin/deletar', methods=['DELETE'])
def del_adm():
    d = request.json
    if d.get('key', '').strip() != get_admin_key(): return jsonify({"e":403}), 403
    conn = get_db_connection(); cur = conn.cursor(); cur.execute("DELETE FROM clientes WHERE pin_hash = %s", (d['pin'],))
    conn.commit(); cur.close(); conn.close(); return jsonify({"ok": True})

@app.route('/v1/cliente/dados')
def get_cli():
    pin = request.args.get('pin')
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT nome_empresa, acessos, limite, historico_chaves, ativo FROM clientes WHERE pin_hash = %s", (pin,))
    c = cur.fetchone(); cur.close(); conn.close()
    if c and c[4]: return jsonify({"empresa": c[0], "usadas": c[1], "limite": c[2], "hist": c[3]})
    return jsonify({"e": 401}), 401

@app.route('/v1/cliente/gerar', methods=['POST'])
def gen_key():
    d = request.json
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT acessos, limite, ativo FROM clientes WHERE pin_hash = %s", (d['pin'],))
    c = cur.fetchone()
    if c and c[2] and (c[1] == -1 or c[0] < c[1]):
        nk = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(25))
        reg = f"X | {d['obs'].upper()} | {nk}"
        cur.execute("UPDATE clientes SET acessos=acessos+1, historico_chaves=array_append(historico_chaves, %s) WHERE pin_hash=%s", (reg, d['pin']))
        conn.commit(); cur.close(); conn.close(); return jsonify({"ok": True})
    cur.close(); conn.close(); return jsonify({"e": 403}), 403

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))