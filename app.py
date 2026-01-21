import os
import secrets
import string
import psycopg2
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

ADMIN_KEY = os.environ.get('ADMIN_KEY', 'ADMIN123')

def get_db_connection():
    url = os.environ.get('DATABASE_URL')
    if url and url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    try:
        return psycopg2.connect(url, sslmode='require')
    except Exception as e:
        print(f"Erro no Banco: {e}")
        return None

def generate_quantum_key(length=30):
    chars = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))

HTML_SISTEMA = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>KEYQUANTUM | VISUALIZAÇÃO DIRETA</title>
    <style>
        :root { --blue: #38bdf8; --dark: #0b1120; --card: #1e293b; --input: #0f172a; }
        body { background: var(--dark); color: white; font-family: sans-serif; padding: 20px; }
        .container { max-width: 800px; margin: auto; background: var(--card); padding: 25px; border-radius: 15px; border: 1px solid #334155; }
        
        /* ESTILO DA LISTA SEM DATA/HORA */
        .hist-item { 
            background: var(--input); padding: 15px; margin-top: 8px; border-radius: 8px; 
            display: flex; align-items: center; border: 2px solid transparent; 
        }
        .hist-item.selected { border-color: var(--blue); background: #162e45; }
        .marcador { width: 22px; height: 22px; margin-right: 15px; cursor: pointer; }
        
        .label-obs { color: var(--blue); font-weight: bold; margin-right: 10px; min-width: 100px; }
        .key-txt { font-family: monospace; color: #cbd5e1; flex-grow: 1; }

        input { padding: 12px; margin: 10px 0; background: var(--input); border: 1px solid #334155; color: white; border-radius: 8px; width: 90%; }
        button { padding: 10px 20px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; color: white; }
        .btn-green { background: #22c55e; width: 100%; margin-top: 10px; }
        .btn-blue { background: #0284c7; }

        @media print {
            body { background: white !important; color: black !important; }
            button, input, h1, .btn-green { display: none !important; }
            .hist-item:not(.selected) { display: none !important; }
            .hist-item { border: 1px solid #000 !important; color: black !important; }
            .marcador { display: none !important; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div id="login_area">
            <h1>SISTEMA QUANTUM</h1>
            <input type="text" id="pin" placeholder="PIN (6 DÍGITOS)" maxlength="6">
            <button class="btn-blue" style="width:95%" onclick="entrar()">ACESSAR</button>
        </div>

        <div id="dashboard" style="display:none;">
            <h2 id="emp_nome" style="color: var(--blue);"></h2>
            <div style="display:flex; justify-content:space-between; margin-bottom:20px;">
                <span>Créditos: <b id="uso">0</b> / <b id="total">0</b></span>
                <div>
                    <button class="btn" style="background:#475569" onclick="window.print()">🖨️ IMPRIMIR</button>
                    <button class="btn btn-blue" onclick="exportarExcel()">📊 EXCEL</button>
                </div>
            </div>

            <input type="text" id="obs" placeholder="Nome do Lote / Cliente / Observação">
            <button class="btn btn-green" onclick="gerar()">GERAR CHAVE AGORA</button>
            
            <div style="margin-top:20px;"><label><input type="checkbox" onclick="selTudo(this)"> Selecionar Todas</label></div>
            <div id="lista_historico"></div>
        </div>
    </div>

    <script>
        let pinAtivo = "";

        // Bloqueia letras no PIN de 6 dígitos
        document.querySelectorAll('input[placeholder*="PIN"]').forEach(el => {
            el.oninput = () => el.value = el.value.replace(/[^0-9]/g, '').slice(0,6);
        });

        async function entrar() {
            pinAtivo = document.getElementById('pin').value;
            if(pinAtivo.length !== 6) return alert("PIN de 6 dígitos!");
            const res = await fetch('/v1/cliente/dados?pin=' + pinAtivo);
            if(res.ok) { 
                document.getElementById('login_area').style.display='none';
                document.getElementById('dashboard').style.display='block';
                atualizar(); 
            } else { alert("PIN Inválido!"); }
        }

        async function atualizar() {
            const res = await fetch('/v1/cliente/dados?pin=' + pinAtivo);
            const d = await res.json();
            document.getElementById('emp_nome').innerText = d.empresa;
            document.getElementById('uso').innerText = d.usadas;
            document.getElementById('total').innerText = d.limite;
            
            let html = "";
            d.hist.reverse().forEach((txt, i) => {
                const partes = txt.split(' | ');
                // partes[0] era data, partes[1] é obs, partes[2] é chave
                // Ajustado para mostrar apenas Obs e Chave
                const exibicao = `<span class="label-obs">${partes[1]}</span> <span class="key-txt">${partes[2]}</span>`;
                
                html += `
                <div class="hist-item" id="row-${i}">
                    <input type="checkbox" class="marcador" onchange="toggleRow(this, 'row-${i}')" data-info="${partes[1]};${partes[2]}">
                    ${exibicao}
                </div>`;
            });
            document.getElementById('lista_historico').innerHTML = html;
        }

        function toggleRow(cb, id) {
            document.getElementById(id).classList.toggle('selected', cb.checked);
        }

        function selTudo(source) {
            document.querySelectorAll('.marcador').forEach(cb => {
                cb.checked = source.checked;
                toggleRow(cb, cb.parentElement.id);
            });
        }

        async function gerar() {
            const obsInput = document.getElementById('obs').value || "SEM OBS";
            await fetch('/v1/cliente/gerar', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ pin: pinAtivo, obs: obsInput })
            });
            atualizar();
            document.getElementById('obs').value = "";
        }

        function exportarExcel() {
            const marcados = document.querySelectorAll('.marcador:checked');
            if(marcados.length === 0) return alert("Selecione os itens!");
            let csv = "OBSERVACAO;CHAVE\\n";
            marcados.forEach(m => csv += m.getAttribute('data-info') + "\\n");
            const blob = new Blob([csv], { type: 'text/csv' });
            const a = document.createElement('a');
            a.href = URL.createObjectURL(blob);
            a.download = "relatorio_quantum.csv";
            a.click();
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home(): return render_template_string(HTML_SISTEMA)

@app.route('/v1/cliente/dados')
def get_dados():
    pin = request.args.get('pin')
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT nome_empresa, acessos, limite, historico_chaves FROM clientes WHERE pin_hash = %s", (pin,))
    c = cur.fetchone(); cur.close(); conn.close()
    if c: return jsonify({"empresa": c[0], "usadas": c[1], "limite": c[2], "hist": c[3]})
    return jsonify({"erro": "n"}), 404

@app.route('/v1/cliente/gerar', methods=['POST'])
def gerar_api():
    d = request.json
    pin = d.get('pin')
    obs = d.get('obs', 'GERAL').upper()
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT acessos, limite FROM clientes WHERE pin_hash = %s", (pin,))
    c = cur.fetchone()
    if c and c[0] < c[1]:
        nk = generate_quantum_key(30)
        # Salvamos agora sem a data e hora, apenas OBS e CHAVE
        reg = f"DATA_REMOVIDA | {obs} | {nk}"
        cur.execute("UPDATE clientes SET acessos=acessos+1, historico_chaves=array_append(historico_chaves, %s) WHERE pin_hash=%s", (reg, pin))
        conn.commit(); cur.close(); conn.close()
        return jsonify({"key": nk})
    return jsonify({"erro": "saldo"}), 403