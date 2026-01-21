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
        /* TELA TODA BRANCA E LIMPA */
        :root { --primary: #1e293b; --accent: #38bdf8; --bg: #f8fafc; }
        body { background: var(--bg); color: #1e293b; font-family: 'Segoe UI', sans-serif; padding: 20px; margin: 0; }
        
        .container { max-width: 900px; margin: auto; background: white; padding: 40px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); border: 1px solid #e2e8f0; }
        
        h1 { text-align: center; color: var(--primary); letter-spacing: -1px; }
        
        input { padding: 14px; background: white; border: 2px solid #e2e8f0; color: #1e293b; border-radius: 8px; width: 100%; box-sizing: border-box; font-size: 16px; transition: border 0.3s; }
        input:focus { border-color: var(--accent); outline: none; }
        
        .btn { padding: 15px 25px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; font-size: 16px; transition: 0.3s; width: 100%; }
        .btn-primary { background: var(--primary); color: white; }
        .btn-primary:hover { background: #334155; }
        
        .hist-item { background: #ffffff; padding: 20px; margin-top: 15px; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; cursor: pointer; border: 1px solid #e2e8f0; }
        .hist-item:hover { background: #f1f5f9; }
        .hist-item.selected { border-left: 6px solid var(--primary); background: #f8fafc; }

        /* --- ESTILO DO CERTIFICADO (PARA TELA E IMPRESSÃO) --- */
        .certificado-a4 { 
            display: none; 
            background: white !important; 
            color: black !important; 
            width: 210mm; 
            min-height: 297mm; 
            margin: 20px auto; 
            padding: 25mm; 
            box-sizing: border-box; 
            border: 2px solid #000; /* Moldura externa fina */
            outline: 15px double #000; /* Moldura dupla interna */
            outline-offset: -20px;
            position: relative;
            text-align: center;
        }

        .cert-stamp { position: absolute; top: 40px; right: 60px; border: 3px solid #000; padding: 10px; font-weight: bold; transform: rotate(15deg); text-transform: uppercase; font-size: 14px; }
        .cert-header { font-size: 32px; font-weight: bold; margin-top: 60px; text-transform: uppercase; }
        .cert-subtitle { font-size: 14px; letter-spacing: 4px; margin-bottom: 50px; border-top: 1px solid #000; display: inline-block; padding-top: 5px; }
        .cert-content { font-size: 20px; line-height: 1.6; margin-bottom: 40px; }
        .auth-box { border: 1px solid #000; padding: 20px; margin: 30px auto; width: 80%; }
        .auth-code { font-family: monospace; font-size: 24px; font-weight: bold; }
        .footer-line { margin-top: 80px; display: flex; justify-content: space-around; width: 100%; }
        .sign { border-top: 1px solid #000; width: 200px; font-size: 12px; padding-top: 5px; }

        @media print {
            @page { size: A4; margin: 0; }
            .no-print { display: none !important; }
            body { background: white !important; padding: 0; }
            .container { border: none !important; box-shadow: none !important; width: 100%; max-width: 100%; padding: 0; }
            .certificado-a4 { display: flex !important; flex-direction: column; margin: 0; border: none; outline-offset: -30px; }
        }
    </style>
</head>
<body>
    <div class="container">
        {% if tipo == 'admin' %}
            <h1>ADMINISTRAÇÃO</h1>
            <div class="no-print">
                <input type="password" id="mestre" placeholder="Chave Admin" style="margin-bottom:10px;">
                <button class="btn btn-primary" onclick="listar()">CARREGAR DADOS</button>
            </div>
            <div id="lista_admin"></div>
        {% else %}
            <div id="login_area" style="text-align:center;">
                <h1 style="font-size: 35px; margin-bottom: 10px;">QUANTUM</h1>
                <p style="color: #64748b; margin-bottom: 30px;">Sistema de Autenticação e Registro</p>
                
                <div style="max-width: 400px; margin: auto;">
                    <label style="display:block; text-align:left; font-weight:bold; margin-bottom:5px;">Senha de Acesso</label>
                    <input type="password" id="senha_cli" placeholder="••••••••" maxlength="8">
                    <br><br>
                    <button class="btn btn-primary" onclick="entrar()">ACESSAR PAINEL</button>
                </div>
            </div>

            <div id="dashboard" style="display:none;">
                <div style="display:flex; justify-content:space-between; align-items:center; border-bottom: 2px solid #f1f5f9; padding-bottom: 20px; margin-bottom: 20px;">
                    <h2 id="emp_nome" style="margin:0;"></h2>
                    <button class="btn btn-primary no-print" style="width:auto;" onclick="window.print()">🖨️ IMPRIMIR SELECIONADO</button>
                </div>

                <div class="no-print" style="margin-bottom: 30px;">
                    <label style="display:block; font-weight:bold; margin-bottom:5px;">Novo Registro de Produto</label>
                    <div style="display:flex; gap:10px;">
                        <input type="text" id="obs" placeholder="Ex: Software Quantum Pro">
                        <button class="btn btn-primary" style="width:200px;" onclick="gerar()">GERAR AGORA</button>
                    </div>
                </div>

                <div id="lista_historico"></div>
            </div>
        {% endif %}
    </div>

    <script>
    async function entrar() {
        const s = document.getElementById('senha_cli').value;
        const res = await fetch('/v1/cliente/dados?pin=' + s);
        if(!res.ok) return alert("Senha incorreta!");
        const d = await res.json();
        
        document.getElementById('login_area').style.display='none';
        document.getElementById('dashboard').style.display='block';
        document.getElementById('emp_nome').innerText = d.empresa;
        
        let h_tela = ""; let h_cert = "";
        [...d.hist].reverse().forEach((t, i) => {
            const pt = t.split(' | '); 
            h_tela += `<div class="hist-item no-print" id="row-${i}" onclick="toggleCert(${i})">
                <span><strong style="font-size:18px">${pt[1]}</strong><br><small style="color:#64748b">${pt[0]}</small></span>
                <span style="font-family:monospace; font-weight:bold; color:#0f172a; background:#f1f5f9; padding:8px; border-radius:4px;">${pt[2].substring(0,8)}...</span>
            </div>`;
            
            h_cert += `
                <div class="certificado-a4" id="cert-${i}">
                    <div class="cert-stamp">REGISTO<br>QUANTUM</div>
                    <div class="cert-header">CERTIFICADO DE AUTENTICIDADE</div>
                    <div class="cert-subtitle">REGISTRO OFICIAL DE PROPRIEDADE</div>
                    
                    <div class="cert-content">
                        Certificamos que o item abaixo identificado:<br>
                        <strong style="font-size:28px;">${pt[1]}</strong><br>
                        foi autenticado com sucesso em nosso sistema.
                    </div>

                    <div class="auth-box">
                        <div style="font-size:12px; margin-bottom:10px; font-weight:bold;">CÓDIGO DE VALIDAÇÃO</div>
                        <div class="auth-code">${pt[2]}</div>
                    </div>

                    <p><strong>DATA DE REGISTRO:</strong> ${pt[0]}</p>

                    <div class="footer-line">
                        <div class="sign">Assinatura</div>
                        <div class="sign">Selo de Originalidade</div>
                    </div>
                </div>`;
        });
        document.getElementById('lista_historico').innerHTML = h_tela + h_cert;
    }

    function toggleCert(i) {
        document.querySelectorAll('.certificado-a4').forEach(c => c.style.display = 'none');
        document.querySelectorAll('.hist-item').forEach(r => r.classList.remove('selected'));
        
        const cert = document.getElementById('cert-'+i);
        document.getElementById('row-'+i).classList.add('selected');
        cert.style.display = 'flex';
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
    </script>
</body>
</html>