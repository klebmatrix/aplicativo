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
    <title>SISTEMA QUANTUM | REGISTRO</title>
    <style>
        /* INTERFACE TOTALMENTE BRANCA */
        body { background-color: #f4f7f6 !important; color: #1a1a1a !important; font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 20px; }
        .container { max-width: 850px; margin: auto; background: #ffffff; padding: 40px; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); border: 1px solid #e0e0e0; }
        
        h1 { color: #0f172a; text-align: center; margin-bottom: 30px; }
        label { display: block; margin-bottom: 8px; font-weight: bold; color: #444; }
        input { padding: 12px; border: 1px solid #ccc; border-radius: 6px; width: 100%; box-sizing: border-box; margin-bottom: 20px; font-size: 16px; }
        
        .btn { padding: 14px; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 16px; width: 100%; transition: 0.3s; }
        .btn-azul { background: #2563eb; color: white; }
        .btn-azul:hover { background: #1d4ed8; }
        
        .hist-item { border: 1px solid #eee; padding: 20px; margin-top: 15px; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; background: #fff; }
        .btn-imprimir { background: #000; color: white; padding: 8px 15px; border-radius: 4px; width: auto; font-size: 13px; }

        /* CONFIGURAÇÃO DO CERTIFICADO A4 (SÓ APARECE NA IMPRESSÃO) */
        .certificado-a4 { display: none; }

        @media print {
            @page { size: A4; margin: 0; }
            .no-print { display: none !important; }
            body { background: white !important; padding: 0 !important; margin: 0 !important; }
            .container { border: none !important; box-shadow: none !important; width: 100% !important; max-width: 100% !important; }
            
            /* MOSTRA APENAS O CERTIFICADO QUE ESTÁ SENDO IMPRESSO NO MOMENTO */
            .certificado-a4.print-focus { 
                display: flex !important; 
                flex-direction: column; 
                justify-content: center; 
                align-items: center;
                width: 210mm; 
                height: 297mm; 
                border: 20px double #000 !important; 
                padding: 30mm; 
                box-sizing: border-box; 
                text-align: center;
                background: white !important;
            }
            .cert-title { font-size: 38px; font-weight: bold; margin-bottom: 10px; }
            .cert-line { border-top: 2px solid #000; width: 100%; margin: 20px 0; }
            .auth-box { border: 1px solid #000; padding: 20px; margin: 40px 0; width: 90%; }
            .footer-sign { margin-top: 80px; width: 100%; display: flex; justify-content: space-around; }
        }
    </style>
</head>
<body>
    <div class="container no-print">
        <div id="login_area">
            <h1>ÁREA DO CLIENTE</h1>
            <label>Senha de Acesso (8 caracteres)</label>
            <input type="password" id="senha_cli" placeholder="Digite sua senha" maxlength="8">
            <button class="btn btn-azul" onclick="entrar()">ENTRAR NO SISTEMA</button>
        </div>

        <div id="dashboard" style="display:none;">
            <h2 id="emp_nome" style="border-bottom: 2px solid #f0f0f0; padding-bottom: 10px;"></h2>
            
            <div style="margin: 30px 0;">
                <label>Registrar Novo Produto</label>
                <div style="display:flex; gap:10px;">
                    <input type="text" id="obs" placeholder="Ex: Módulo Pro v2.0" style="margin:0;">
                    <button class="btn btn-azul" style="width:200px;" onclick="gerar()">GERAR</button>
                </div>
            </div>

            <h3 style="margin-top:40px;">Histórico de Registros</h3>
            <div id="lista_historico"></div>
        </div>
    </div>

    <div id="area_certificados"></div>

    <script>
    async function entrar() {
        const s = document.getElementById('senha_cli').value;
        const res = await fetch('/v1/cliente/dados?pin=' + s);
        if(!res.ok) return alert("Senha Inválida!");
        const d = await res.json();
        
        document.getElementById('login_area').style.display='none';
        document.getElementById('dashboard').style.display='block';
        document.getElementById('emp_nome').innerText = d.empresa;
        
        let h_tela = ""; let h_cert = "";
        [...d.hist].reverse().forEach((t, i) => {
            const pt = t.split(' | '); 
            h_tela += `
                <div class="hist-item">
                    <div>
                        <strong>${pt[1]}</strong><br>
                        <small style="color:#666">${pt[0]}</small>
                    </div>
                    <button class="btn btn-imprimir" onclick="imprimirSoEste(${i})">IMPRIMIR A4</button>
                </div>`;
            
            h_cert += `
                <div class="certificado-a4" id="cert-${i}">
                    <div class="cert-title">CERTIFICADO</div>
                    <div style="letter-spacing:5px; font-weight:bold;">AUTENTICIDADE DE SOFTWARE</div>
                    <div class="cert-line"></div>
                    <p style="font-size:22px;">Atestamos que o produto abaixo foi registrado com sucesso:</p>
                    <h2 style="font-size:32px; text-transform:uppercase;">${pt[1]}</h2>
                    
                    <div class="auth-box">
                        <small>CÓDIGO DE VALIDAÇÃO ÚNICO</small>
                        <div style="font-family:monospace; font-size:26px; font-weight:bold; margin-top:10px;">${pt[2]}</div>
                    </div>

                    <p><strong>REGISTRADO EM:</strong> ${pt[0]}</p>
                    <div class="footer-sign">
                        <div style="border-top:1px solid #000; width:220px; padding-top:10px;">Assinatura do Responsável</div>
                        <div style="border-top:1px solid #000; width:220px; padding-top:10px;">Carimbo da Empresa</div>
                    </div>
                </div>`;
        });
        document.getElementById('lista_historico').innerHTML = h_tela;
        document.getElementById('area_certificados').innerHTML = h_cert;
    }

    function imprimirSoEste(i) {
        // Remove foco de qualquer outro certificado
        document.querySelectorAll('.certificado-a4').forEach(c => c.classList.remove('print-focus'));
        
        // Aplica foco apenas no selecionado
        const cert = document.getElementById('cert-'+i);
        cert.classList.add('print-focus');
        
        // Dispara a impressão
        window.print();
    }

    async function gerar() {
        const s = document.getElementById('senha_cli').value;
        const obs = document.getElementById('obs').value || "PRODUTO";
        await fetch('/v1/cliente/gerar', {
            method:'POST', 
            headers:{'Content-Type':'application/json'}, 
            body:JSON.stringify({pin:s, obs:obs})
        });
        entrar();
    }
    </script>
</body>
</html>