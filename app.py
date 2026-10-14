import time
import threading
import requests
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import os

app = FastAPI()

CONFIG_ROBO = {
    "ativo": False,
    "take_profit_pct": 3.0,
    "alavancagem": 10
}

SIMBOLOS_FUTUROS = [
    'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT',
    'ADAUSDT', 'AVAXUSDT', 'LINKUSDT', 'DOTUSDT', 'NEARUSDT',
    'POLUSDT', 'UNIUSDT', 'ICPUSDT', 'APTUSDT', 'RENDERUSDT',
    'INJUSDT', 'ARUSDT', 'FTMUSDT', 'ATOMUSDT', 'OPUSDT',
    'ARBUSDT', 'SUIUSDT', 'TIAUSDT', 'SEIUSDT', 'STXUSDT',
    'IMXUSDT', 'GRTUSDT', 'RUNEUSDT', 'LDOUSDT', 'FETUSDT',
    'AGIXUSDT', 'PEPEUSDT', 'WIFUSDT', 'FILUSDT', 'HBARUSDT',
    'VETUSDT', 'MKRUSDT', 'AAVEUSDT', 'SNXUSDT', 'CRVUSDT',
    'COMPUSDT', 'KASUSDT', 'ALGOUSDT', 'FTTUSDT', 'BCHUSDT',
    'LTCUSDT', 'ETCUSDT', 'XLMUSDT', 'EOSUSDT', 'THETAUSDT',
    'XTZUSDT', 'EGLDUSDT', 'KAVAUSDT', 'ZILUSDT', 'CHZUSDT',
    'AXSUSDT', 'SANDUSDT', 'MANAUSDT', 'GALAUSDT', 'ENJUSDT'
]

dados_globais = {
    "status_conexao": "Iniciando Blindagem...",
    "saldo_usdt": 8.00,
    "mercado": {},
    "logs": []
}

posicoes_abertas = {}

def adicionar_log(msg: str):
    timestamp = time.strftime("[%H:%M:%S]")
    entrada = f"{timestamp} {msg}"
    dados_globais["logs"].insert(0, entrada)
    if len(dados_globais["logs"]) > 50:
        dados_globais["logs"].pop()

def background_loop():
    global dados_globais, posicoes_abertas
    adicionar_log("Motor Resiliente 24/365 iniciado.")
    
    while True:
        precos_atuais = {}
        sucesso = False
        
        # Tentativa 1: MEXC
        try:
            resp = requests.get("https://api.mexc.com/api/v3/ticker/price", timeout=6)
            if resp.status_code == 200:
                data = resp.json()
                precos_atuais = {item['symbol']: float(item['price']) for item in data}
                sucesso = True
        except Exception:
            pass

        # Tentativa 2: Binance Spot (Fallback se MEXC falhar)
        if not sucesso:
            try:
                resp = requests.get("https://api.binance.com/api/v3/ticker/price", timeout=6)
                if resp.status_code == 200:
                    data = resp.json()
                    precos_atuais = {item['symbol']: float(item['price']) for item in data}
                    sucesso = True
            except Exception:
                pass

        if sucesso:
            dados_globais["status_conexao"] = f"Online (Resiliente | {CONFIG_ROBO['alavancagem']}x)"
        else:
            dados_globais["status_conexao"] = "Aviso: Sincronizando rota..."

        mercado_formatado = {}
        lev = CONFIG_ROBO["alavancagem"]
        tp_alvo = CONFIG_ROBO["take_profit_pct"]

        for simbolo in SIMBOLOS_FUTUROS:
            preco = precos_atuais.get(simbolo, 0.0)
            par_legivel = f"{simbolo.replace('USDT', '')}/USDT"
            
            preco_entrada = posicoes_abertas.get(simbolo, 0.0)
            lucro_pct = 0.0
            
            if preco_entrada > 0 and preco > 0:
                lucro_bruto = ((preco - preco_entrada) / preco_entrada) * 100
                lucro_pct = lucro_bruto * lev

                if lucro_pct >= tp_alvo and CONFIG_ROBO["ativo"]:
                    adicionar_log(f"🚨 TAKE PROFIT ATINGIDO em {par_legivel}! Lucro Alavancado: {lucro_pct:.2f}%")
                    posicoes_abertas.pop(simbolo, None)

            mercado_formatado[par_legivel] = {
                "name": par_legivel,
                "simbolo_bruto": simbolo,
                "preco": preco,
                "preco_str": f"{preco:,.4f} USDT" if preco < 1 else f"{preco:,.2f} USDT",
                "preco_compra": preco_entrada,
                "preco_compra_str": f"{preco_entrada:,.2f} USDT" if preco_entrada > 0 else "Sem Posição",
                "lucro_pct": round(lucro_pct, 2),
                "alerta": lucro_pct >= tp_alvo
            }

        dados_globais["mercado"] = mercado_formatado
        time.sleep(5)

