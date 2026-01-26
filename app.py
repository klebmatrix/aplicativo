import streamlit as st
import os
import numpy as np
import pandas as pd
import plotly.express as px
from cryptography.fernet import Fernet
import math

# --- 1. VERIFICAÇÃO DE INTEGRIDADE ---
def checar_ambiente():
    avisos = []
    if not os.environ.get('chave_mestra'):
        avisos.append("❌ Erro: Variável 'chave_mestra' ausente no Render.")
    if not os.environ.get('acesso_aluno'):
        avisos.append("❌ Erro: Variável 'acesso_aluno' ausente no Render.")
    if not os.path.exists("img1ori.png"):
        avisos.append("⚠️ Alerta: Arquivo 'img1ori.png' não encontrado na pasta raiz.")
    return avisos

# --- 2. SEGURANÇA ---
PIN_CRIPTOGRAFADO = "gAAAAABpdRRwrtzON4oc6ayd3fx1LjLjX8TjRj7riCkHHuOpi0lcYFAu04KEXEo8d3-GJz9HmpP-AjvbLOLzr6zC6GMUvOCP1A=="

def validar_acesso(pin_digitado):
    senha_aluno_env = os.environ.get('acesso_aluno')
    if senha_aluno_env and pin_digitado == senha_aluno_env:
        return "aluno"
    try:
        chave = os.environ.get('chave_mestra') # [cite: 2026-01-24]
        if not chave: return "erro_env"
        chave = chave.strip().replace("'", "").replace('"', "").replace('b', '', 1) if chave.startswith('b') else chave.strip()
        f = Fernet(chave.encode())
        if pin_digitado == f.decrypt(PIN_CRIPTOGRAFADO.strip().encode()).decode():
            return "admin"
    except: pass
    return "negado"

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

# Rodar check inicial
for alerta in checar_ambiente():
    st.sidebar.warning(alerta)

if 'perfil' not in st.session_state:
    st.session_state.perfil = None

# --- 3. TELA DE LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Quantum Math Lab - Acesso")
    pin = st.text_input("Digite seu PIN de 6 dígitos:", type="password", key="login_field")
    if st.button("Entrar"):
        acesso = validar_acesso(pin)
        if acesso != "negado":
            st.session_state.perfil = acesso
            st.rerun()
        else:
            st.error("PIN inválido ou variáveis de ambiente incorretas.")
    st.stop()

# --- 4. PAINEL DO PROFESSOR (ADMIN) ---
elif st.session_state.perfil == "admin":
    st.sidebar.title("🛠 Menu Professor")
    menu = st.sidebar.radio("Navegação:", [
        "Expressões (PEMDAS)", 
        "Sistemas Lineares", 
        "Logaritmos (Gráfico)",
        "Funções Aritméticas",
        "Matrizes (Sarrus)",
        "Álgebra & Geometria", 
        "Financeiro (Pandas)", 
        "Pasta Drive"
    ])
    st.sidebar.button("Sair", on_click=lambda: st.session_state.update({"perfil": None}))

    # MÓDULO: EXPRESSÕES
    if menu == "Expressões (PEMDAS)":
        st.header("🧮 Hierarquia de Operações")
        if os.path.exists("img1ori.png"):
            st.image("img1ori.png", caption="Guia: Parênteses -> Colchetes -> Chaves")
        exp = st.text_input("Expressão (use apenas parênteses):", value="((10 + 2) * 5) / 2")
        if st.button("Resolver"):
            try:
                # Resolve de dentro para fora seguindo a lógica matemática
                limpo = exp.replace('^', '**')
                resultado = eval(limpo, {"__builtins__": None}, {"math": math, "sqrt": math.sqrt})
                st.success(f"Resultado: {resultado}")
            except Exception as e:
                st.error(f"Erro de sintaxe: {e}")

    # MÓDULO: SISTEMAS LINEARES
    elif menu == "Sistemas Lineares":
        st.header("📏 Sistema Ax = B")
        ordem = st.selectbox("Incógnitas:", [2, 3], key="sys_o")
        mat_A, vec_B = [], []
        for i in range(ordem):
            cols = st.columns(ordem + 1)
            mat_A.append([cols[j].number_input(f"A{i+1}{j+1}", value=1.0 if i==j else 0.0, key=f"sysA{i}{j}") for j in range(ordem)])
            vec_B.append(cols[ordem].number_input(f"B{i+1}", value=1.0, key=f"sysB{i}"))
        if st.button("Calcular Solução"):
            try:
                res = np.linalg.solve(np.array(mat_A), np.array(vec_B))
                st.write("Vetor Solução X:", res)
            except: st.error("Sistema Impossível ou Indeterminado.")

    # MÓDULO: LOGARITMOS
    elif menu == "Logaritmos (Gráfico)":
        st.header("🔢 Função Logarítmica")
        base = st.slider("Escolha a base b:", 1.1, 10.0, 2.0)
        x_vals = np.linspace(0.1, 20, 200)
        y_vals = [math.log(x, base) for x in x_vals]
        fig = px.line(pd.DataFrame({'x': x_vals, 'y': y_vals}), x='x', y='y', title=f"f(x) = log_{base}(x)")
        st.plotly_chart(fig)

    # MÓDULO: FUNÇÕES ARITMÉTICAS
    elif menu == "Funções Aritméticas":
        st.header("🔍 Função Divisor f(n)")
        n_val = st.number_input("Número n:", min_value=1, value=12)
        divs = [d for d in range(1, n_val + 1) if n_val % d == 0]
        st.info(f"Divisores de {n_val}: {divs}")
        st.success(f"Quantidade f({n_val}) = {len(divs)}")

    # MÓDULO: FINANCEIRO
    elif menu == "Financeiro (Pandas)":
        st.header("💰 Juros Compostos")
        c = st.number_input("Capital Inicial:", 1000.0)
        tx = st.number_input("Taxa mensal (%):", 1.0) / 100
        t = st.number_input("Tempo (meses):", 12)
        if st.button("Gerar Tabela de Evolução"):
            df = pd.DataFrame([{"Mês": m, "Montante": c * (1 + tx)**m} for m in range(int(t) + 1)])
            st.table(df)

    # MÓDULO: DRIVE
    elif menu == "Pasta Drive":
        st.link_button("🚀 Abrir Google Drive", "SEU_LINK_AQUI")