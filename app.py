UI_FINAL = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QUANTUM SEED - SISTEMA VIBRACIONAL</title>
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Montserrat:wght@300;400;600&display=swap" rel="stylesheet">
    <style>
        :root { --gold: #c5a059; --gold-dark: #8e6d2f; --bg: #05070a; --glass: rgba(255, 255, 255, 0.03); }
        
        * { box-sizing: border-box; }
        body { background: var(--bg); color: #e2e8f0; font-family: 'Montserrat', sans-serif; margin: 0; overflow-x: hidden; }
        
        /* Interface de Usuário (Dashboard) */
        .no-print { max-width: 1000px; margin: 40px auto; padding: 20px; position: relative; z-index: 10; }
        .glass-card { background: var(--glass); border: 1px solid rgba(197, 160, 89, 0.2); backdrop-filter: blur(10px); border-radius: 20px; padding: 40px; box-shadow: 0 20px 50px rgba(0,0,0,0.5); }
        
        h1, h2, h3 { font-family: 'Cinzel', serif; color: var(--gold); letter-spacing: 2px; text-align: center; }
        
        input { background: rgba(0,0,0,0.4); border: 1px solid #334155; padding: 15px; color: white; border-radius: 10px; width: 100%; margin-bottom: 15px; transition: 0.3s; }
        input:focus { border-color: var(--gold); outline: none; box-shadow: 0 0 10px rgba(197, 160, 89, 0.3); }
        
        .btn-quantum { background: linear-gradient(135deg, var(--gold), var(--gold-dark)); color: #000; border: none; padding: 15px 30px; border-radius: 10px; font-weight: bold; cursor: pointer; width: 100%; text-transform: uppercase; letter-spacing: 1px; transition: 0.3s; }
        .btn-quantum:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(197, 160, 89, 0.4); }
        
        .history-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 15px; margin-top: 30px; }
        .history-item { background: rgba(255,255,255,0.05); padding: 20px; border-radius: 12px; border-left: 4px solid var(--gold); display: flex; align-items: center; }
        .history-item input { width: 20px; margin-right: 15px; margin-bottom: 0; }

        /* Estilo do Certificado de Impressão */
        #print_area { display: none; }
        @media print {
            .no-print { display: none !important; }
            #print_area { display: block !important; background: #fff; }
            .cert-page { height: 100vh; page-break-after: always; display: flex; justify-content: center; align-items: center; background: white; padding: 40px; position: relative; }
            .cert-border { border: 15px solid #1a1a1a; width: 90%; height: 90%; padding: 40px; position: relative; border-image: url('https://www.transparenttextures.com/patterns/gold-glitter.png') 30 stretch; }
            .cert-content { text-align: center; font-family: 'Cinzel', serif; color: #1a1a1a; }
            .cert-gold-txt { color: #8e6d2f; font-size: 14px; letter-spacing: 5px; }
            .cert-main-val { font-size: 45px; margin: 30px 0; border-top: 1px solid #d4af37; border-bottom: 1px solid #d4af37; padding: 20px 0; font-weight: bold; }
            .cert-mantra { font-family: 'Montserrat', sans-serif; font-style: italic; font-size: 20px; color: #444; margin: 40px 0; }
            .cert-footer { position: absolute; bottom: 40px; width: 80%; left: 10%; display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #eee; padding-top: 20px; }
            .qr-box { width: 80px; height: 80px; background: #eee; }
        }
    </style>
</head>
<body>
    <div style="position:fixed; top:0; left:0; width:100%; height:100%; z-index:-1; background: radial-gradient(circle at center, #101827 0%, #05070a 100%); opacity:0.8;"></div>

    <div class="no-print">
        <div class="glass-card">
            {% if modo == 'admin' %}
                <h1>QUANTUM ADMIN CONTROL</h1>
                <input type="password" id="ak" placeholder="CHAVE MASTER DO SISTEMA">
                <button class="btn-quantum" onclick="listar()">Sincronizar Banco de Dados</button>
                <div id="res_adm" style="margin-top:20px"></div>
                
                <div style="margin-top:40px; border-top: 1px solid rgba(197, 160, 89, 0.2); padding-top:20px;">
                    <h3>GERENCIAR PORTAL</h3>
                    <input type="text" id="n" placeholder="Nome do Terapeuta / Empresa">
                    <input type="text" id="p" placeholder="Definir PIN (6-8 caracteres)">
                    <input type="number" id="l" placeholder="Limite de Fluxo (Créditos)">
                    <button class="btn-quantum" onclick="salvar()">Consagrar Acesso</button>
                </div>
            {% else %}
                <div id="view_login">
                    <h1>ACESSO QUÂNTICO</h1>
                    <p style="text-align:center; opacity:0.6">Sintonize sua frequência de acesso</p>
                    <input type="password" id="pin" placeholder="DIGITE SEU PIN">
                    <button class="btn-quantum" onclick="logar()">ENTRAR NO PORTAL</button>
                </div>

                <div id="view_dash" style="display:none;">
                    <h2 id="txt_terapeuta" style="margin-bottom:5px"></h2>
                    <p style="text-align:center; margin-bottom:30px">
                        Fluxo Disponível: <span id="txt_saldo" style="color:var(--gold); font-weight:bold"></span>
                    </p>
                    
                    <div style="background: rgba(255,255,255,0.03); padding:25px; border-radius:15px; margin-bottom:20px">
                        <input type="text" id="obs" placeholder="Nome do Paciente / Intenção da Ativação">
                        <button class="btn-quantum" onclick="gerar()">GERAR NOVA ATIVAÇÃO</button>
                        <button class="btn-quantum" style="background: transparent; border: 1px solid var(--gold); color: var(--gold); margin-top:10px;" onclick="window.print()">IMPRIMIR SELECIONADOS</button>
                    </div>

                    <div style="display:flex; justify-content:space-between; align-items:center; padding:0 10px">
                        <span>Histórico de Ativações</span>
                        <label><input type="checkbox" onclick="toggleAll(this)"> Selecionar Todos</label>
                    </div>
                    <div id="lista_ativações" class="history-grid"></div>
                </div>
            {% endif %}
        </div>
    </div>

    <div id="print_area"></div>

    <script>
        // Funções de Lógica (Mesma estrutura do seu app.py)
        async function logar() {
            const p = document.getElementById('pin').value;
            const res = await fetch(`/api/cli/info?p=${p}`);
            if(!res.ok) return alert("PIN não sintonizado.");
            const d = await res.json();
            document.getElementById('view_login').style.display = 'none';
            document.getElementById('view_dash').style.display = 'block';
            document.getElementById('txt_terapeuta').innerText = d.n;
            document.getElementById('txt_saldo').innerText = `${d.l - d.u} de ${d.l}`;
            
            let html = "";
            d.h.reverse().forEach((item, i) => {
                html += `
                <div class="history-item">
                    <input type="checkbox" class="ck" data-full="${item}">
                    <div>
                        <div style="font-size:12px; color:var(--gold)">${item.split(' | ')[0]}</div>
                        <div style="font-weight:600">${item.split(' | ')[1]}</div>
                        <div style="font-size:11px; opacity:0.6">${item.split(' | ')[2]}</div>
                    </div>
                </div>`;
            });
            document.getElementById('lista_ativações').innerHTML = html;
        }

        async function gerar() {
            const pin = document.getElementById('pin').value;
            const obs = document.getElementById('obs').value;
            const res = await fetch('/api/cli/generate', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({p: pin, o: obs})
            });
            if(res.ok) logar(); else alert("Limite de fluxo atingido.");
        }

        async function listar() {
            const k = document.getElementById('ak').value;
            const res = await fetch(`/api/admin/list?k=${k}`);
            const data = await res.json();
            let h = "<table style='width:100%; margin-top:20px;'><tr><th>Nome</th><th>Fluxo</th><th>Ação</th></tr>";
            data.forEach(c => {
                h += `<tr><td>${c.n}</td><td>${c.u}/${c.l}</td><td><button onclick="excluir('${c.p}')">Excluir</button></td></tr>`;
            });
            document.getElementById('res_adm').innerHTML = h + "</table>";
        }

        async function salvar() {
            const payload = {
                k: document.getElementById('ak').value,
                n: document.getElementById('n').value,
                p: document.getElementById('p').value,
                l: document.getElementById('l').value
            };
            await fetch('/api/admin/save', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload) });
            listar();
        }

        function toggleAll(src) { document.querySelectorAll('.ck').forEach(c => c.checked = src.checked); }

        window.onbeforeprint = () => {
            let h = "";
            document.querySelectorAll('.ck:checked').forEach(c => {
                const p = c.getAttribute('data-full').split(' | ');
                h += `
                <div class="cert-page">
                    <div class="cert-border">
                        <div class="cert-content">
                            <div class="cert-gold-txt">CERTIFICADO DE SINTONIA</div>
                            <h2 style="font-size:30px; margin:10px 0;">ATIVAÇÃO QUÂNTICA</h2>
                            <p style="margin-top:40px">Certificamos que a frequência vibracional de</p>
                            <h3 style="font-size:24px; color:#000;">${p[1]}</h3>
                            <p>foi sintonizada e gravada no campo informacional.</p>
                            
                            <div class="cert-main-val">${p[2]}</div>
                            
                            <div class="cert-mantra">"${p[3]}"</div>
                            
                            <div style="font-size:12px; margin-top:40px;">
                                Validade da Ativação: <strong>${p[4]}</strong><br>
                                <small>Recomenda-se nova sintonização após este período.</small>
                            </div>

                            <div class="cert-footer">
                                <div style="text-align:left">
                                    <small>Autenticidade:</small><br>
                                    <span style="font-family:monospace; font-size:10px;">${Math.random().toString(36).substr(2, 9).toUpperCase()}</span>
                                </div>
                                <div>
                                    <img src="https://api.qrserver.com/v1/create-qr-code/?size=60x60&data=https://www.youtube.com/results?search_query=solfeggio+${p[2].split(' ')[0]}" />
                                </div>
                            </div>
                        </div>
                    </div>
                </div>`;
            });
            document.getElementById('print_area').innerHTML = h;
        };
    </script>
</body>
</html>
"""