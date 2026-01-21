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
        body { background: var(--dark); color: white; font-family: 'Segoe UI', serif; padding: 20px; }
        .container { max-width: 1000px; margin: auto; background: var(--card); padding: 30px; border-radius: 15px; border: 1px solid #334155; }
        
        /* BOTÕES E INPUTS */
        input { padding: 12px; background: #1e293b; border: 1px solid #334155; color: white; border-radius: 8px; margin-bottom: 5px; }
        .btn { padding: 10px 15px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; color: white; transition: 0.2s; }
        
        /* DASHBOARD */
        .hist-item { background: #0f172a; padding: 15px; margin-top: 10px; border-radius: 10px; display: flex; justify-content: space-between; cursor: pointer; border: 1px solid transparent; }
        .hist-item.selected { border-color: var(--gold); background: #1e3a8a; }

        /* --- LAYOUT A4 DE IMPRESSÃO --- */
        .certificado-a4 { display: none; }

        @media print {
            @page { size: A4; margin: 0; }
            .no-print { display: none !important; }
            body { background: white !important; color: black !important; padding: 0; margin: 0; }
            .container { border: none !important; background: white !important; max-width: 100%; width: 100%; }
            
            .certificado-a4 { 
                display: flex !important;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                width: 210mm;
                height: 297mm;
                padding: 40mm;
                box-sizing: border-box;
                border: 25px double #1e293b; /* Borda luxuosa */
                position: relative;
                page-break-after: always;
                text-align: center;
                margin: 0 auto;
            }

            .cert-stamp { position: absolute; top: 60mm; right: 40mm; border: 4px solid #000; padding: 10px; font-weight: bold; transform: rotate(15deg); opacity: 0.6; }
            .cert-title { font-size: 42px; font-weight: bold; text-transform: uppercase; margin-bottom: 20px; border-bottom: 4px solid #000; }
            .cert-subtitle { font-size: 20px; letter-spacing: 5px; color: #555; margin-bottom: 60px; }
            .cert-body { font-size: 24px; line-height: 1.8; margin-bottom: 50px; }
            
            .auth-box { border: 3px solid #000; padding: 30px; background: #f9f9f9; margin-bottom: 60px; }
            .auth-label { font-size: 14px; margin-bottom: 10px; display: block; }
            .auth-code { font-family: 'Courier New', monospace; font-size: 32px; font-weight: bold; letter-spacing: 5px; }
            
            .footer-sign { margin-top: 100px; width: 100%; display: flex; justify-content: space-around; }
            .sign-line { border-top: 2px solid #000; width: 250px; font-size: 14px; padding-top: 10px; }
        }
    </style>
</head>
<body>
    <div class="container">
        {% if tipo == 'admin' %}
            <h1 style="color:var(--blue)">ADMINISTRAÇÃO MESTRE</h1>
            <div class="no-print">
                <input type="password" id="mestre" placeholder="Chave Admin">
                <button class="btn" style="background:var(--blue)" onclick="listar()">CARREGAR CLIENTES</button>
            </div>
            <div id="lista_admin"></div>

        {% else %}
            <div id="login_area" style="text-align:center; padding: 100px 0;">
                <h1 style="font-size:40px">QUANTUM AUTH</h1>
                <input type="password" id="pin_cli" placeholder="Senha de até 8 dígitos" maxlength="8" style="width:300px; text-align:center; font-size:22px;">
                <br><br>
                <button class="btn" style="background:var(--blue); width:325px; height:50px;" onclick="entrar()">AUTENTICAR</button>
            </div>

            <div id="dashboard" style="display:none;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h2 id="emp_nome" style="color:var(--blue)"></h2>
                    <button class="btn no-print" style="background:var(--gold); color:black" onclick="window.print()">🖨️ IMPRIMIR CERTIFICADO A4</button>
                </div>

                <div class="no-print" style="margin:20px 0; background:#0f172a; padding:20px; border-radius:10px; border-left: 4px solid var(--green);">
                    <input type="text" id="obs" placeholder="Referência (Ex: Lote Software X)" style="width:60%">
                    <button class="btn" style="background:var(--green); width:30%" onclick="gerar()">GERAR AUTENTICADOR</button>
                </div>

                <div id="lista_historico"></div>
            </div>
        {% endif %}
    </div>

    <script>
    async function entrar() {
        const p = document.getElementById('pin_cli').value;
        const res = await fetch('/v1/cliente/dados?pin=' + p);
        if(!res.ok) return alert("PIN Inválido!");
        const d = await res.json();
        
        document.getElementById('login_area').style.display='none';
        document.getElementById('dashboard').style.display='block';
        document.getElementById('emp_nome').innerText = d.empresa;
        
        let h_tela = ""; let h_cert = "";
        [...d.hist].reverse().forEach((t, i) => {
            const pt = t.split(' | ');
            h_tela += `<div class="hist-item no-print" id="row-${i}" onclick="toggleCert(${i})">
                <span><b>${pt[1]}</b></span> <span style="font-family:monospace; color:var(--blue)">${pt[2]}</span>
            </div>`;
            
            h_cert += `
                <div class="certificado-a4" id="cert-${i}">
                    <div class="cert-stamp">VALIDADO E<br>ORIGINAL</div>
                    <div class="cert-title">Certificado</div>
                    <div class="cert-subtitle">DE AUTENTICIDADE</div>
                    
                    <div class="cert-body">
                        Certificamos para os devidos fins de direito que a licença<br>
                        referente ao módulo <strong>${pt[1]}</strong> foi processada<br>
                        e autenticada com sucesso pelo Sistema Quantum.
                    </div>

                    <div class="auth-box">
                        <span class="auth-label">CÓDIGO DE AUTENTICAÇÃO ÚNICO</span>
                        <div class="auth-code">${pt[2]}</div>
                    </div>

                    <div class="cert-body" style="font-size:16px;">
                        Data de Emissão: ${new Date().toLocaleDateString('pt-BR')}<br>
                        Identificador Digital: #Q${Math.floor(Math.random() * 1000000)}
                    </div>

                    <div class="footer-sign">
                        <div class="sign-line">Assinatura do Responsável</div>
                        <div class="sign-line">Carimbo da Empresa</div>
                    </div>
                </div>`;
        });
        document.getElementById('lista_historico').innerHTML = h_tela + h_cert;
    }

    function toggleCert(i) {
        document.getElementById('row-'+i).classList.toggle('selected');
        const c = document.getElementById('cert-'+i);
        c.style.setProperty('display', (c.style.display==='flex'?'none':'flex'), 'important');
    }

    async function gerar() {
        const p = document.getElementById('pin_cli').value;
        const res = await fetch('/v1/cliente/gerar', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({pin:p, obs:document.getElementById('obs').value || "PADRÃO"})});
        if(res.ok) entrar(); else alert("Limite atingido!");
    }

    async function listar() {
        const k = document.getElementById('mestre').value;
        const res = await fetch('/admin/listar?key=' + k);
        const dados = await res.json();
        let h = `<table style="width:100%; border-collapse:collapse; margin-top:20px;">
            <tr style="background:#1e293b; color:var(--blue)"><th>Empresa</th><th>PIN (8 car.)</th><th>Ações</th></tr>`;
        dados.forEach(c => {
            h += `<tr style="border-bottom: 1px solid #334155;">
                <td>${c.n}</td>
                <td><input type="text" value="${c.p}" id="pin-${c.p}" style="width:100px; padding:5px;"></td>
                <td>
                    <button class="btn" style="background:var(--blue); font-size:10px;" onclick="mudarPin('${c.p}')">Salvar PIN</button>
                    <button class="btn" style="background:var(--red); font-size:10px;" onclick="del('${c.p}')">Remover</button>
                </td>
            </tr>`;
        });
        document.getElementById('lista_admin').innerHTML = h + "</table>";
    }

    async function mudarPin(p_antigo) {
        const np = document.getElementById('pin-'+p_antigo).value;
        await fetch('/admin/mudar-pin', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({key:document.getElementById('mestre').value, pin_antigo:p_antigo, pin_novo:np})});
        alert("PIN Atualizado!"); listar();
    }
    </script>
</body>
</html>