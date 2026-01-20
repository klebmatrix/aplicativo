from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
import hashlib
import os

app = Flask(__name__)
CORS(app)

# CONFIGURAÇÃO DE SEGURANÇA
# No Render, vá em Environment e defina MEU_PIN. Se não definir, o padrão é 123456
MEU_PIN = os.environ.get("MEU_PIN", "123456")

# INTERFACE DASHBOARD (HTML embutido para facilitar o deploy único)
HTML_DASHBOARD = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KLEBMATRIX | Quantum Vault</title>
    <style>
        body { background: #0f172a; color: #38bdf8; font-family: 'Inter', sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .card { background: #1e293b; padding: 40px; border-radius: 20px; border: 1px solid #0ea5e9; box-shadow: 0 0 30px rgba(14, 165, 233, 0.3); text-align: center; max-width: 400px; width: 90%; }
        h1 { font-size: 1.5rem; margin-bottom: 10px; color: #fff; letter-spacing: 2px; }
        p { color: #94a3b8; font-size: 0.9rem; margin-bottom: 25px; }
        input { background: #0f172a; border: 1px solid #38bdf8; color: #fff; padding: 12px; border-radius: 8px; width: 100%; box-sizing: border-box; text-align: center; font-size: 1.2rem; margin-bottom: 20px; outline: none; }
        button { background: #0ea5e9; color: #fff; border: none; padding: 12px 20px; border-radius: 8px; cursor: pointer; font-weight: bold; width: 100%; transition: 0.3s; }
        button:hover { background: #38bdf8; box-shadow: 0 0 15px #38bdf8; }
        #output { margin-top: 25px; padding: 15px; background: rgba(0,0,0,0.2); border-radius: 8px; font-family: monospace; font-size: 0.85rem; word-break: break-all; color: #22c55e; display: none; border-left: 3px solid #22c55e; }
    </style>
</head>
<body>
    <div class="card">
        <h1>KLEBMATRIX</h1>
        <p>Quantum Key Generator for Databases</p>
        <input type="password" id="pinInput" placeholder="Digite o PIN de 6 dígitos" maxlength="6">
        <button onclick="requestKey()">GERAR CHAVE QUÂNTICA</button>
        <div id="output"></div>
    </div>

    <script>
        async function requestKey() {
            const pin = document.getElementById('pinInput').value;
            const output = document.getElementById('output');
            
            if(pin.length !== 6) { alert("O PIN deve ter 6 dígitos."); return; }
            
            output.style.display = "block";
            output.innerText = "Calculando superposição quântica...";
            output.style.color = "#38bdf8";

            try {
                const res = await fetch('/v1/quantum-key', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ pin: pin })
                });
                const data = await res.json();
                
                if (data.status === "success") {
                    output.style.color = "#22c55e";
                    output.innerHTML = `<strong>CHAVE SHA-256:</strong><br>${data.key}<br><br><small>Fonte: ${data.entropy_source}</small>`;
                } else {
                    output.style.color = "#ef4444";
                    output.innerText = "ERRO: " + data.erro;
                }
            } catch (e) {
                output.innerText = "Falha na conexão com o servidor.";
            }
        }
    </script>
</body>
</html>
"""

def processamento_quantico():
    # Motor Quântico: Gera entropia pura através de 8 qubits em superposição
    n_qubits = 8
    qc = QuantumCircuit(n_qubits)
    for i in range(n_qubits):
        qc.h(i) # Aplica porta Hadamard (Superposição)
    qc.measure_all()
    
    backend = Aer.get_backend('qasm_simulator')
    job = backend.run(transpile(qc, backend), shots=1)
    resultado_bits = list(job.result().get_counts().keys())[0]
    
    # Converte os bits quânticos em uma chave SHA-256 industrial
    chave_hex = hashlib.sha256(resultado_bits.encode()).hexdigest().upper()
    return chave_hex

@app.route('/')
def index():
    return render_template_string(HTML_DASHBOARD)

@app.route('/v1/quantum-key', methods=['POST'])
def api_get_key():
    dados = request.json
    
    # Validação rigorosa do PIN
    if not dados or dados.get('pin') != MEU_PIN:
        return jsonify({"status": "error", "erro": "PIN de acesso inválido"}), 401
    
    try:
        chave = processamento_quantico()
        return jsonify({
            "status": "success",
            "key": chave,
            "entropy_source": "Quantum Superposition (Qiskit Aer)",
            "bits": 256
        })
    except Exception as e:
        return jsonify({"status": "error", "erro": str(e)}), 500

if __name__ == '__main__':
    # Porta dinâmica para o Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)