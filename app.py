import streamlit as st
import os
import numpy as np
from cryptography.fernet import Fernet
from fpdf import FPDF
import random
import math

# --- 1. SEGURANÇA (ÂNCORA DE ACESSO) ---
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

def contar_divisores(n):
    if n <= 0: return 0
    return len([i for i in range(1, n + 1) if n % i == 0])

st.set_page_config(page_title="Quantum Math Lab", layout="wide")
if 'perfil' not in st.session_state: st.session_state.perfil = None

# --- 2. LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Quantum Math Lab")
    pin = st.text_input("PIN de 6 dígitos:", type="password", key="login_pin")
    if st.button("Entrar", key="btn_login"):
        acesso = validar_acesso(pin)
        if acesso != "negado":
            st.session_state.perfil = acesso
            st.rerun()
        else: st.error("Acesso negado.")
    st.stop()

# --- 3. PAINEL ADMIN (CONTÍNUO) ---
elif st.session_state.perfil == "admin":
    st.sidebar.title("🛠 Menu Professor")
    menu = st.sidebar.radio("Escolha o Módulo:", [
        "Função Divisores", "Expressões (PEMDAS)", "Logaritmos", 
        "Matrizes/Sistemas", "Álgebra/Geometria", "Financeiro", "Pasta Drive"
    ])
    st.sidebar.button("Sair", on_click=lambda: st.session_state.update({"perfil": None}))

    # --- MÓDULO: FUNÇÃO DIVISORES ---
    if menu == "Função Divisores":
        st.header("🔍 Função Aritmética Divisor f(n)")
        
        st.latex(r"f(n) = \sum_{d|n} 1")
        n_input = st.number_input("Digite um número inteiro positivo:", min_value=1, value=12, key="divisor_n")
        if st.button("Analisar Propriedades", key="btn_div"):
            res = contar_divisores(n_input)
            divs = [i for i in range(1, n_input + 1) if n_input % i == 0]
            st.success(f"f({n_input}) = {res}")
            st.write(f"**Conjunto de Divisores:** {divs}")
            st.info("**Classificação:** Função Multiplicativa. Se mdc(a,b)=1, então f(a·b) = f(a)·f(b).")

    # --- MÓDULO: EXPRESSÕES (PEMDAS) ---
    elif menu == "Expressões (PEMDAS)":
        st.header("🧮 Expressões e Ordem de Operações")
        
        expr = st.text_input("Insira a expressão (ex: 2^3 + 5 * (10/2)):", key="expr_in")
        if st.button("Calcular", key="btn_expr"):
            try:
                # Converte ^ para ** e avalia com segurança
                res_expr = eval(expr.replace('^', '**'), {"__builtins__": None}, {"math": math, "sqrt": math.sqrt})
                st.subheader(f"Resultado: {res_expr}")
            except: st.error("Erro na expressão.")

    # --- MÓDULO: LOGARITMOS ---
    elif menu == "Logaritmos":
        st.header("🔢 Logaritmos")
        
        c1, c2 = st.columns(2)
        base = c1.number_input("Base:", min_value=0.1, value=10.0, key="log_b")
        val = c2.number_input("Logaritmando:", min_value=0.1, value=100.0, key="log_v")
        if st.button("Calcular Log", key="btn_log"):
            st.success(f"Resultado: {math.log(val, base):.4f}")

    # --- MÓDULO: FINANCEIRO ---
    elif menu == "Financeiro":
        st.header("💰 Juros Compostos")
        
        c, i, t = st.columns(3)
        cap = c.number_input("Capital:", value=1000.0, key="fin_c")
        tax = i.number_input("Taxa %:", value=1.0, key="fin_i") / 100
        tmp = t.number_input("Tempo (meses):", value=12, key="fin_t")
        if st.button("Calcular Montante", key="btn_fin"):
            st.metric("Montante", f"R$ {cap*(1+tax)**tmp:.2f}")

    # --- MÓDULO: ÁLGEBRA E GEOMETRIA ---
    elif menu == "Álgebra/Geometria":
        st.subheader("🔍 Bhaskara e Pitágoras")
        

[Image of the quadratic formula]

        a, b, c = st.columns(3)
        va = a.number_input("a", 1.0, key="b_a"); vb = b.number_input("b", -5.0, key="b_b"); vc = c.number_input("c", 6.0, key="b_c")
        if st.button("Resolver Bhaskara", key="btn_bha"):
            delta = vb**2 - 4*va*vc
            if delta >= 0: st.write(f"Raízes: {(-vb+np.sqrt(delta))/(2*va):.2f} e {(-vb-np.sqrt(delta))/(2*va):.2f}")
            else: st.error("Sem raízes reais.")
        st.divider()
        

[Image of the Pythagorean theorem diagram]

        ca = st.number_input("Cateto A", 3.0, key="p_a"); cb = st.number_input("Cateto B", 4.0, key="p_b")
        if st.button("Calcular Hipotenusa", key="btn_pit"):
            st.success(f"H = {np.sqrt(ca**2 + cb**2):.2f}")

    # --- MÓDULO: DRIVE ---
    elif menu == "Pasta Drive":
        st.header("📂 Gerenciamento Drive")
        st.link_button("🚀 Abrir Google Drive", "COLE_SEU_LINK_AQUI")