t = threading.Thread(target=background_loop, daemon=True)
t.start()

class ConfigModel(BaseModel):
    ativo: bool
    take_profit_pct: float
    alavancagem: int

class AutonomiaModel(BaseModel):
    simbolo: str
    preco_entrada: float

@app.get("/ping")
def ping_keep_alive():
    return {"status": "alive", "time": time.strftime("%H:%M:%S")}

@app.get("/api/dados")
def pegar_dados():
    return {
        **dados_globais,
        "robo": CONFIG_ROBO
    }

@app.post("/api/configurar")
def configurar_robo(cfg: ConfigModel):
    global CONFIG_ROBO
    CONFIG_ROBO["ativo"] = cfg.ativo
    CONFIG_ROBO["take_profit_pct"] = cfg.take_profit_pct
    CONFIG_ROBO["alavancagem"] = cfg.alavancagem
    adicionar_log(f"Config atualizada -> Status: {cfg.ativo} | TP: {cfg.take_profit_pct}% | {cfg.alavancagem}x")
    return {"status": "ok", "robo": CONFIG_ROBO}

@app.post("/api/registrar_posicao")
def registrar_posicao(dados: AutonomiaModel):
    posicoes_abertas[dados.simbolo] = dados.preco_entrada
    adicionar_log(f"Posição registrada em {dados.simbolo} a {dados.preco_entrada} USDT")
    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
