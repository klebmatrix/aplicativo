import os, secrets, string, psycopg2, datetime
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
    <title>SISTEMA QUANTUM | AUTENTICAÇÃO</title>
    <style>
        :root { --blue: #38bdf8; --dark: #0b1120; --card: #1e293b; --gold: #fbbf24; }
        body { background: var(--dark); color: white; font-family: 'Segoe UI', sans-serif; padding: 20px; }
        .container { max-width: 1000px; margin: auto; background: var(--card); padding: 30px; border-radius: 15px; border: 1px solid #334155; }
        
        input { padding: 12px; background: #1e293b; border: 1px solid #334155; color: white; border-radius: 8px; margin-bottom: 5px; }
        .btn { padding: 10px 15px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; color: white; }
        
        .hist-item { background: #0f172a; padding: 15px; margin-top: 10px; border-radius: 10px; display: flex; justify-content: space-between; cursor: pointer; border: 1px solid transparent; }
        .hist-item.selected { border-color: var(--gold); background: #1e3a8a; }

        /* --- LAYOUT DO CERTIFICADO A4 --- */
        .certificado-a4 { display: none; }

        @media print {
            @page { size: A4; margin: 0; }
            .no-print { display: none !important; }
            body { background: white !important; color: black !important; padding: 0; margin: 0; }
            .container { border: none !important; background: white !important; width: 100%; max-width: 100%; }
            
            .certificado-a4 { 
                display: flex !important;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                width: 210mm;
                height: 297mm;
                padding: 30mm;
                box-sizing: border-box;
                border: 20px double #000;
                position: relative;
                page-break-after: always;
                background: white !important;
                color: black !important;
                text-align: center;
            }

            .cert-header { font-size: 35px; font-weight: bold; text-decoration: underline; margin-bottom: 10px; }
            .cert-subtitle { font-size: 16px; letter-spacing: 5px; margin-bottom: 50px; font-weight: bold; }
            .auth-box { border: 2px solid #000; padding: 20px; width: 85%; margin: 20px 0; }
            .auth-code { font-family: monospace; font-size: 28px; font-weight: bold; letter-spacing: 3px; }
            .footer-area { margin-top: 60px; width: 100%; display: flex; justify-content: space-around; }
            .signature { border-top: 1px solid #000; width: 220px; font-size: 12px; padding-top: 8px; }
        }
    </style>
</head>
<body>
    <div class="container">
        {% if tipo == 'admin' %}
            <h1>PAINEL ADMIN</h1>
            <div class="no-print">
                <input type="password" id="mestre" placeholder="Chave Admin">
                <button class="btn" style="background:var(--blue)" onclick="listar()">CARREGAR</button>
            </div>
            <div id="lista_admin"></div>
        {% else %}
            <div id="login_area" style="text-align:center; padding: 80px 0;">
                <h1 style="color:var(--blue)">ÁREA DO CLIENTE</h1>
                <p>Por favor, insira sua senha de acesso:</p>
                <input type="password" id="senha_cli" placeholder="DIGITE SUA SENHA" maxlength="8" style="width:280px; text-align:center; font-size:20px;">
                <br><br>
                <button class="btn" style="background:var(--blue); width:305px; height:50px;" onclick="entrar()">ACESSAR SISTEMA</button>
            </div>

            <div id="dashboard" style="display:none;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h2 id="emp_nome" style="color:var(--blue)"></h2>
                    <button class="btn no-print" style="background:var(--gold); color:black" onclick="window.print()">🖨️ IMPRIMIR SELECIONADOS</button>
                </div>

                <div class="no-print" style="margin:20px 0; background:#0f172a; padding:20px; border-radius:10px;">
                    <input type="text" id="obs" placeholder="Nome do Produto / Lote" style="width:60%">
                    <button class="btn" style="background:var(--blue)" onclick="gerar()">GERAR REGISTRO</button>
                </div>

                <div id="lista_historico"></div>
            </div>
        {% endif %}
    </div>

    <script>
    async function entrar() {
        const s = document.getElementById('senha_cli').value;
        const res = await fetch('/v1/cliente/dados?pin=' + s); // Mantemos 'pin' na URL para não quebrar o backend
        if(!res.ok) return alert("Senha incorreta!");
        const d = await res.json();
        
        document.getElementById('login_area').style.display='none';
        document.getElementById('dashboard').style.display='block';
        document.getElementById('emp_nome').innerText = d.empresa;
        
        let h_tela = ""; let h_cert = "";
        [...d.hist].reverse().forEach((t, i) => {
            const pt = t.split(' | '); 
            h_tela += `<div class="hist-item no-print" id="row-${i}" onclick="toggleCert(${i})">
                <span><b>${pt[1]}</b> <br><small>Registrado em: ${pt[0]}</small></span>
                <span style="font-family:monospace; color:var(--blue)">${pt[2]}</span>
            </div>`;
            
            h_cert += `
                <div class="certificado-a4" id="cert-${i}">
                    <div class="cert-header">CERTIFICADO DE AUTENTICIDADE</div>
                    <div class="cert-subtitle">REGISTRO OFICIAL DE PROPRIEDADE</div>
                    <div style="font-size:20px; margin-bottom:30px;">
                        Certificamos que o item <br><strong>${pt[1]}</strong><br> foi autenticado com sucesso.
                    </div>
                    <div class="auth-box">
                        <div style="font-size:12px; margin-bottom:5px;">CÓDIGO DE VALIDAÇÃO</div>
                        <div class="auth-code">${pt[2]}</div>
                    </div>
                    <p><strong>DATA DE REGISTRO:</strong> ${pt[0]}</p>
                    <div class="footer-area">
                        <div class="signature">Assinatura</div>
                        <div class="signature">Selo de Originalidade</div>
                    </div>
                </div>`;
        });
        document.getElementById('lista_historico').innerHTML = h_tela + h_cert;
    }

    function toggleCert(i) {
        const row = document.getElementById('row-'+i);
        const cert = document.getElementById('cert-'+i);
        row.classList.toggle('selected');
        cert.style.display = (cert.style.display === 'flex') ? 'none' : 'flex';
    }

    async function gerar() {
        const s = document.getElementById('senha_cli').value;
        const res = await fetch('/v1/cliente/gerar', {
            method:'POST', 
            headers:{'Content-Type':'application/json'}, 
            body:JSON.stringify({pin:s, obs:document.getElementById('obs').value || "PRODUTO PADRÃO"})
        });
        if(res.ok) entrar();
    }
    // Funções Admin permanecem as mesmas
    </script>
</body>
</html>
"""

# --- BACKEND (Python) ---
@app.route('/v1/cliente/gerar', methods=['POST'])
def gen_key():
    d = request.json
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT acessos, limite FROM clientes WHERE pin_hash = %s", (d['pin'],))
    c = cur.fetchone()
    if c and (c[1] == -1 or c[0] < c[1]):
        nk = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(25))
        data_atual = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
        reg = f"{data_atual} | {d['obs'].upper()} | {nk}"
        cur.execute("UPDATE clientes SET acessos=acessos+1, historico_chaves=array_append(historico_chaves, %s) WHERE pin_hash=%s", (reg, d['pin']))
        conn.commit(); cur.close(); conn.close(); return jsonify({"ok": True})
    cur.close(); conn.close(); return jsonify({"e": 403}), 403

# (As outras rotas de admin e listagem continuam as mesmas do código anterior)