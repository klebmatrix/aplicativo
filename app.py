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
    <title>QUANTUM | CERTIFICADOS PREMIUM</title>
    <style>
        :root { --blue: #38bdf8; --dark: #0b1120; --card: #1e293b; --gold: #fbbf24; }
        body { background: var(--dark); color: white; font-family: 'Segoe UI', sans-serif; padding: 20px; }
        .container { max-width: 1000px; margin: auto; background: var(--card); padding: 30px; border-radius: 20px; border: 1px solid #334155; }
        
        input, select { padding: 12px; background: #0f172a; border: 1px solid #334155; color: white; border-radius: 8px; outline: none; margin-bottom: 5px; }
        button { padding: 10px 15px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; color: white; }
        
        .progress-container { background: #0f172a; border-radius: 10px; height: 12px; margin: 15px 0; border: 1px solid #334155; overflow: hidden; }
        .progress-bar { height: 100%; background: var(--blue); width: 0%; transition: 0.5s; }
        .infinite-bar { background: linear-gradient(90deg, var(--blue), var(--gold), var(--blue)); background-size: 200%; animation: move 2s linear infinite; width: 100% !important; }
        @keyframes move { 0% {background-position: 0%} 100% {background-position: 200%} }

        .hist-item { background: #0f172a; padding: 15px; margin-top: 10px; border-radius: 10px; display: flex; justify-content: space-between; cursor: pointer; border: 1px solid transparent; }
        .hist-item.selected { border-color: var(--gold); background: #1e3a8a; }

        /* --- LAYOUT DO CERTIFICADO PARA IMPRESSÃO --- */
        .certificado { display: none; }

        @media print {
            .no-print, button, input, select, h1, h2, .progress-container, .hist-item, label, p { display: none !important; }
            body { background: white !important; color: black !important; padding: 0; }
            .container { border: none !important; background: white !important; width: 100%; max-width: 100%; }
            
            .certificado { 
                display: block !important;
                border: 10px double #1e293b;
                padding: 40px;
                margin-bottom: 60px;
                text-align: center;
                position: relative;
                page-break-inside: avoid;
                background: #fff;
            }
            .cert-header { font-size: 30px; font-weight: bold; text-decoration: underline; margin-bottom: 15px; }
            .cert-body { font-size: 18px; margin: 30px 0; line-height: 1.5; }
            .cert-key { font-family: monospace; font-size: 24px; font-weight: bold; border: 2px solid #000; padding: 10px; display: block; margin: 20px auto; width: fit-content; }
            
            .assinatura-area { margin-top: 60px; display: flex; justify-content: space-around; align-items: flex-end; }
            .linha-assinatura { border-top: 1px solid #000; width: 250px; text-align: center; font-size: 12px; padding-top: 5px; }
            
            .selo-oficial { position: absolute; top: 40px; right: 40px; border: 4px solid #000; padding: 5px; font-size: 10px; font-weight: bold; transform: rotate(10deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        {% if tipo == 'admin' %}
            <h1>PAINEL ADMIN</h1>
            <input type="password" id="mestre" placeholder="Chave Mestra">
            <button style="background:var(--blue)" onclick="listar()">LISTAR</button>
            <div id="lista_admin"></div>
        {% else %}
            <div id="login_area">
                <h1 style="text-align:center">QUANTUM LOGIN</h1>
                <input type="text" id="pin" placeholder="Seu PIN de 6 dígitos" maxlength="6" style="width:100%">
                <button style="background:var(--blue); width:100%; margin-top:10px;" onclick="entrar()">ENTRAR</button>
            </div>

            <div id="dashboard" style="display:none;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h2 id="emp_nome" style="color:var(--blue)"></h2>
                    <button class="no-print" style="background:var(--gold); color:black" onclick="window.print()">🖨️ IMPRIMIR SELECIONADOS</button>
                </div>
                <div class="progress-container"><div id="barra" class="progress-bar"></div></div>
                
                <div class="no-print" style="margin:20px 0; background:#16213e; padding:15px; border-radius:10px;">
                    <input type="text" id="obs" placeholder="Nome do Lote" style="width:50%">
                    <button style="background:var(--blue)" onclick="gerar()">GERAR CHAVE</button>
                </div>

                <div id="lista_historico"></div>
            </div>
        {% endif %}
    </div>

    <script>
    async function entrar() {
        const p = document.getElementById('pin').value;
        const res = await fetch('/v1/cliente/dados?pin=' + p);
        const d = await res.json();
        if(!res.ok) return alert("PIN Inválido!");
        
        document.getElementById('login_area').style.display='none';
        document.getElementById('dashboard').style.display='block';
        document.getElementById('emp_nome').innerText = d.empresa;
        
        const b = document.getElementById('barra');
        if(d.limite == -1) b.classList.add('infinite-bar');
        else b.style.width = (d.usadas/d.limite*100) + "%";

        let h_tela = ""; let h_cert = "";
        [...d.hist].reverse().forEach((t, i) => {
            const pt = t.split(' | ');
            h_tela += `<div class="hist-item" id="row-${i}" onclick="toggleCert(${i})">
                <b>${pt[1]}</b> <span style="font-family:monospace; color:var(--blue)">${pt[2]}</span>
            </div>`;
            h_cert += `
                <div class="certificado" id="cert-${i}">
                    <div class="selo-oficial">AUTENTICADO<br>SISTEMA QUANTUM</div>
                    <div class="cert-header">CERTIFICADO DE LICENÇA</div>
                    <div class="cert-body">
                        Declaramos para os devidos fins que a licença referente ao lote <b>${pt[1]}</b><br>
                        foi devidamente processada e autenticada.<br>
                        <span class="cert-key">${pt[2]}</span>
                        Segurança e integridade garantidas via criptografia quântica.
                    </div>
                    <div class="assinatura-area">
                        <div class="linha-assinatura">Assinatura do Responsável</div>
                        <div class="linha-assinatura">Data: ${new Date().toLocaleDateString()}</div>
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
        await fetch('/v1/cliente/gerar', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({pin:p, obs:document.getElementById('obs').value || "GERAL"})});
        entrar();
    }
    // Funções Admin permanecem as mesmas (listar, addCr, setSub, del)
    </script>
</body>
</html>