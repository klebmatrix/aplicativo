import streamlit as st
import os
import numpy as np
import pandas as pd
from cryptography.fernet import Fernet
import math

# --- 1. SEGURANÇA ---
PIN_CRIPTOGRAFADO = "gAAAAABpdRRwrtzON4oc6ayd3fx1LjLjX8TjRj7riCkHHuOpi0lcYFAu04KEXEo8d3-GJz9HmpP-AjvbLOLzr6zC6GMUvOCP1A=="

def validar_acesso(pin_digitado):
    senha_aluno_env = os.environ.get('acesso_aluno')
    if senha_aluno_env and pin_digitado == senha_aluno_env:
        return "aluno"
    try:
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
    pin = st.text_input("Digite o PIN:", type="password", key="login_pass")
    if st.button("Entrar"):
        acesso = validar_acesso(pin)
        if acesso != "negado":
            st.session_state.perfil = acesso
            st.rerun()
        else: st.error("Acesso negado.")
    st.stop()

# --- 3. PAINEL DO PROFESSOR (TUDO AQUI) ---
elif st.session_state.perfil == "admin":
    st.sidebar.title("🛠 Menu Professor")
    menu = st.sidebar.radio("Módulos:", [
        "Expressões (PEMDAS)", 
        "Logaritmos (Cálculo)",
        "Funções Aritméticas",
        "Sistemas Lineares", 
        "Matrizes (Sarrus)",
        "Álgebra & Geometria", 
        "Financeiro", 
        "Pasta Drive"
    ])
    st.sidebar.button("Sair", on_click=lambda: st.session_state.update({"perfil": None}))

    # MÓDULO 1: EXPRESSÕES
    if menu == "Expressões (PEMDAS)":
        st.header("🧮 Hierarquia de Operações")
        if os.path.exists("img1ori.png"):
            st.image("img1ori.png", caption="Guia: Parênteses -> Colchetes -> Chaves")
        exp = st.text_input("Digite a expressão:", value="((10 + 5) * 2) / 3")
        if st.button("Resolver"):
            try:
                res = eval(exp.replace('^', '**'), {"__builtins__": None}, {"math": math, "sqrt": math.sqrt})
                st.success(f"Resultado: {res}")
            except: st.error("Erro na expressão.")

    # MÓDULO 2: LOGARITMOS (SIMPLIFICADO)
    elif menu == "Logaritmos (Cálculo)":
        st.header("🔢 Cálculo de Logaritmos")
        v_base = st.number_input("Base (b):", min_value=0.1, value=10.0)
        v_log = st.number_input("Logaritmando (a):", min_value=0.1, value=100.0)
        if st.button("Calcular"):
            try:
                st.success(f"Resultado: {math.log(v_log, v_base):.4f}")
            except: st.error("Cálculo impossível.")

    # MÓDULO 3: FUNÇÕES ARITMÉTICAS (RESTURADO)
    elif menu == "Funções Aritméticas":
        st.header("🔍 Estudo de Divisores f(n)")
        n_val = st.number_input("Digite o número n:", min_value=1, value=12)
        if st.button("Analisar"):
            divs = [d for d in range(1, n_val + 1) if n_val % d == 0]
            st.success(f"f({n_val}) = {len(divs)}")
            st.write(f"**Conjunto de Divisores:** {divs}")

    # MÓDULO 4: SISTEMAS LINEARES
    elif menu == "Sistemas Lineares":
        st.header("📏 Sistemas Ax = B")
        ordem = st.selectbox("Incógnitas:", [2, 3], key="sys_o")
        mat_A, vec_B = [], []
        for i in range(ordem):
            cols = st.columns(ordem + 1)
            mat_A.append([cols[j].number_input(f"A{i+1}{j+1}", value=1.0 if i==j else 0.0, key=f"A{i}{j}") for j in range(ordem)])
            vec_B.append(cols[ordem].number_input(f"B{i+1}", value=1.0, key=f"B{i}"))
        if st.button("Resolver"):
            try:
                sol = np.linalg.solve(np.array(mat_A), np.array(vec_B))
                st.success(f"Solução: {sol}")
            except: st.error("Erro no sistema.")

    # MÓDULO 5: MATRIZES
    elif menu == "Matrizes (Sarrus)":
        st.header("🧮 Determinantes")
        ordem_m = st.selectbox("Ordem:", [2, 3], key="m_o")
        mat_m = []
        for i in range(ordem_m):
            cols = st.columns(ordem_m)
            mat_m.append([cols[j].number_input(f"M{i+1}{j+1}", value=0.0, key=f"M{i}{j}") for j in range(ordem_m)])
        if st.button("Calcular"):
            st.success(f"Determinante = {np.linalg.det(np.array(mat_m)):.2f}")

    # MÓDULO 6: ÁLGEBRA
    elif menu == "Álgebra & Geometria":
        st.header("📐 Bhaskara")
        a = st.number_input("a", 1.0); b = st.number_input("b", -5.0); c = st.number_input("c", 6.0)
        if st.button("Calcular Raízes"):
            delta = b**2 - 4*a*c
            if delta >= 0:
                st.write(f"x1: {(-b+math.sqrt(delta))/(2*a):.2f}, x2: {(-b-math.sqrt(delta))/(2*a):.2f}")
            else: st.error("Delta negativo.")

    # MÓDULO 7: FINANCEIRO
    elif menu == "Financeiro":
        st.header("💰 Juros Compostos")
        cap = st.number_input("Capital:", 1000.0); i = st.number_input("Taxa %:", 1.0)/100; t = st.number_input("Tempo:", 12)
        if st.button("Calcular"):
            st.metric("Montante Final", f"R$ {cap*(1+i)**t:.2f}")

    # MÓDULO 8: DRIVE
    elif menu == "Pasta Drive":
        st.link_button("🚀 Abrir Drive", "SEU_LINK_AQUI")