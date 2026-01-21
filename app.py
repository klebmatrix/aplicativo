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
    <title>SISTEMA QUANTUM | REGISTO OFICIAL</title>
    <style>
        :root { --blue: #38bdf8; --dark: #0b1120; --card: #1e293b; --gold: #fbbf24; }
        body { background: var(--dark); color: white; font-family: 'Segoe UI', sans-serif; padding: 20px; }
        .container { max-width: 1000px; margin: auto; background: var(--card); padding: 30px; border-radius: 15px; border: 1px solid #334155; }
        
        input { padding: 12px; background: #1e293b; border: 1px solid #334155; color: white; border-radius: 8px; margin-bottom: 5px; }
        .btn { padding: 10px 15px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; color: white; }
        
        .hist-item { background: #0f172a; padding: 15px; margin-top: 10px; border-radius: 10px; display: flex; justify-content: space-between; cursor: pointer; border: 1px solid transparent; }
        .hist-item.selected { border-color: var(--gold); background: #1e3a8a; }

        /* --- LAYOUT DO CERTIFICADO A4 (BRANCO PARA IMPRESSÃO) --- */
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
            }

            .cert-header { font-size: 35px; font-weight: bold; text-decoration: underline; margin-bottom: 10px; }
            .cert-subtitle { font-size: 16px; letter-spacing: 5px; margin-bottom: 50px; font-weight: bold; }
            
            .cert-content { font-size: 20px; line-height: 1.8; text-align: center; margin-bottom: 40px; }
            .highlight { font-weight: bold; font-size: 24px; text-transform: uppercase; }

            .auth-box { border: 2px solid #000; padding: 20px; width: 85%; background: #fcfcfc; margin: 20px 0; }
            .auth-code { font-family: 'Courier New', monospace; font-size: 28px; font-weight: bold; letter-spacing: 3px; }

            .date-box { font-size: 16px; margin: 20px 0; border-top: 1px solid #eee; padding-top: 10px; }
            
            .footer-area { margin-top: 60px; width: 100%; display: flex; justify-content: space-around; }
            .signature { border-top: 1px solid #000; width: 220px; font-size: 12px; padding-top: 8px; text-align: center; }
            .stamp-watermark { position: absolute; top: 45mm; right: 35mm; border: 4px solid #000; padding: 10px; transform: rotate(15deg); font-weight: bold; opacity: 0.8; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div id="dashboard" style="display:none;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <h2 id="emp_nome" style="color:var(--blue)"></h2>
                <button class="btn no-print" style="background:var(--gold); color:black" onclick="window.print()">🖨️ IMPRIMIR SELECIONADOS (A4)</button>
            </div>

            <div class="no-print" style="margin:20px 0; background:#0f172a; padding:20px; border-radius:10px; border-left: 5px solid var(--blue);">
                <input type="text" id="obs" placeholder="Nome do Produto / Lote" style="width:60%">
                <button class="btn" style="background:var(--blue)" onclick="gerar()">GERAR AUTENTICAÇÃO</button>
            </div>

            <div id="lista_historico"></div>
        </div>
    </div>

    <script>
    async function entrar() {
        const p = document.getElementById('pin_cli').value;
        const res = await fetch('/v1/cliente/dados?pin=' + p);
        const d = await res.json();
        
        document.getElementById('login_area').style.display='none';
        document.getElementById('dashboard').style.display='block';
        document.getElementById('emp_nome').innerText = d.empresa;
        
        let h_tela = ""; let h_cert = "";
        [...d.hist].reverse().forEach((t, i) => {
            const pt = t.split(' | '); 
            // pt[0] = Data/Hora | pt[1] = Obs | pt[2] = Código
            
            h_tela += `<div class="hist-item no-print" id="row-${i}" onclick="toggleCert(${i})">
                <span><b>${pt[1]}</b> <br><small>${pt[0]}</small></span>
                <span style="font-family:monospace; color:var(--blue)">${pt[2]}</span>
            </div>`;
            
            h_cert += `
                <div class="certificado-a4" id="cert-${i}">
                    <div class="stamp-watermark">REGISTO<br>QUANTUM</div>
                    <div class="cert-header">CERTIFICADO DE AUTENTICIDADE</div>
                    <div class="cert-subtitle">DOCUMENTO DE GARANTIA E LICENCIAMENTO</div>
                    
                    <div class="cert-content">
                        Declaramos que o produto/módulo identificado como:<br>
                        <span class="highlight">${pt[1]}</span><br>
                        foi devidamente registado no nosso banco de dados global.
                    </div>

                    <div class="auth-box">
                        <div style="font-size:12px; margin-bottom:5px;">CÓDIGO DE AUTENTICAÇÃO ÚNICO</div>
                        <div class="auth-code">${pt[2]}</div>
                    </div>

                    <div class="date-box">
                        <strong>DATA DE REGISTO:</strong> ${pt[0]}<br>
                        <strong>ESTADO:</strong> ATIVO / ORIGINAL
                    </div>

                    <div class="cert-content" style="font-size:14px; margin-top:20px;">
                        Este código é único e intransferível, garantindo a integridade da licença.<br>
                        A validade deste documento é permanente após a data de registo.
                    </div>

                    <div class="footer-area">
                        <div class="signature">Assinatura do Responsável</div>
                        <div class="signature">Carimbo da Empresa</div>
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
        const p = document.getElementById('pin_cli').value;
        const now = new Date().toLocaleString('pt-PT');
        const res = await fetch('/v1/cliente/gerar', {
            method:'POST', 
            headers:{'Content-Type':'application/json'}, 
            body:JSON.stringify({pin:p, obs:document.getElementById('obs').value || "GERAL", data: now})
        });
        if(res.ok) entrar();
    }
    </script>
</body>
</html>