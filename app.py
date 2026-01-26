import streamlit as st
import os
import numpy as np
import pandas as pd
import plotly.express as px
from cryptography.fernet import Fernet
import math

# --- 1. SEGURANÇA E AMBIENTE ---
# PIN configurado para 6 dígitos conforme solicitado
PIN_CRIPTOGRAFADO = "gAAAAABpdRRwrtzON4oc6ayd3fx1LjLjX8TjRj7riCkHHuOpi0lcYFAu04KEXEo8d3-GJz9HmpP-AjvbLOLzr6zC6GMUvOCP1A=="

def validar_acesso(pin_digitado):
    senha_aluno_env = os.environ.get('acesso_aluno')
    if senha_aluno_env and pin_digitado == senha_aluno_env:
        return "aluno"
    try:
        # Puxa a chave mestra em letras minúsculas do Render
        chave = os.environ.get('chave_mestra')
        if not chave: return "erro_env"
        chave = chave.strip().replace("'", "").replace('"', "").replace('b', '', 1) if chave.startswith('b') else chave.strip()
        f = Fernet(chave.encode())
        # Validação do PIN entre 6 e 8 caracteres
        if pin_digitado == f.decrypt(PIN_CRIPTOGRAFADO.strip().encode()).decode():
            return "admin"
    except: pass
    return "negado"

st.set_page_config(page_title="Quantum Math Lab", layout="wide")
if 'perfil' not in st.session_state: st.session_state.perfil = None

# --- 2. LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Quantum Math Lab")
    pin = st.text_input("Digite o PIN:", type="password", key="main_pin")
    if st.button("Acessar"):
        acesso = validar_acesso(pin)
        if acesso != "negado":
            st.session_state.perfil = acesso
            st.rerun()
        else: st.error("Acesso negado.")
    st.stop()

# --- 3. PAINEL DO PROFESSOR ---
elif st.session_state.perfil == "admin":
    st.sidebar.title("🛠 Menu Professor")
    menu = st.sidebar.radio("Escolha o Módulo:", [
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

    # --- EXPRESSÕES ---
    if menu == "Expressões (PEMDAS)":
        st.header("🧮 Calculadora e Hierarquia")
        if os.path.exists("img1ori.png"):
            st.image("img1ori.png", caption="Guia Pedagógico de Resolução")
        
        exp = st.text_input("Expressão (Use apenas parênteses):", value="(10 + 2) * 3^2")
        if st.button("Calcular"):
            try:
                res = eval(exp.replace('^', '**'), {"__builtins__": None}, {"math": math, "sqrt": math.sqrt})
                st.success(f"Resultado: {res}")
            except: st.error("Erro na expressão.")

    # --- LOGARITMOS ---
    elif menu == "Logaritmos (Gráfico)":
        st.header("🔢 Função Logarítmica")
        base = st.slider("Base b:", 1.1, 10.0, 2.0)
        x_vals = np.linspace(0.1, 10, 100)
        y_vals = [math.log(x, base) for x in x_vals]
        fig = px.line(pd.DataFrame({'x': x_vals, 'y': y_vals}), x='x', y='y', title=f"log base {base}")
        st.plotly_chart(fig)

    # --- FUNÇÕES ARITMÉTICAS ---
    elif menu == "Funções Aritméticas":
        st.header("🔍 Função Divisor f(n)")
        n = st.number_input("Número n:", min_value=1, value=12)
        divs = [d for d in range(1, n + 1) if n % d == 0]
        st.write(f"Divisores: {divs}")
        st.success(f"Total de divisores: {len(divs)}")

    # --- SISTEMAS LINEARES ---
    elif menu == "Sistemas Lineares":
        st.header("📏 Sistemas Ax = B")
        ordem = st.selectbox("Incógnitas:", [2, 3])
        mat_A, vec_B = [], []
        for i in range(ordem):
            cols = st.columns(ordem + 1)
            mat_A.append([cols[j].number_input(f"A{i+1}{j+1}", value=1.0 if i==j else 0.0) for j in range(ordem)])
            vec_B.append(cols[ordem].number_input(f"B{i+1}", value=1.0))
        if st.button("Resolver"):
            try:
                st.write("Solução:", np.linalg.solve(np.array(mat_A), np.array(vec_B)))
            except: st.error("Erro no sistema.")

    # --- FINANCEIRO ---
    elif menu == "Financeiro (Pandas)":
        st.header("💰 Juros Compostos")
        c = st.number_input("Capital:", 1000.0)
        i = st.number_input("Taxa %:", 1.0) / 100
        t = st.number_input("Meses:", 12)
        if st.button("Tabela de Evolução"):
            df = pd.DataFrame([{"Mês": m, "Montante": c*(1+i)**m} for m in range(int(t)+1)])
            st.table(df)

    elif menu == "Pasta Drive":
        st.link_button("🚀 Abrir Drive", "SEU_LINK_AQUI")