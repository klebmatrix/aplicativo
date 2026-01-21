import os, secrets, string, psycopg2
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def get_admin_key():
    return (os.environ.get('ADMIN_KEY') or '').strip()

def get_db_connection():
    url = os.environ.get('DATABASE_URL')
    if not url: return None
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return psycopg2.connect(url, sslmode='require')

HTML_SISTEMA = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QUANTUM UTILITIES</title>
    <style>
        :root { --blue: #38bdf8; --dark: #0b1120; --card: #1e293b; --red: #ef4444; --green: #22c55e; --neon: 0 0 15px rgba(56, 189, 248, 0.4); }
        body { background: var(--dark); color: white; font-family: 'Segoe UI', sans-serif; padding: 20px; }
        .container { max-width: 1000px; margin: auto; background: var(--card); padding: 30px; border-radius: 20px; border: 1px solid #334155; }
        
        input, select { padding: 12px; background: #0f172a; border: 1px solid #334155; color: white; border-radius: 8px; outline: none; }
        button { padding: 12px 18px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; color: white; transition: 0.2s; }
        button:active { transform: scale(0.95); }

        /* Barra Neon */
        .progress-container { background: #0f172a; border-radius: 10px; height: 10px; width: 100%; margin: 10px 0; border: 1px solid #334155; }
        .progress-bar { height: 100%; background: var(--blue); box-shadow: var(--neon); transition: 0.5s; width: 0%; }

        /* Cards de Chaves */
        .hist-item { background: #0f172a; padding: 15px; margin-top: 8px; border-radius: 10px; display: flex; align-items: center; border: 1px solid transparent; }
        .hist-item:hover { border-color: var(--blue); }
        .hist-item.selected { background: #1e3a8a; border-color: var(--blue); }
        .key-txt { font-family: monospace; color: var(--blue); font-size: 15px; margin-left: auto; }

        .util-bar { display: flex; gap: 10px; background: #16213e; padding: 15px; border-radius: 12px; margin-bottom: 20px; align-items: center; }
        
        @media print { .no-print { display: none !important; } .hist-item:not(.selected) { display: none !important; } }
    </style>
</head>
<body>
    <div class="container">
        <div id="login_area">
            <h1>SISTEMA QUANTUM</h1>
            <input type="text" id="pin" placeholder="PIN de 6 dígitos" maxlength="6" style="width:100%">
            <button style="background:var(--blue); width:100%; margin-top:15px;" onclick="entrar()">ENTRAR NO NÚCLEO</button>
        </div>

        <div id="dashboard" style="display:none;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <h2 id="emp_nome" style="color:var(--blue); margin:0;"></h2>
                <div class="no-print">
                    <button style="background:#475569" onclick="exportarTXT()">📥 BAIXAR TXT</button>
                    <button style="background:var(--blue)" onclick="window.print()">🖨️ IMPRIMIR</button>
                </div>
            </div>

            <div class="progress-container"><div id="barra" class="progress-bar"></div></div>
            <p id="txt_saldo" style="text-align:right; font-size:12px; margin:0; color:#94a3b8;"></p>

            <div class="util-bar no-print">
                <div style="flex-grow:1">
                    <label style="font-size:11px; display:block">GERAR EM MASSA</label>
                    <select id="qtd_massa">
                        <option value="1">1 Chave</option>
                        <option value="5">5 Chaves</option>
                        <option value="10">10 Chaves</option>
                        <option value="20">20 Chaves</option>
                    </select>
                </div>
                <div style="flex-grow:2">
                    <label style="font-size:11px; display:block">OBSERVAÇÃO DO LOTE</label>
                    <input type="text" id="obs" placeholder="Ex: Lote Premium" style="width:90%">
                </div>
                <button style="background:var(--green); height:45px; margin-top:15px;" onclick="gerarMassa()">EXECUTAR</button>
            </div>

            <input type="text" id="busca" placeholder="🔍 Filtrar por lote ou chave..." style="width:100%; margin-bottom:10px;" onkeyup="filtrar()" class="no-print">

            <div id="lista_historico"></div>
        </div>
    </div>

    <script>
    let dadosAtuais = [];

    async function entrar() {
        const p = document.getElementById('pin').value;
        const res = await fetch('/v1/cliente/dados?pin=' + p);
        if(!res.ok) return alert("PIN Inválido!");
        const d = await res.json();
        dadosAtuais = d.hist;
        
        document.getElementById('login_area').style.display='none';
        document.getElementById('dashboard').style.display='block';
        document.getElementById('emp_nome').innerText = d.empresa;
        document.getElementById('txt_saldo').innerText = `Consumo: ${d.usadas} de ${d.limite}`;
        
        const perc = (d.usadas / d.limite) * 100;
        document.getElementById('barra').style.width = perc + "%";
        renderizar(d.hist);
    }

    function renderizar(hist) {
        let h = "";
        [...hist].reverse().forEach((t, i) => {
            const pt = t.split(' | ');
            h += `<div class="hist-item" id="row-${i}" onclick="this.classList.toggle('selected')">
                <span style="font-size:12px; color:#94a3b8">#${hist.length - i}</span>
                <b style="margin-left:15px; color:white">${pt[1]}</b>
                <span class="key-txt">${pt[2]}</span>
                <button style="background:transparent; color:var(--blue); font-size:10px; border:1px solid var(--blue); margin-left:10px;" onclick="event.stopPropagation(); navigator.clipboard.writeText('${pt[2]}'); alert('Copiado!')">COPY</button>
            </div>`;
        });
        document.getElementById('lista_historico').innerHTML = h;
    }

    async function gerarMassa() {
        const qtd = document.getElementById('qtd_massa').value;
        const pin = document.getElementById('pin').value;
        const obs = document.getElementById('obs').value || "QUANTUM";

        for(let i=0; i < qtd; i++) {
            const res = await fetch('/v1/cliente/gerar', {
                method:'POST', 
                headers:{'Content-Type':'application/json'}, 
                body:JSON.stringify({pin:pin, obs:obs})
            });
            if(!res.ok) { alert("Saldo insuficiente para completar a massa!"); break; }
        }
        entrar();
    }

    function exportarTXT() {
        const conteudo = dadosAtuais.map(t => t.replace(/ \| /g, ' - ')).join('\\n');
        const blob = new Blob([conteudo], {type: 'text/plain'});
        const link = document.createElement('a');
        link.href = window.URL.createObjectURL(blob);
        link.download = `chaves_quantum_${document.getElementById('emp_nome').innerText}.txt`;
        link.click();
    }

    function filtrar() {
        const t = document.getElementById('busca').value.toUpperCase();
        const itens = document.getElementsByClassName('hist-item');
        for (let it of itens) { it.style.display = it.innerText.toUpperCase().includes(t) ? "flex" : "none"; }
    }
    </script>
</body>
</html>
"""

# Mantive as rotas otimizadas para processar massa sem travar o banco
@app.route('/')
def home(): return render_template_string(HTML_SISTEMA)

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
    if c and c[0] < c[1] and c[2]:
        nk = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(25))
        reg = f"X | {d['obs'].upper()} | {nk}"
        cur.execute("UPDATE clientes SET acessos=acessos+1, historico_chaves=array_append(historico_chaves, %s) WHERE pin_hash=%s", (reg, d['pin']))
        conn.commit(); cur.close(); conn.close(); return jsonify({"ok": True})
    cur.close(); conn.close(); return jsonify({"e": "Erro"}), 403