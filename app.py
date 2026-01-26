import streamlit as st
import os
import numpy as np
import pandas as pd
import plotly.express as px
from cryptography.fernet import Fernet
from fpdf import FPDF
import math

# --- 1. SEGURANÇA ---
# PIN de 6 dígitos configurado via variável de ambiente no Render
PIN_CRIPTOGRAFADO = "gAAAAABpdRRwrtzON4oc6ayd3fx1LjLjX8TjRj7riCkHHuOpi0lcYFAu04KEXEo8d3-GJz9HmpP-AjvbLOLzr6zC6GMUvOCP1A=="

def validar_acesso(pin_digitado):
    senha_aluno_env = os.environ.get('acesso_aluno')
    if senha_aluno_env and pin_digitado == senha_aluno_env:
        return "aluno"
    try:
        # Puxa a chave mestra (em minúsculas) do ambiente do Render
        chave = os.environ.get('chave_mestra')
        if not chave: return "erro_env"
        chave = chave.strip().replace("'", "").replace('"', "").replace('b', '', 1) if chave.startswith('b') else chave.strip()
        f = Fernet(chave.encode())
        # Validação do PIN de 6 dígitos (mínimo 6, máximo 8 caracteres)
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
        "Expressões (PEMDAS)", 
        "Sistemas Lineares", 
        "Matrizes (Sarrus)",
        "Funções Aritméticas", 
        "Logaritmos (Gráfico)", 
        "Álgebra & Geometria", 
        "Financeiro (Pandas)", 
        "Pasta Drive"
    ])
    st.sidebar.button("Sair", on_click=lambda: st.session_state.update({"perfil": None}))

    # --- SISTEMAS LINEARES ---
    if menu == "Sistemas Lineares":
        st.header("📏 Resolução de Sistemas (Ax = B)")
        ordem_s = st.selectbox("Incógnitas:", [2, 3], key="os_s")
        mat_A, vec_B = [], []
        for i in range(ordem_s):
            cols = st.columns(ordem_s + 1)
            linha = [cols[j].number_input(f"A{i+1}{j+1}", value=1.0 if i==j else 0.0, key=f"sA_{i}{j}") for j in range(ordem_s)]
            res_b = cols[ordem_s].number_input(f"B{i+1}", value=1.0, key=f"sB_{i}")
            mat_A.append(linha)
            vec_B.append(res_b)
        if st.button("Resolver Sistema"):
            try:
                sol = np.linalg.solve(np.array(mat_A), np.array(vec_B))
                for idx, s in enumerate(sol): st.success(f"x{idx+1} = {s:.4f}")
            except: st.error("O sistema não possui solução única.")

    # --- EXPRESSÕES ---
    elif menu == "Expressões (PEMDAS)":
        st.header("🧮 Hierarquia de Operações")
        if os.path.exists("img1ori.png"):
            st.image("img1ori.png", use_container_width=True)
        exp = st.text_input("Expressão (use apenas parênteses no código):", key="ex_p")
        if st.button("Calcular"):
            try:
                res = eval(exp.replace('^', '**'), {"__builtins__": None}, {"math": math, "sqrt": math.sqrt})
                st.subheader(f"Resultado: {res}")
            except: st.error("Erro na sintaxe.")

    # --- MATRIZES ---
    elif menu == "Matrizes (Sarrus)":
        st.header("🧮 Determinantes")
        ordem_m = st.selectbox("Ordem:", [2, 3], key="om_m")
        mat_m = []
        for i in range(ordem_m):
            cols = st.columns(ordem_m)
            mat_m.append([cols[j].number_input(f"M{i+1}{j+1}", value=0.0, key=f"mm_{i}{j}") for j in range(ordem_m)])
        if st.button("Calcular"):
            det = np.linalg.det(np.array(mat_m))
            st.success(f"Determinante = {det:.2f}")

    # --- ÁLGEBRA & GEOMETRIA ---
    elif menu == "Álgebra & Geometria":
        st.header("📐 Bhaskara e Pitágoras")
        a = st.number_input("a", 1.0, key="b_a")
        b = st.number_input("b", -5.0, key="b_b")
        c = st.number_input("c", 6.0, key="b_c")
        if st.button("Raízes"):
            delta = b**2 - 4*a*c
            if delta >= 0: st.write(f"x1: {(-b+math.sqrt(delta))/(2*a):.2f}, x2: {(-b-math.sqrt(delta))/(2*a):.2f}")
            else: st.error("Delta negativo.")

    # --- FINANCEIRO ---
    elif menu == "Financeiro (Pandas)":
        st.header("💰 Juros Compostos")
        cap = st.number_input("Capital:", 1000.0, key="f_c")
        txa = st.number_input("Taxa (%):", 1.0, key="f_i") / 100
        tme = st.number_input("Tempo:", 12, key="f_t")
        if st.button("Ver Tabela"):
            df = pd.DataFrame([{"Mês": m, "Montante": cap*(1+txa)**m} for m in range(int(tme)+1)])
            st.table(df)

    elif menu == "Pasta Drive":
        st.link_button("🚀 Abrir Drive", "SEU_LINK_AQUI")