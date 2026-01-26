import streamlit as st
import os
import numpy as np
import pandas as pd
import plotly.express as px
from cryptography.fernet import Fernet
from fpdf import FPDF
import math

# --- 1. SEGURANÇA ---
PIN_CRIPTOGRAFADO = "gAAAAABpdRRwrtzON4oc6ayd3fx1LjLjX8TjRj7riCkHHuOpi0lcYFAu04KEXEo8d3-GJz9HmpP-AjvbLOLzr6zC6GMUvOCP1A=="

def validar_acesso(pin_digitado):
    senha_aluno_env = os.environ.get('acesso_aluno')
    if senha_aluno_env and pin_digitado == senha_aluno_env:
        return "aluno"
    try:
        chave = os.environ.get('chave_mestra') [cite: 2026-01-24]
        if not chave: return "erro_env"
        chave = chave.strip().replace("'", "").replace('"', "").replace('b', '', 1) if chave.startswith('b') else chave.strip()
        f = Fernet(chave.encode())
        if pin_digitado == f.decrypt(PIN_CRIPTOGRAFADO.strip().encode()).decode(): [cite: 2026-01-19, 2026-01-21]
            return "admin"
    except: pass
    return "negado"

st.set_page_config(page_title="Quantum Math Lab", layout="wide")
if 'perfil' not in st.session_state: st.session_state.perfil = None

# --- 2. LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Quantum Math Lab")
    pin = st.text_input("PIN:", type="password", key="main_pin")
    if st.button("Entrar"):
        acesso = validar_acesso(pin)
        if acesso != "negado":
            st.session_state.perfil = acesso
            st.rerun()
        else: st.error("Acesso negado.")
    st.stop()

# --- 3. ÁREA ADMIN ---
elif st.session_state.perfil == "admin":
    st.sidebar.title("🛠 Painel Professor")
    menu = st.sidebar.radio("Módulos:", [
        "Expressões (PEMDAS)", 
        "Logaritmos (Gráfico)",
        "Funções Aritméticas",
        "Sistemas Lineares", 
        "Matrizes (Sarrus)",
        "Álgebra & Geometria", 
        "Financeiro (Pandas)", 
        "Pasta Drive"
    ])
    st.sidebar.button("Sair", on_click=lambda: st.session_state.update({"perfil": None}))

    # --- LOGARITMOS (RECUPERADO) ---
    if menu == "Logaritmos (Gráfico)":
        st.header("🔢 Análise Logarítmica")
        st.latex(r"\log_{b}(x) = y")
        c1, c2 = st.columns(2)
        base = c1.slider("Base (b):", 1.1, 10.0, 2.0, key="log_b")
        alcance = c2.slider("Alcance de x:", 5, 100, 10, key="log_x")
        
        x_vals = np.linspace(0.1, alcance, 100)
        y_vals = [math.log(x, base) for x in x_vals]
        df_log = pd.DataFrame({'x': x_vals, 'f(x)': y_vals})
        
        fig = px.line(df_log, x='x', y='f(x)', title=f"Gráfico da Função Logarítmica (Base {base})")
        st.plotly_chart(fig)

    # --- FUNÇÕES ARITMÉTICAS (RECUPERADO) ---
    elif menu == "Funções Aritméticas":
        st.header("🔍 Estudo da Função Divisor f(n)")
        st.info("Classificação: Função Multiplicativa baseada na fatoração.")
        n_val = st.number_input("Analise o número n:", min_value=1, value=12, key="fn_n")
        divs = [d for d in range(1, n_val + 1) if n_val % d == 0]
        st.success(f"f({n_val}) = {len(divs)}")
        st.write(f"**Conjunto de Divisores:** {divs}")

    # --- EXPRESSÕES ---
    elif menu == "Expressões (PEMDAS)":
        st.header("🧮 Hierarquia de Operações")
        if os.path.exists("img1ori.png"):
            st.image("img1ori.png", use_container_width=True)
        exp = st.text_input("Digite a expressão (apenas parênteses):", key="ex_p")
        if st.button("Calcular"):
            try:
                res = eval(exp.replace('^', '**'), {"__builtins__": None}, {"math": math, "sqrt": math.sqrt})
                st.subheader(f"Resultado: {res}")
            except: st.error("Erro na expressão.")

    # --- SISTEMAS LINEARES ---
    elif menu == "Sistemas Lineares":
        st.header("📏 Sistemas Ax = B")
        ordem_s = st.selectbox("Incógnitas:", [2, 3], key="os_s")
        mat_A, vec_B = [], []
        for i in range(ordem_s):
            cols = st.columns(ordem_s + 1)
            linha = [cols[j].number_input(f"A{i+1}{j+1}", value=1.0 if i==j else 0.0, key=f"sA_{i}{j}") for j in range(ordem_s)]
            res_b = cols[ordem_s].number_input(f"B{i+1}", value=1.0, key=f"sB_{i}")
            mat_A.append(linha)
            vec_B.append(res_b)
        if st.button("Resolver"):
            try:
                sol = np.linalg.solve(np.array(mat_A), np.array(vec_B))
                st.write(f"Solução: {sol}")
            except: st.error("Erro no cálculo.")

    # --- FINANCEIRO ---
    elif menu == "Financeiro (Pandas)":
        st.header("💰 Juros Compostos")
        cap = st.number_input("Capital:", 1000.0, key="f_c")
        txa = st.number_input("Taxa (%):", 1.0, key="f_i") / 100
        tme = st.number_input("Meses:", 12, key="f_t")
        if st.button("Gerar Tabela"):
            df = pd.DataFrame([{"Mês": m, "Montante": cap*(1+txa)**m} for m in range(int(tme)+1)])
            st.table(df)

    elif menu == "Pasta Drive":
        st.link_button("🚀 Abrir Drive", "SEU_LINK_AQUI")