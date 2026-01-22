<script>
    // URL AUTOMÁTICA (Detecta se está local ou no Render)
    const API_BASE = window.location.origin;

    // --- FUNÇÕES DE ADMIN (FORÇADAS) ---
    async function listar() {
        const k = document.getElementById('ak').value;
        if(!k) return alert("Digite a Chave Master!");
        
        try {
            const res = await fetch(`${API_BASE}/api/admin/list?k=${k}`, { cache: "no-store" });
            if(!res.ok) throw new Error("Chave Incorreta");
            const data = await res.json();
            
            let h = `<table style="width:100%; border-collapse: collapse; margin-top:20px;">
                        <tr style="background:var(--gold); color:black">
                            <th style="padding:10px">Portador</th>
                            <th style="padding:10px">Uso/Limite</th>
                            <th style="padding:10px">Ação</th>
                        </tr>`;
            data.forEach(c => {
                h += `<tr style="border-bottom:1px solid rgba(255,255,255,0.1)">
                        <td style="padding:10px">${c.n} <br><small style="color:var(--gold)">${c.p}</small></td>
                        <td style="padding:10px; text-align:center">${c.u} / ${c.l}</td>
                        <td style="padding:10px"><button onclick="deletar('${c.p}')" style="background:red; color:white; border:none; padding:5px; cursor:pointer">X</button></td>
                      </tr>`;
            });
            document.getElementById('res_adm').innerHTML = h + "</table>";
        } catch (e) { alert(e.message); }
    }

    async function salvar() {
        const payload = {
            k: document.getElementById('ak').value,
            n: document.getElementById('n').value.toUpperCase(),
            p: document.getElementById('p').value,
            l: parseInt(document.getElementById('l').value)
        };

        if(!payload.k || !payload.n || !payload.p || !payload.l) return alert("ERRO: Preencha todos os campos!");

        try {
            const res = await fetch(`${API_BASE}/api/admin/save`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(payload)
            });
            
            if(res.ok) {
                alert("SUCESSO: Fluxo Quântico Consagrado!");
                document.getElementById('n').value = "";
                document.getElementById('p').value = "";
                document.getElementById('l').value = "";
                listar();
            } else { alert("ERRO no Servidor. Verifique a Chave Master."); }
        } catch (e) { alert("Falha na conexão."); }
    }

    async function deletar(pin) {
        const k = document.getElementById('ak').value;
        if(!confirm("Remover este acesso permanentemente?")) return;
        await fetch(`${API_BASE}/api/admin/delete`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({k: k, p: pin})
        });
        listar();
    }

    // --- FUNÇÕES DE CLIENTE (FORÇADAS) ---
    async function logar() {
        const p = document.getElementById('pin').value;
        try {
            const res = await fetch(`${API_BASE}/api/cli/info?p=${p}`, { cache: "no-store" });
            if(!res.ok) throw new Error("PIN Não Sintonizado.");
            const d = await res.json();
            
            document.getElementById('login_area').style.display='none';
            document.getElementById('dash_area').style.display='block';
            document.getElementById('nome_terapeuta').innerText = d.n;
            
            // CÁLCULO DE SALDO FORÇADO
            const restante = d.l - d.u;
            document.getElementById('txt_saldo').innerText = `${restante} ativações disponíveis`;
            
            let h = "";
            d.h.reverse().forEach(item => {
                const pts = item.split(' | ');
                h += `<div class="item-historico">
                        <input type="checkbox" class="ck" data-full="${item}">
                        <div style="flex-grow:1">
                            <div style="font-size:11px; color:var(--gold)">${pts[0]} - ${pts[2]}</div>
                            <div style="font-weight:bold">${pts[1]}</div>
                            <div style="font-size:12px; font-style:italic">"${pts[3]}"</div>
                        </div>
                      </div>`;
            });
            document.getElementById('lista_cli').innerHTML = h;
        } catch (e) { alert(e.message); }
    }
</script>