def dashboard():
    html_content = """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>OmniTechAI - Automação 8 USDT</title>
        <style>
            body { background-color: #0d1117; color: #c9d1d9; font-family: Arial, sans-serif; margin: 0; padding: 20px; }
            h1, h2 { color: #58a6ff; }
            .card { background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 15px; margin-bottom: 20px; display: inline-block; vertical-align: top; width: 45%; margin-right: 2%; }
            table { width: 100%; border-collapse: collapse; margin-top: 15px; background: #161b22; border-radius: 6px; overflow: hidden; }
            th, td { padding: 10px; text-align: left; border-bottom: 1px solid #30363d; font-size: 14px; }
            th { background: #21262d; color: #58a6ff; }
            tr:hover { background: #1f242c; }
            .alerta-pisca { background-color: #381313 !important; animation: pisca 1s infinite; }
            @keyframes pisca { 0% { opacity: 1; } 50% { opacity: 0.4; } 100% { opacity: 1; } }
            .btn { background: #238636; color: white; border: none; padding: 8px 12px; border-radius: 4px; cursor: pointer; font-weight: bold; }
            .btn-danger { background: #da3633; }
            .log-box { background: #010409; border: 1px solid #30363d; padding: 10px; height: 140px; overflow-y: scroll; font-family: monospace; font-size: 12px; color: #8b949e; border-radius: 6px; margin-top: 5px; }
            input, select { background: #0d1117; color: #fff; border: 1px solid #30363d; padding: 5px; border-radius: 4px; }
        </style>
    </head>
    <body>
        <h1>OmniTechAI - Robô Autônomo 8 USDT (24/365)</h1>
        <div>
            <div class="card">
                <h3>Gerenciamento</h3>
                <p>Status: <span id="status" style="color: #3fb950; font-weight: bold;">Carregando...</span></p>
                <p>Capital: <span id="saldo" style="color: #3fb950; font-weight: bold;">8.00 USDT</span></p>
            </div>
            <div class="card">
                <h3>Painel de Controle</h3>
                <p>Modo: <span id="robo-status" style="font-weight: bold;">Desligado</span></p>
                <label>Meta TP (%): <input type="number" id="input-tp" value="3.0" step="0.5" style="width: 60px;"></label>
                <label style="margin-left: 10px;">Alavancagem: 
                    <select id="input-lev">
                        <option value="1">1x</option>
                        <option value="5">5x</option>
                        <option value="10" selected>10x</option>
                        <option value="20">20x</option>
                    </select>
                </label>
                <br><br>
                <button id="btn-toggle" class="btn" onclick="alternarMonitor()">Ligar Robô</button>
            </div>
        </div>
        <h2>Logs</h2>
        <div id="log-box" class="log-box">Carregando...</div>
        <h2>Ativos Monitorados</h2>
        <table>
            <thead>
                <tr>
                    <th>Par</th>
                    <th>Preço Atual</th>
                    <th>Entrada</th>
                    <th>Lucro Alavancado</th>
                    <th>Ação</th>
                </tr>
            </thead>
            <tbody id="tabela-corpo">
                <tr><td colspan="5">Sincronizando...</td></tr>
            </tbody>
        </table>
        <script>
            let monitorAtivo = false;
            let audioAlerta = new Audio('https://actions.google.com/sounds/v1/alarms/beep_short.ogg');

            async function atualizarDados() {
                try {
                    let resposta = await fetch('/api/dados');
                    let dados = await resposta.json();
                    document.getElementById('status').innerText = dados.status_conexao;
                    document.getElementById('saldo').innerText = dados.saldo_usdt.toFixed(2) + ' USDT';
                    monitorAtivo = dados.robo.ativo;
                    document.getElementById('input-lev').value = dados.robo.alavancagem;
                    
                    let statusEl = document.getElementById('robo-status');
                    let btnEl = document.getElementById('btn-toggle');
                    if (monitorAtivo) {
                        statusEl.innerText = "LIGADO";
                        statusEl.style.color = "#3fb950";
                        btnEl.innerText = "Desligar Robô";
                        btnEl.className = "btn btn-danger";
                    } else {
                        statusEl.innerText = "DESLIGADO";
                        statusEl.style.color = "#f85149";
                        btnEl.innerText = "Ligar Robô";
                        btnEl.className = "btn";
                    }

                    document.getElementById('log-box').innerHTML = dados.logs.join('<br>');
                    let tbody = document.getElementById('tabela-corpo');
                    tbody.innerHTML = '';
                    let temAlerta = false;

                    for (let [simbolo, info] of Object.entries(dados.mercado)) {
                        let tr = document.createElement('tr');
                        if (info.alerta && monitorAtivo) {
                            tr.className = "alerta-pisca";
                            temAlerta = true;
                        }
                        let lucroCor = info.lucro_pct >= 0 ? '#3fb950' : '#f85149';
                        tr.innerHTML = `
                            <td><b>${info.name}</b></td>
                            <td>${info.preco_str}</td>
                            <td>${info.preco_compra_str}</td>
                            <td style="color: ${lucroCor}; font-weight: bold;">${info.lucro_pct}%</td>
                            <td>
                                <button class="btn" style="padding: 4px 8px; font-size: 12px;" onclick="registrarPosicao('${info.simbolo_bruto}', ${info.preco})">Definir Entrada</button>
                                ${info.alerta && monitorAtivo ? '<span style="color: #ff7b72; font-weight: bold; margin-left: 10px;">🚨 TP ATINGIDO!</span>' : ''}
                            </td>
                        `;
                        tbody.appendChild(tr);
                    }

                    if (temAlerta && monitorAtivo) {
                        audioAlerta.play().catch(e => console.log("Áudio bloqueado"));
                    }
                } catch (e) {
                    console.error("Erro:", e);
                }
            }

            async function alternarMonitor() {
                let novoEstado = !monitorAtivo;
                let tpValor = parseFloat(document.getElementById('input-tp').value);
                let levValor = parseInt(document.getElementById('input-lev').value);
                
                await fetch('/api/configurar', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ ativo: novoEstado, take_profit_pct: tpValor, alavancagem: levValor })
                });
                atualizarDados();
            }

            async function registrarPosicao(simboloBruto, precoAtual) {
                let precoInformado = prompt("Preço de entrada para " + simboloBruto + ":", precoAtual > 0 ? precoAtual : "");
                if (precoInformado) {
                    let precoFloat = parseFloat(precoInformado.replace(',', '.'));
                    if (!isNaN(precoFloat) && precoFloat > 0) {
                        await fetch('/api/registrar_posicao', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({ simbolo: simboloBruto, preco_entrada: precoFloat })
                        });
                        atualizarDados();
                    }
                }
            }

            setInterval(atualizarDados, 4000);
            atualizarDados();
        </script>
    </body>
    </html>
    """
    return html_content
