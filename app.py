import os
import secrets
import string
import psycopg2
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

ADMIN_KEY = os.environ.get('ADMIN_KEY', 'ADMIN123')

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
    <title>SISTEMA QUANTUM | v2.0</title>
    <style>
        body { background: #0b1120; color: white; font-family: sans-serif; padding: 20px; }
        .container { max-width: 800px; margin: auto; background: #1e293b; padding: 25px; border-radius: 15px; border: 1px solid #334155; }
        h1 { color: #38bdf8; text-align: center; }
        input { padding: 12px; margin: 10px 0; background: #0f172a; border: 1px solid #444; color: white; border-radius: 5px; width: 90%; }
        
        /* ESTILO DO HISTÓRICO COM SELEÇÃO */
        .hist-item { 
            background: #0f172a; padding: 15px; margin-bottom: 10px; border-radius: 8px;
            display: flex; align-items: center; border: 2px solid transparent; transition: 0.3s;
        }
        .hist-item.selected { border-color: #38bdf8; background: #1e293b; }
        .marcador { width: 22px; height: 22px; margin-right: 15px; cursor: pointer; }
        
        .btn { padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; margin: 5px; }
        .btn-gerar { background: #22c55e; width: 100%; font-size: 1.2rem; margin-top: 10px; }
        .btn-export { background: #0284c7; }
        .btn-print { background: #64748b; }
        
        .menu-acoes { background: #0f172a; padding: 15px; border-radius: 10px; margin: 20px 0; display: flex; justify-content: space-between; align-items: center; }

        /* REGRAS DE IMPRESSÃO - SÓ MOSTRA O QUE FOI MARCADO */
        @media print {
            body { background: white !important; color: black !important; }
            .no-print, button, input, .menu-acoes { display: none !important; }
            .container { border: none; width: 100%; }
            .hist-item { border: 1px solid #000 !important; color: black !important; }
            .hist-item:not(.selected) { display: none !important; } /* AQUI O FILTRO DE IMPRESSÃO */
            .marcador { display: none !important; }
        }
    </style>
</head>
<body>
    <div class="container">
        {% if tipo == 'admin' %}
            <h1>ADMIN PAINEL</h1>
            <input type="password" id="mestre" placeholder="Chave Mestra">
            <button class="btn btn-export" onclick="listar()">LISTAR CLIENTES</button>
            <hr>
            <input type="text" id="n" placeholder="Empresa">
            <input type="text" id="p" placeholder="PIN (6 dígitos)" maxlength="6">
            <input type="number" id="l" placeholder="Créditos" value="10">
            <button class="btn btn-gerar" onclick="add()">ATIVAR AGORA</button>
            <div id="lista_admin"></div>
        {% else %}
            <div id="login_area">
                <h1>LOGIN QUANTUM</h1>
                <input type="text" id="pin" placeholder="DIGITE SEU PIN DE 6 DÍGITOS" maxlength="6">
                <button class="btn btn-export" style="width:95%" onclick="entrar()">ENTRAR NO SISTEMA</button>
            </div>

            <div id="dashboard" style="display:none;">
                <h1 id="boas_vindas"></h1>
                <div class="menu-acoes">
                    <div>
                        <p>Saldo: <b id="uso">0</b> / <b id="total">0</b></p>
                    </div>
                    <div>
                        <button class="btn btn-print" onclick="window.print()">🖨️ IMPRIMIR MARCADOS</button>
                        <button class="btn btn-export" onclick="exportarExcel()">📊 EXCEL MARCADOS</button>
                    </div>
                </div>

                <input type="text" id="obs" placeholder="Observação para esta chave...">
                <button class="btn btn-gerar" onclick="gerar()">GERAR NOVA CHAVE</button>
                
                <h3 style="margin-top:30px">Histórico de Chaves:</h3>
                <div style="margin-bottom:10px">
                    <input type="checkbox" id="check_todos" onclick="selecionarTudo(this)"> Selecionar Todos
                </div>
                <div id="lista_historico"></div>
            </div>
        {% endif %}
    </div>

    <script>
        let pinAtivo = "";

        // Garante que o PIN tenha apenas números e 6 dígitos
        document.querySelectorAll('input[placeholder*="PIN"]').forEach(input => {
            input.oninput = () => input.value = input.value.replace(/[^0-9]/g, '');
        });

        async function entrar() {
            pinAtivo = document.getElementById('pin').value;
            if(pinAtivo.length !== 6) return alert("O PIN deve ter 6 dígitos!");
            const r = await fetch('/v1/cliente/dados?pin=' + pinAtivo);
            if(r.ok) { carregarDados(); } else { alert("PIN incorreto!"); }
        }

        async function carregarDados() {
            const r = await fetch('/v1/cliente/dados?pin=' + pinAtivo);
            const d = await r.json();
            document.getElementById('login_area').style.display = 'none';
            document.getElementById('dashboard').style.display = 'block';
            document.getElementById('boas_vindas').innerText = d.empresa;
            document.getElementById('uso').innerText = d.usadas;
            document.getElementById('total').innerText = d.limite;
            
            let html = "";
            d.hist.reverse().forEach((txt, i) => {
                html += `
                <div class="hist-item" id="row-${i}">
                    <input type="checkbox" class="marcador" onchange="marcarLinha(this, 'row-${i}')" data-info="${txt}">
                    <div style="flex-grow:1">${txt}</div>
                    <button class="btn btn-print" style="padding:5px" onclick="navigator.clipboard.writeText('${txt.split(' | ')[2]}');alert('Copiado!')">COPY</button>
                </div>`;
            });
            document.getElementById('lista_historico').innerHTML = html;
        }

        function marcarLinha(cb, id) {
            if(cb.checked) document.getElementById(id).classList.add('selected');
            else document.getElementById(id).classList.remove('selected');
        }

        function selecionarTudo(source) {
            document.querySelectorAll('.marcador').forEach(cb => {
                cb.checked = source.checked;
                marcarLinha(cb, cb.parentElement.id);
            });
        }

        async function gerar() {
            const obs = document.getElementById('obs').value || "GERAL";
            await fetch('/v1/cliente/gerar', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ pin: pinAtivo, obs: obs })
            });
            carregarDados();
        }

        function exportarExcel() {
            const marcados = document.querySelectorAll('.marcador:checked');
            if(marcados.length === 0) return alert("Selecione as chaves primeiro!");
            
            let csv = "DATA | OBS | CHAVE\\n";
            marcados.forEach(m => csv += m.getAttribute('data-info') + "\\n");
            
            const blob = new Blob([csv], { type: 'text/csv' });
            const a = document.createElement('a');
            a.href = URL.createObjectURL(blob);
            a.download = `Chaves_Quantum_${pinAtivo}.csv`;
            a.click();
        }

        // Funções Admin
        async function add() {
            const p = document.getElementById('p').value;
            if(p.length !== 6) return alert("PIN deve ter 6 dígitos!");
            await fetch('/admin/cadastrar', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({key: document.getElementById('mestre').value, n: document.getElementById('n').value, p: p, l: document.getElementById('l').value})
            });
            listar();
        }

        async function listar() {
            const res = await fetch('/admin/listar?key=' + document.getElementById('mestre').value);
            const dados = await res.json();
            let h = "<table border='1' style='width:100%; margin-top:20px'><tr><th>Empresa</th><th>PIN</th></tr>";
            dados.forEach(c => h += `<tr><td>${c.n}</td><td>${c.p}</td></tr>`);
            document.getElementById('lista_admin').innerHTML = h + "</table>";
        }
    </script>
</body>
</html>
"""

# ... (Manter as rotas Flask do @app.route exatamente como o código anterior)