import streamlit as st
import os
import numpy as np
import pandas as pd
import plotly.express as px
from cryptography.fernet import Fernet
from fpdf import FPDF
import math

# --- 1. SEGURANÇA ---
# PIN de 6 dígitos com validação de 6-8 caracteres
PIN_CRIPTOGRAFADO = "gAAAAABpdRRwrtzON4oc6ayd3fx1LjLjX8TjRj7riCkHHuOpi0lcYFAu04KEXEo8d3-GJz9HmpP-AjvbLOLzr6zC6GMUvOCP1A=="

def validar_acesso(pin_digitado):
    senha_aluno_env = os.environ.get('acesso_aluno')
    if senha_aluno_env and pin_digitado == senha_aluno_env:
        return "aluno"
    try:
        # Recupera a chave mestra do ambiente Render
        chave = os.environ.get('chave_mestra') 
        if not chave: return "erro_env"
        chave = chave.strip().replace("'", "").replace('"', "").replace('b', '', 1) if chave.startswith('b') else chave.strip()
        f = Fernet(chave.encode())
        if pin_digitado == f.decrypt(PIN_CRIPTOGRAFADO.strip().encode()).decode():
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
        "Expressões (PEMDAS)", "Funções Aritméticas", "Logaritmos (Gráfico)", 
        "Matrizes & Sistemas", "Álgebra & Geometria", "Financeiro (Pandas)", "Pasta Drive"
    ])
    st.sidebar.button("Sair", on_click=lambda: st.session_state.update({"perfil": None}))

    # --- EXPRESSÕES ---
    if menu == "Expressões (PEMDAS)":
        st.header("🧮 Calculadora de Expressões")
        if os.path.exists("img1ori.png"):
            st.image("img1ori.png", caption="Guia de Orientação: Ordem de Precedência")
        else:
            st.info("💡 Dica: Siga a ordem PEMDAS.")
        
        exp = st.text_input("Digite a expressão:", value="(10 + 2) * 3^2", key="calc_exp")
        if st.button("Resolver"):
            try:
                res = eval(exp.replace('^', '**'), {"__builtins__": None}, {"math": math, "sqrt": math.sqrt})
                st.success(f"Resultado: {res}")
            except Exception as e: st.error(f"Erro na expressão.")

    # --- FUNÇÕES ARITMÉTICAS ---
    elif menu == "Funções Aritméticas":
        st.header("🔍 Função Divisor f(n)")
        n_val = st.number_input("Número n:", min_value=1, value=12, key="arit_n")
        if st.button("Analisar"):
            divs = [d for d in range(1, n_val + 1) if n_val % d == 0]
            st.success(f"f({n_val}) = {len(divs)}")
            st.write(f"Divisores: {divs}")

    # --- LOGARITMOS ---
    elif menu == "Logaritmos (Gráfico)":
        st.header("🔢 Gráfico Logarítmico")
        base_g = st.slider("Base:", 1.1, 10.0, 2.0, key="log_slider")
        x_vals = np.linspace(0.1, 10, 100)
        y_vals = [math.log(x, base_g) for x in x_vals]
        df_log = pd.DataFrame({'x': x_vals, 'y': y_vals})
        st.plotly_chart(px.line(df_log, x='x', y='y', title="f(x) = log(x)"))

    # --- FINANCEIRO ---
    elif menu == "Financeiro (Pandas)":
        st.header("💰 Projeção de Juros")
        cap = st.number_input("Capital:", 1000.0, key="f_cap")
        txa = st.number_input("Taxa (%):", 1.0, key="f_txa") / 100
        tme = st.number_input("Meses:", 12, key="f_tme")
        if st.button("Calcular"):
            evolucao = [{"Mês": m, "Montante": cap * (1 + txa)**m} for m in range(int(tme) + 1)]
            st.table(pd.DataFrame(evolucao))

    # --- MATRIZES ---
    elif menu == "Matrizes & Sistemas":
        st.header("📏 Álgebra Linear")
        ordem = st.selectbox("Ordem:", [2, 3], key="m_ord")
        matriz = []
        for i in range(ordem):
            cols = st.columns(ordem)
            matriz.append([cols[j].number_input(f"A{i+1}{j+1}", value=float(i==j), key=f"m_{i}_{j}") for j in range(ordem)])
        if st.button("Calcular Det"):
            st.write(f"Determinante: {np.linalg.det(np.array(matriz)):.2f}")

    # --- ÁLGEBRA ---
    elif menu == "Álgebra & Geometria":
        st.header("📐 Bhaskara e Pitágoras")
        a = st.number_input("a", 1.0, key="bh_a")
        b = st.number_input("b", -5.0, key="bh_b")
        c = st.number_input("c", 6.0, key="bh_c")
        if st.button("Calcular Raízes"):
            delta = b**2 - 4*a*c
            if delta >= 0:
                st.write(f"x1: {(-b+math.sqrt(delta))/(2*a):.2f}")
                st.write(f"x2: {(-b-math.sqrt(delta))/(2*a):.2f}")
            else: st.error("Sem raízes reais.")

    elif menu == "Pasta Drive":
        st.link_button("🚀 Abrir Google Drive", "SEU_LINK_AQUI")