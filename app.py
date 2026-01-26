import streamlit as st
import os
import numpy as np
from cryptography.fernet import Fernet
from fpdf import FPDF
import random
import math

# --- 1. SEGURANÇA E AMBIENTE ---
# PIN de 6 dígitos configurado via variável de ambiente
PIN_CRIPTOGRAFADO = "gAAAAABpdRRwrtzON4oc6ayd3fx1LjLjX8TjRj7riCkHHuOpi0lcYFAu04KEXEo8d3-GJz9HmpP-AjvbLOLzr6zC6GMUvOCP1A=="

def validar_acesso(pin_digitado):
    senha_aluno_env = os.environ.get('acesso_aluno')
    if senha_aluno_env and pin_digitado == senha_aluno_env:
        return "aluno"
    try:
        chave = os.environ.get('chave_mestra') # [cite: 2026-01-24]
        if not chave: return "erro_env"
        # Limpeza da chave para evitar erros de string
        chave = chave.strip().replace("'", "").replace('"', "").replace('b', '', 1) if chave.startswith('b') else chave.strip()
        f = Fernet(chave.encode())
        # PIN entre 6 e 8 caracteres [cite: 2026-01-21]
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
    pin = st.text_input("Digite o PIN:", type="password", key="login_pass")
    if st.button("Acessar Sistema"):
        acesso = validar_acesso(pin)
        if acesso != "negado":
            st.session_state.perfil = acesso
            st.rerun()
        else: st.error("PIN incorreto.")
    st.stop()

# --- 3. PAINEL ADMIN ---
elif st.session_state.perfil == "admin":
    st.sidebar.title("🛠 Painel Professor")
    menu = st.sidebar.radio("Navegação:", [
        "Função Divisores", "Expressões (PEMDAS)", "Logaritmos", 
        "Matrizes & Sistemas", "Álgebra & Geometria", "Financeiro", "Pasta Drive"
    ])
    st.sidebar.button("Sair", on_click=lambda: st.session_state.update({"perfil": None}))

    # --- FUNÇÃO DIVISORES ---
    if menu == "Função Divisores":
        st.header("🔍 Função Aritmética f(n)")
        st.latex(r"f(n) = \text{quantidade de divisores de } n")
        n_val = st.number_input("Número n:", min_value=1, value=12, key="n_div")
        if st.button("Calcular"):
            res = contar_divisores(n_val)
            divs = [i for i in range(1, n_val + 1) if n_val % i == 0]
            st.success(f"f({n_val}) = {res}")
            st.write(f"Divisores: {divs}")
            st.info("Classificação: Função Multiplicativa.")

    # --- EXPRESSÕES ---
    elif menu == "Expressões (PEMDAS)":
        st.header("🧮 Ordem de Operações")
        exp_txt = st.text_input("Expressão (Ex: (2+3)*5^2):", key="exp_in")
        if st.button("Resolver"):
            try:
                res = eval(exp_txt.replace('^', '**'), {"__builtins__": None}, {"math": math, "sqrt": math.sqrt})
                st.subheader(f"Resultado: {res}")
            except: st.error("Expressão inválida.")

    # --- LOGARITMOS ---
    elif menu == "Logaritmos":
        st.header("🔢 Logaritmos")
        st.latex(r"\log_{b}(a) = x \iff b^x = a")
        c1, c2 = st.columns(2)
        la = c1.number_input("Logaritmando:", min_value=0.1, value=100.0, key="l_a")
        lb = c2.number_input("Base:", min_value=0.1, value=10.0, key="l_b")
        if st.button("Calcular Log"):
            st.success(f"Resultado: {math.log(la, lb):.4f}")

    # --- MATRIZES & SISTEMAS ---
    elif menu == "Matrizes & Sistemas":
        st.header("🧮 Matrizes e Sistemas Lineares")
        ordem = st.selectbox("Ordem:", [2, 3], key="m_ord")
        mat = []
        for i in range(ordem):
            cols = st.columns(ordem)
            mat.append([cols[j].number_input(f"A{i+1}{j+1}", value=float(i==j), key=f"mat_{i}_{j}") for j in range(ordem)])
        if st.button("Calcular Determinante"):
            det = np.linalg.det(np.array(mat))
            st.write(f"Determinante: {det:.2f}")

    # --- ÁLGEBRA & GEOMETRIA ---
    elif menu == "Álgebra & Geometria":
        st.subheader("🔍 Equação de 2º Grau (Bhaskara)")
        st.latex(r"x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}")
        a, b, c = st.columns(3)
        va = a.number_input("a", 1.0, key="a2"); vb = b.number_input("b", -5.0, key="b2"); vc = c.number_input("c", 6.0, key="c2")
        if st.button("Raízes"):
            delta = vb**2 - 4*va*vc
            if delta >= 0: st.write(f"x1: {(-vb+math.sqrt(delta))/(2*va):.2f}, x2: {(-vb-math.sqrt(delta))/(2*va):.2f}")
            else: st.error("Delta negativo.")

    # --- FINANCEIRO ---
    elif menu == "Financeiro":
        st.header("💰 Matemática Financeira")
        st.latex(r"M = C(1+i)^t")
        cap = st.number_input("Capital (C):", 1000.0, key="fin_c")
        tax = st.number_input("Taxa % (i):", 1.0, key="fin_i") / 100
        tme = st.number_input("Tempo (t):", 12, key="fin_t")
        if st.button("Montante"):
            st.metric("Total", f"R$ {cap*(1+tax)**tme:.2f}")

    # --- DRIVE ---
    elif menu == "Pasta Drive":
        st.link_button("🚀 Abrir Google Drive", "https://drive.google.com/drive/folders/1OickfiilObBDB2FdL58ftFeW-zngNAbQ?usp=drive_link")