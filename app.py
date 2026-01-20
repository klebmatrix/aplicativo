# ... (mantenha o início do código igual até as rotas)

# --- NOVA TELA DE ADMINISTRAÇÃO (SÓ VOCÊ SABE O LINK) ---
HTML_ADMIN = """
<!DOCTYPE html>
<html>
<head>
    <title>KLEBMATRIX | Admin</title>
    <style>
        body { background: #000; color: #fff; font-family: sans-serif; padding: 50px; }
        .box { border: 1px solid #22c55e; padding: 20px; max-width: 400px; margin: auto; }
        input { width: 90%; padding: 10px; margin: 10px 0; display: block; }
        button { background: #22c55e; color: #000; padding: 10px; width: 96%; cursor: pointer; border: none; font-weight: bold; }
    </style>
</head>
<body>
    <div class="box">
        <h2>Painel do Kleber</h2>
        <input type="password" id="adm" placeholder="Sua Chave Mestre (ADMIN_KEY)">
        <input type="text" id="emp" placeholder="Nome do Cliente/Empresa">
        <input type="text" id="pin" placeholder="PIN de 6 dígitos" maxlength="6">
        <button onclick="salvar()">CADASTRAR CLIENTE</button>
        <p id="msg"></p>
    </div>
    <script>
        async function salvar() {
            const res = await fetch('/admin/cadastrar', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    admin_key: document.getElementById('adm').value,
                    nome_empresa: document.getElementById('emp').value,
                    pin: document.getElementById('pin').value
                })
            });
            const data = await res.json();
            document.getElementById('msg').innerText = data.status === "sucesso" ? "Cadastrado!" : "Erro: " + data.erro;
        }
    </script>
</body>
</html>
"""

@app.route('/painel-secreto-kleber')
def admin_page():
    return render_template_string(HTML_ADMIN)

# ... (mantenha o restante das rotas /v1/quantum-key e /admin/cadastrar)