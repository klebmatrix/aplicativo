import os
import secrets
import string
import psycopg2
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

ADMIN_KEY = os.environ.get('ADMIN_KEY')

def get_db_connection():
    url = os.environ.get('DATABASE_URL')
    if url and url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return psycopg2.connect(url, sslmode='require')

def generate_quantum_key(length=30):
    chars = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))

HTML_SISTEMA = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>KLEBMATRIX | QUANTUM CUSTOM</title>
    <style>
        body { background: #0b1120; color: white; font-family: sans-serif; text-align: center; padding: 20px; }
        .container { background: #1e293b; padding: 25px; border-radius: 15px; display: inline-block; width: 95%; max-width: 650px; border: 1px solid #334155; }
        input, select { padding: 12px; margin: 8px; background: #0f172a; border: 1px solid #334155; color: white; border-radius: 6px; width: 85%; }
        button { padding: 12px 24px; background: #0284c7; border: none; color: white; cursor: pointer; border-radius: 6px; font-weight: bold; width: 85%; }
        .key-box { background: #fff; color: #000; padding: 15px; font-family: monospace; border-radius: 6px; margin: 15px 0; word-break: break-all; font-weight: bold; }
        .hist-card { background: #0f172a; padding: 10px; margin-top: 8px; border-radius: 6px; text-align: left; border-left: 10px solid #334155; font-size: 12px; }
        .label { display: block; text-align: left; margin-left: 8%; font-size: 12px; color: #38bdf8; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        {% if tipo == 'admin' %}
            <h2>PAINEL MASTER</h2>
            <input type="password" id="mestre" placeholder="Chave Mestre">
            <button onclick="listar()">ATUALIZAR LISTA</button>
            <hr style="border:0; border-top:1px solid #334155; margin:20px 0;">
            <input type="text" id="n" placeholder="Nome Empresa">
            <input type="text" id="p" placeholder="PIN">
            <input type="number" id="l" placeholder="Créditos" value="10">
            <button onclick="add()" style="background:#22c55e">CADASTRAR</button>
            <div id="lista_admin"></div>
        {% else %}
            <h1 style="color:#38bdf8">KLEBMATRIX QUANTUM</h1>
            
            <label class="label">SEU PIN DE ACESSO:</label>
            <input type="password" id="pin" placeholder="••••••">
            
            <label class="label">E-MAIL DO DESTINATÁRIO (OPCIONAL):</label>
            <input type="email" id="desc_email" placeholder="cliente@email.com">
            
            <label class="label">COR DE IDENTIFICAÇÃO:</label>
            <select id="desc_cor">
                <option value="#38bdf8">AZUL (Padrão)</option>
                <option value="#22c55e">VERDE (Ativado)</option>
                <option value="#eab308">AMARELO (Pendente)</option>
                <option value="#ef4444">VERMELHO (Urgente)</option>
            </select>

            <button onclick="gerar()" style="margin-top:20px;">GERAR CHAVE PERSONALIZADA</button>
            <div id="res" style="margin-top:20px;"></div>
        {% endif %}
    </div>

    <script>
    async function add() {
        const res = await fetch('/admin/cadastrar', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({key: document.getElementById('mestre').value, n: document.getElementById('n').value, p: document.getElementById('p').value, l: document.getElementById('l').value})
        });
        const d = await res.json(); alert(d.msg || d.erro); listar();
    }
    async function listar() {
        const k = document.getElementById('mestre').value;
        const res = await fetch('/admin/listar?key=' + k);
        const dados = await res.json();
        let html = "<table><tr><th>Empresa</th><th>PIN</th><th>Uso</th></tr>";
        dados.forEach(c => { html += `<tr><td>${c.n}</td><td>${c.p}</td><td>${c.u}/${c.l}</td></tr>`; });
        document.getElementById('lista_admin').innerHTML = html + "</table>";
    }
    async function gerar() {
        const r = document.getElementById('res');
        r.innerHTML = "Processando...";
        const res = await fetch('/v1/quantum-key', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ 
                pin: document.getElementById('pin').value,
                email: document.getElementById('desc_email').value || "Sem E-mail",
                cor: document.getElementById('desc_cor').value
            })
        });
        const d = await res.json();
        if(res.ok) {
            r.innerHTML = `
                <div style="text-align:left; background:#0f172a; padding:15px; border-radius:10px; border:1px solid ${d.cor_usada}">
                    <p><b>${d.empresa}</b> | Créditos: ${d.usadas}/${d.limite}</p>
                    <div class="key-box" id="ch">${d.key}</div>
                    <button onclick="navigator.clipboard.writeText('${d.key}'); alert('Copiado!')" style="background:#22c55e; width:100%">COPIAR</button>
                    <p style="margin-top:15px; font-size:12px">HISTÓRICO RECENTE:</p>
                    ${d.hist.map(h => `<div class="hist-card" style="border-left-color:${h.cor}">${h.texto}</div>`).join('')}
                </div>`;
        } else { r.innerHTML = "<b style='color:red'>ERRO: PIN INVÁLIDO OU SEM CRÉDITOS</b>"; }
    }
    </script>
</body>
</html>
"""

@app.route('/')
def home(): return render_template_string(HTML_SISTEMA, tipo='login')

@app.route('/painel-secreto-kleber')
def admin_page(): return render_template_string(HTML_SISTEMA, tipo='admin')

@app.route('/admin/cadastrar', methods=['POST'])
def add():
    d = request.json
    if not ADMIN_KEY or d.get('key') != ADMIN_KEY: return jsonify({"erro": "Erro"}), 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("INSERT INTO clientes (nome_empresa, pin_hash, limite) VALUES (%s, %s, %s)", (d['n'], d['p'], d['l']))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"msg": "OK"})

@app.route('/admin/listar')
def list_all():
    if not ADMIN_KEY or request.args.get('key') != ADMIN_KEY: return jsonify([]), 403
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT nome_empresa, pin_hash, COALESCE(acessos,0), COALESCE(limite,0) FROM clientes")
    r = cur.fetchall(); cur.close(); conn.close()
    return jsonify([{"n": x[0], "p": x[1], "u": x[2], "l": x[3]} for x in r])

@app.route('/v1/quantum-key', methods=['POST'])
def login():
    d = request.json
    pin = d.get('pin', '').strip()
    email = d.get('email', 'Sem E-mail')
    cor = d.get('cor', '#38bdf8')
    
    try:
        conn = get_db_connection(); cur = conn.cursor()
        cur.execute("SELECT nome_empresa, acessos, limite, historico_chaves FROM clientes WHERE pin_hash = %s", (pin,))
        c = cur.fetchone()
        
        if c and c[1] < c[2]:
            nk = generate_quantum_key(30)
            # Salvamos a cor e o email dentro da string do histórico
            info_completa = f"{cor}|{email}|{nk}"
            cur.execute("UPDATE clientes SET acessos=acessos+1, historico_chaves=array_append(historico_chaves, %s) WHERE pin_hash=%s RETURNING historico_chaves", (info_completa, pin))
            h_raw = cur.fetchone()[0]
            conn.commit(); cur.close(); conn.close()
            
            # Formata o histórico para o cliente ver bonitinho
            h_formatado = []
            for item in h_raw[-5:]:
                partes = item.split('|')
                if len(partes) == 3:
                    h_formatado.append({"cor": partes[0], "texto": f"{partes[1]}: {partes[2]}"})
            
            return jsonify({
                "empresa": c[0], "usadas": c[1]+1, "limite": c[2], 
                "key": nk, "cor_usada": cor, "hist": h_formatado[::-1]
            })
        cur.close(); conn.close()
    except: pass
    return jsonify({"status": "error"}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))