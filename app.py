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
    <title>SISTEMA QUANTUM | REGISTRO PROFISSIONAL</title>
    <style>
        /* TELA TOTALMENTE BRANCA - SEM CONFLITOS */
        body { 
            background-color: #ffffff !important; 
            color: #1a1a1a !important; 
            font-family: 'Segoe UI', Arial, sans-serif; 
            margin: 0; 
            padding: 20px; 
        }

        .container { 
            max-width: 850px; 
            margin: auto; 
            background: #ffffff !important; 
            padding: 40px; 
            border-radius: 12px; 
            box-shadow: 0 10px 25px rgba(0,0,0,0.05); 
            border: 1px solid #e2e8f0; 
        }
        
        h1 { color: #0f172a; text-align: center; font-weight: 800; }
        label { display: block; margin-bottom: 8px; font-weight: 600; color: #475569; }
        
        input { 
            padding: 14px; 
            border: 2px solid #e2e8f0; 
            border-radius: 8px; 
            width: 100%; 
            box-sizing: border-box; 
            margin-bottom: 20px; 
            font-size: 16px; 
            background: white !important;
            color: black !important;
        }

        .btn { 
            padding: 15px; 
            border: none; 
            border-radius: 8px; 
            cursor: pointer; 
            font-weight: bold; 
            font-size: 16px; 
            width: 100%; 
            transition: all 0.2s; 
        }

        .btn-principal { background: #000000; color: white; }
        .btn-principal:hover { background: #334155; }

        .hist-item { 
            border: 1px solid #e2e8f0; 
            padding: 20px; 
            margin-top: 15px; 
            border-radius: 10px; 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            background: #f8fafc; 
        }

        .btn-imprimir { 
            background: #2563eb; 
            color: white; 
            padding: 10px 20px; 
            border-radius: 6px; 
            width: auto; 
            font-size: 14px; 
        }

        /* --- CONFIGURAÇÃO DO CERTIFICADO A4 --- */
        .certificado-a4 { display: none; }

        @media print {
            @page { size: A4; margin: 0; }
            .no-print { display: none !important; }
            body { background: white !important; padding: 0 !important; margin: 0 !important; }
            .container { border: none !important; box-shadow: none !important; width: 100% !important; max-width: 100% !important; }
            
            /* SÓ APARECE O QUE ESTIVER COM A CLASSE 'imprimir-agora' */
            .certificado-a4.imprimir-agora { 
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
                color: black !important;
                page-break-after: always;
            }

            .cert-header { font-size: 40px; font-weight: bold; margin-bottom: 5px; }
            .cert-subtitle { font-size: 16px; letter-spacing: 6px; margin-bottom: 40px; font-weight: bold; }
            .cert-box { border: 1px solid #000; padding: 25px; margin: 30px 0; width: 85%; }
            .footer-line { margin-top: 80px; width: 100%; display: flex; justify-content: space-around; }
            .signature { border-top: 1px solid #000; width: 220px; font-size: 12px; padding-top: 8px; }
        }
    </style>
</head>
<body>
    <div class="container no-print">
        <div id="login_area">
            <h1>SISTEMA QUANTUM</h1>
            <label>Senha de Acesso</label>
            <input type="password" id="senha_cli" placeholder="Digite sua senha de 6 dígitos" maxlength="6">
            <button class="btn btn-principal" onclick="entrar()">ENTRAR</button>
        </div>

        <div id="dashboard" style="display:none;">
            <div style="text-align:center; margin-bottom:30px;">
                <h2 id="emp_nome" style="margin:0; color:#2563eb;"></h2>
                <p style="color:#64748b;">Painel de Autenticação de Produtos</p>
            </div>
            
            <div style="background:#f1f5f9; padding:20px; border-radius:10px;">
                <label>Novo Registro (Nome do Produto)</label>
                <div style="display:flex; gap:10px;">
                    <input type="text" id="obs" placeholder="Ex: Software XP" style="margin:0;">
                    <button class="btn btn-principal" style="width:180px;" onclick="gerar()">REGISTRAR</button>
                </div>
            </div>

            <h3 style="margin-top:30px; border-bottom: 2px solid #f1f5f9; padding-bottom: 10px;">Meus Certificados</h3>
            <div id="lista_historico"></div>
        </div>
    </div>

    <div id="area_certificados"></div>

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
            h_tela += `
                <div class="hist-item">
                    <div>
                        <strong style="font-size:18px;">${pt[1]}</strong><br>
                        <small style="color:#64748b">Data: ${pt[0]}</small>
                    </div>
                    <button class="btn btn-imprimir" onclick="imprimirUnico(${i})">IMPRIMIR A4</button>
                </div>`;
            
            h_cert += `
                <div class="certificado-a4" id="cert-${i}">
                    <div class="cert-header">CERTIFICADO</div>
                    <div class="cert-subtitle">DE AUTENTICIDADE ORIGINAL</div>
                    
                    <div style="margin: 40px 0; font-size:22px; line-height:1.6;">
                        Certificamos que o produto/licença:<br>
                        <strong style="font-size:30px; text-transform:uppercase;">${pt[1]}</strong><br>
                        foi autenticado com sucesso e possui garantia de originalidade.
                    </div>
                    
                    <div class="cert-box">
                        <small style="display:block; margin-bottom:10px; font-weight:bold;">CHAVE DE VALIDAÇÃO</small>
                        <div style="font-family:monospace; font-size:24px; font-weight:bold; letter-spacing:2px;">${pt[2]}</div>
                    </div>

                    <p><strong>REGISTRADO EM:</strong> ${pt[0]}</p>

                    <div class="footer-line">
                        <div class="signature">Assinatura Digital Quantum</div>
                        <div class="signature">Carimbo e Selo da Empresa</div>
                    </div>
                </div>`;
        });
        document.getElementById('lista_historico').innerHTML = h_tela;
        document.getElementById('area_certificados').innerHTML = h_cert;
    }

    function imprimirUnico(id) {
        // 1. Remove a marca de impressão de todos os outros
        document.querySelectorAll('.certificado-a4').forEach(c => c.classList.remove('imprimir-agora'));
        
        // 2. Ativa apenas o selecionado
        const cert = document.getElementById('cert-'+id);
        cert.classList.add('imprimir-agora');
        
        // 3. Imprime
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