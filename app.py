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
    <title>SISTEMA DE AUTENTICAÇÃO QUANTUM</title>
    <style>
        :root { --blue: #38bdf8; --dark: #0b1120; --card: #1e293b; --gold: #fbbf24; }
        body { background: var(--dark); color: white; font-family: 'Segoe UI', sans-serif; padding: 20px; }
        .container { max-width: 1000px; margin: auto; background: var(--card); padding: 30px; border-radius: 20px; border: 1px solid #334155; }
        
        input { padding: 12px; background: #0f172a; border: 1px solid #334155; color: white; border-radius: 8px; outline: none; margin-bottom: 5px; }
        button { padding: 10px 15px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; color: white; }
        
        .progress-container { background: #0f172a; border-radius: 10px; height: 10px; margin: 15px 0; overflow: hidden; }
        .progress-bar { height: 100%; background: var(--blue); width: 0%; transition: 0.5s; }
        .infinite-bar { background: linear-gradient(90deg, var(--blue), var(--gold), var(--blue)); background-size: 200%; animation: move 2s linear infinite; width: 100% !important; }
        @keyframes move { 0% {background-position: 0%} 100% {background-position: 200%} }

        .hist-item { background: #0f172a; padding: 15px; margin-top: 10px; border-radius: 10px; display: flex; justify-content: space-between; cursor: pointer; border: 1px solid transparent; }
        .hist-item.selected { border-color: var(--gold); background: #1e3a8a; }

        /* --- CERTIFICADO DE AUTENTICAÇÃO (IMPRESSÃO) --- */
        .certificado { display: none; }

        @media print {
            .no-print, button, input, h1, h2, .progress-container, .hist-item, label, p { display: none !important; }
            body { background: white !important; color: black !important; padding: 0; }
            .container { border: none !important; background: white !important; width: 100%; max-width: 100%; }
            
            .certificado { 
                display: block !important;
                border: 8px double #1e293b;
                padding: 50px;
                margin-bottom: 80px;
                text-align: center;
                position: relative;
                page-break-inside: avoid;
                background: #fff;
            }
            .cert-header { font-size: 26px; font-weight: bold; margin-bottom: 10px; letter-spacing: 2px; }
            .cert-id { font-size: 12px; color: #666; margin-bottom: 30px; }
            .cert-body { font-size: 19px; margin: 25px 0; line-height: 1.6; }
            
            /* Box do Código de Autenticação */
            .auth-box { border: 2px solid #000; padding: 20px; display: inline-block; margin: 20px 0; background: #f8f9fa; }
            .auth-code { font-family: 'Courier New', monospace; font-size: 26px; font-weight: bold; letter-spacing: 3px; }
            
            .assinatura-area { margin-top: 50px; display: flex; justify-content: space-around; }
            .linha { border-top: 1px solid #000; width: 200px; padding-top: 5px; font-size: 11px; }

            /* Simulação de Selo de Segurança */
            .stamp { position: absolute; top: 30px; left: 30px; border: 3px solid #000; padding: 5px; font-size: 10px; font-weight: bold; opacity: 0.7; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div id="login_area">
            <h1 style="text-align:center">NÚCLEO QUANTUM</h1>
            <input type="text" id="pin" placeholder="PIN de 6 dígitos" maxlength="6" style="width:100%; text-align:center">
            <button style="background:var(--blue); width:100%; margin-top:10px;" onclick="entrar()">AUTENTICAR ACESSO</button>
        </div>

        <div id="dashboard" style="display:none;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <h2 id="emp_nome" style="color:var(--blue)"></h2>
                <button class="no-print" style="background:var(--gold); color:black" onclick="window.print()">🖨️ IMPRIMIR AUTENTICADORES</button>
            </div>
            <div class="progress-container"><div id="barra" class="progress-bar"></div></div>
            
            <div class="no-print" style="margin:20px 0; background:#16213e; padding:15px; border-radius:10px;">
                <input type="text" id="obs" placeholder="Referência/Lote" style="width:50%">
                <button style="background:var(--blue)" onclick="gerar()">GERAR NOVO CÓDIGO</button>
            </div>

            <div id="lista_historico"></div>
        </div>
    </div>

    <script>
    async function entrar() {
        const p = document.getElementById('pin').value;
        const res = await fetch('/v1/cliente/dados?pin=' + p);
        if(!res.ok) return alert("Erro na autenticação!");
        const d = await res.json();
        
        document.getElementById('login_area').style.display='none';
        document.getElementById('dashboard').style.display='block';
        document.getElementById('emp_nome').innerText = d.empresa;
        
        const b = document.getElementById('barra');
        if(d.limite == -1) b.classList.add('infinite-bar');
        else b.style.width = (d.usadas/d.limite*100) + "%";

        let h_tela = ""; let h_cert = "";
        [...d.hist].reverse().forEach((t, i) => {
            const pt = t.split(' | ');
            const authID = "Q-" + Math.random().toString(36).substr(2, 9).toUpperCase();
            
            h_tela += `<div class="hist-item" id="row-${i}" onclick="toggleCert(${i})">
                <b>${pt[1]}</b> <span style="font-family:monospace; color:var(--blue)">${pt[2]}</span>
            </div>`;
            
            h_cert += `
                <div class="certificado" id="cert-${i}">
                    <div class="stamp">REGISTRO OFICIAL</div>
                    <div class="cert-header">CERTIFICADO DE AUTENTICAÇÃO</div>
                    <div class="cert-id">Protocolo de Segurança: ${authID}</div>
                    <div class="cert-body">
                        Validamos por meio deste documento o código gerado para:<br>
                        <strong>SISTEMA / MÓDULO: ${pt[1]}</strong>
                    </div>
                    <div class="auth-box">
                        <div style="font-size:10px; margin-bottom:5px;">CÓDIGO DE AUTENTICAÇÃO</div>
                        <div class="auth-code">${pt[2]}</div>
                    </div>
                    <div class="cert-body" style="font-size:14px;">
                        A autenticidade deste código pode ser verificada junto ao emissor.<br>
                        Gerado em: ${new Date().toLocaleString('pt-BR')}
                    </div>
                    <div class="assinatura-area">
                        <div class="linha">Assinatura do Responsável</div>
                        <div class="linha">Carimbo de Validação</div>
                    </div>
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
        await fetch('/v1/cliente/gerar', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({pin:p, obs:document.getElementById('obs').value || "PADRÃO"})});
        entrar();
    }
    </script>
</body>
</html>