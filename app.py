import os, secrets, string, psycopg2, datetime
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

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
        /* ESTILO TOTAL BRANCO */
        :root { --blue: #2563eb; --border: #e2e8f0; --text: #1e293b; --bg: #ffffff; }
        
        body { background: var(--bg); color: var(--text); font-family: 'Segoe UI', system-ui, sans-serif; padding: 20px; margin: 0; }
        .container { max-width: 1000px; margin: auto; background: white; padding: 30px; border-radius: 12px; border: 1px solid var(--border); box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        
        /* BOTÕES E INPUTS LIMPOS */
        input { padding: 12px; background: white; border: 1px solid var(--border); color: black; border-radius: 8px; margin-bottom: 5px; width: 100%; box-sizing: border-box; }
        .btn { padding: 12px 20px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; transition: 0.2s; }
        .btn-blue { background: var(--blue); color: white; }
        .btn-gray { background: #f1f5f9; color: #475569; border: 1px solid var(--border); }
        
        /* DASHBOARD */
        .hist-item { background: #f8fafc; padding: 15px; margin-top: 10px; border-radius: 10px; display: flex; justify-content: space-between; cursor: pointer; border: 1px solid var(--border); }
        .hist-item.selected { border-color: var(--blue); background: #eff6ff; }

        /* --- LAYOUT A4 DE IMPRESSÃO --- */
        .certificado-a4 { display: none; }

        @media print {
            @page { size: A4; margin: 0; }
            .no-print { display: none !important; }
            body { background: white !important; color: black !important; }
            .container { border: none !important; box-shadow: none !important; max-width: 100%; width: 100%; }
            
            .certificado-a4 { 
                display: flex !important;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                width: 210mm;
                height: 297mm;
                padding: 40mm;
                box-sizing: border-box;
                border: 20px double #000;
                position: relative;
                page-break-after: always;
                text-align: center;
                margin: 0 auto;
            }
            .cert-stamp { position: absolute; top: 60mm; right: 40mm; border: 4px solid #000; padding: 10px; font-weight: bold; transform: rotate(15deg); opacity: 0.4; }
            .cert-title { font-size: 42px; font-weight: bold; text-transform: uppercase; margin-bottom: 20px; border-bottom: 4px solid #000; }
            .cert-body { font-size: 24px; line-height: 1.8; margin-bottom: 50px; }
            .auth-box { border: 3px solid #000; padding: 30px; background: #f9f9f9; margin-bottom: 60px; }
            .auth-code { font-family: 'Courier New', monospace; font-size: 32px; font-weight: bold; letter-spacing: 5px; }
            .footer-sign { margin-top: 100px; width: 100%; display: flex; justify-content: space-around; }
            .sign-line { border-top: 2px solid #000; width: 250px; font-size: 14px; padding-top: 10px; }
        }
    </style>
</head>
<body>
    <div class="container">
        {% if tipo == 'admin' %}
            <h1 style="color:black; border-bottom: 2px solid var(--blue); padding-bottom: 10px;">GESTOR MESTRE</h1>
            <div class="no-print" style="background: #f8fafc; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                <input type="password" id="mestre" placeholder="Chave Admin" style="width: 70%;">
                <button class="btn btn-blue" onclick="listar()">CARREGAR CLIENTES</button>
            </div>
            <div id="lista_admin"></div>

        {% else %}
            <div id="login_area" style="text-align:center; padding: 100px 0;">
                <h1 style="font-size:40px; color: black;">QUANTUM AUTH</h1>
                <p>Acesse com sua senha de 6 a 8 dígitos</p>
                <input type="password" id="pin_cli" placeholder="Digite sua senha" minlength="6" maxlength="8" style="width:300px; text-align:center; font-size:22px;">
                <br><br>
                <button class="btn btn-blue" style="width:300px;" onclick="entrar()">ENTRAR NO SISTEMA</button>
            </div>

            <div id="dashboard" style="display:none;">
                <div style="display:flex; justify-content:space-between; align-items:center; border-bottom: 1px solid var(--border); padding-bottom: 15px;">
                    <h2 id="emp_nome" style="color:var(--blue); margin: 0;"></h2>
                    <button class="btn btn-gray no-print" onclick="window.print()">🖨️ IMPRIMIR CERTIFICADOS SELECIONADOS</button>
                </div>

                <div class="no-print" style="margin:20px 0; background:#f8fafc; padding:20px; border-radius:10px; border: 1px solid var(--border);">
                    <div style="display:flex; gap: 10px;">
                        <input type="text" id="obs" placeholder="Referência (Ex: Lote Software X)">
                        <button class="btn btn-blue" style="white-space:nowrap;" onclick="gerar()">GERAR NOVO</button>
                    </div>
                </div>

                <div id="lista_historico"></div>
            </div>
        {% endif %}
    </div>

    <script>
    async function entrar() {
        const p = document.getElementById('pin_cli').value;
        if(p.length < 6) return alert("A senha deve ter no mínimo 6 dígitos!");
        
        const res = await fetch('/v1/cliente/dados?pin=' + p);
        if(!res.ok) return alert("Acesso Negado!");
        const d = await res.json();
        
        document.getElementById('login_area').style.display='none';
        document.getElementById('dashboard').style.display='block';
        document.getElementById('emp_nome').innerText = d.empresa;
        
        atualizarTela(d);
    }

    function atualizarTela(d) {
        let h_tela = ""; let h_cert = "";
        [...d.hist].reverse().forEach((t, i) => {
            const pt = t.split(' | ');
            h_tela += `<div class="hist-item no-print" id="row-${i}" onclick="toggleCert(${i})">
                <span><b>${pt[1]}</b><br><small style="color:gray">${pt[0]}</small></span> 
                <span style="font-family:monospace; color:var(--blue); font-weight:bold;">${pt[2]}</span>
            </div>`;
            
            h_cert += `
                <div class="certificado-a4" id="cert-${i}">
                    <div class="cert-stamp">VALIDADO E<br>ORIGINAL</div>
                    <div class="cert-title">Certificado</div>
                    <div style="letter-spacing: 5px; color: #555; margin-bottom: 60px;">DE AUTENTICIDADE</div>
                    <div class="cert-body">
                        Certificamos que a licença referente ao módulo<br>
                        <strong>${pt[1]}</strong> foi autenticada<br>
                        com sucesso em nossa rede Quantum.
                    </div>
                    <div class="auth-box">
                        <span style="font-size:14px;">CÓDIGO DE AUTENTICAÇÃO</span>
                        <div class="auth-code">${pt[2]}</div>
                    </div>
                    <div class="cert-body" style="font-size:16px;">Data de Emissão: ${pt[0]}</div>
                    <div class="footer-sign">
                        <div class="sign-line">Responsável</div>
                        <div class="sign-line">Carimbo</div>
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
        const res = await fetch('/v1/cliente/gerar', {
            method:'POST', 
            headers:{'Content-Type':'application/json'}, 
            body:JSON.stringify({pin:p, obs:document.getElementById('obs').value || "GERAL"})
        });
        if(res.ok) entrar(); else alert("Erro ao gerar ou limite atingido!");
    }

    async function listar() {
        const k = document.getElementById('mestre').value;
        const res = await fetch('/admin/listar?key=' + k);
        const dados = await res.json();
        let h = `<table style="width:100%; border-collapse:collapse; margin-top:20px;">
            <tr style="background:#f1f5f9; text-align:left;">
                <th style="padding:15px; border-bottom:2px solid var(--border)">Empresa</th>
                <th style="padding:15px; border-bottom:2px solid var(--border)">Senha</th>
                <th style="padding:15px; border-bottom:2px solid var(--border)">Ações</th>
            </tr>`;
        dados.forEach(c => {
            h += `<tr>
                <td style="padding:15px; border-bottom:1px solid var(--border)">${c.n}</td>
                <td style="padding:15px; border-bottom:1px solid var(--border)">
                    <input type="text" value="${c.p}" id="pin-${c.p}" style="width:120px; margin:0; padding:5px;">
                </td>
                <td style="padding:15px; border-bottom:1px solid var(--border)">
                    <button class="btn btn-blue" style="font-size:12px; padding:5px 10px;" onclick="mudarPin('${c.p}')">Salvar</button>
                </td>
            </tr>`;
        });
        document.getElementById('lista_admin').innerHTML = h + "</table>";
    }

    async function mudarPin(p_antigo) {
        const np = document.getElementById('pin-'+p_antigo).value;
        if(np.length < 6 || np.length > 8) return alert("A senha deve ter entre 6 e 8 dígitos!");
        await fetch('/admin/mudar-pin', {
            method:'POST', 
            headers:{'Content-Type':'application/json'}, 
            body:JSON.stringify({key:document.getElementById('mestre').value, pin_antigo:p_antigo, pin_novo:np})
        });
        alert("Senha Atualizada!"); 
        listar();
    }
    </script>
</body>
</html>