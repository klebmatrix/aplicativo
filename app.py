import streamlit as st
import os
import numpy as np
from cryptography.fernet import Fernet
from fpdf import FPDF
import random
import math

# --- 1. SEGURANÇA E AMBIENTE ---
# PIN de 6 dígitos [cite: 2026-01-19]
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

# --- 2. MOTOR DE PDF ---
def gerar_material_pdf(titulo, questoes, respostas):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"Atividade: {titulo}", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    for q in questoes:
        pdf.multi_cell(0, 10, txt=q); pdf.ln(5)
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Gabarito Oficial", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    for r in respostas:
        pdf.multi_cell(0, 10, txt=r); pdf.ln(2)
    return pdf.output(dest='S').encode('latin-1')

# --- 3. LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Quantum Math Lab")
    pin = st.text_input("Digite o PIN:", type="password")
    if st.button("Entrar"):
        acesso = validar_acesso(pin)
        if acesso != "negado":
            st.session_state.perfil = acesso
            st.rerun()
        else: st.error("PIN incorreto.")
    st.stop()

# --- 4. ÁREA PROFESSOR (ADMIN COMPLETO) ---
elif st.session_state.perfil == "admin":
    st.sidebar.title("🛠 Painel Professor")
    menu = st.sidebar.radio("Navegação", [
        "Gerador de Listas", "Funções Aritméticas", "Logaritmos", 
        "Matrizes (Sarrus)", "Sistemas Lineares", 
        "Álgebra e Geometria", "Financeiro", "Pasta Professor"
    ])
    st.sidebar.button("Sair", on_click=lambda: st.session_state.update({"perfil": None}))

    # FUNÇÕES ARITMÉTICAS (CONTAGEM DE DIVISORES)
    if menu == "Funções Aritméticas":
        st.header("🔍 Estudo da Função Divisor f(n)")
        st.latex(r"f(a \cdot b) = f(a) \cdot f(b) \text{ se } \text{mdc}(a,b)=1")
        
        n_input = st.number_input("Analise o número n:", min_value=1, value=12, key="fn_n")
        if st.button("Calcular Propriedades"):
            res = contar_divisores(n_input)
            divs = [i for i in range(1, n_input + 1) if n_input % i == 0]
            st.success(f"f({n_input}) = {res}")
            st.write(f"**Divisores:** {divs}")
            st.info("Classificação: Função Aritmética Multiplicativa (Baseada na Fatoração).")

    # FINANCEIRO (JUROS COMPOSTOS)
    elif menu == "Financeiro":
        st.header("💰 Matemática Financeira")
        st.latex(r"M = C(1+i)^t")
        
        c1, c2, c3 = st.columns(3)
        cap = c1.number_input("Capital:", value=1000.0, key="f_c")
        tax = c2.number_input("Taxa (%):", value=1.0, key="f_i") / 100
        tme = c3.number_input("Tempo:", value=12, key="f_t")
        if st.button("Calcular Montante"):
            st.metric("Montante Final", f"R$ {cap*(1+tax)**tme:.2f}")

    # LOGARITMOS
    elif menu == "Logaritmos":
        st.header("🔢 Logaritmos")
        st.latex(r"\log_{b}(a) = x")
        
        la = st.number_input("Logaritmando:", min_value=0.1, value=100.0, key="l_a")
        lb = st.number_input("Base:", min_value=0.1, value=10.0, key="l_b")
        if st.button("Calcular Log"):
            try: st.success(f"x = {math.log(la, lb):.4f}")
            except: st.error("Erro matemático.")

    # MATRIZES
    elif menu == "Matrizes (Sarrus)":
        st.header("🧮 Matrizes")
        
        ordem = st.selectbox("Ordem:", [2, 3], key="m_o")
        mat = []
        for i in range(ordem):
            cols = st.columns(ordem)
            mat.append([cols[j].number_input(f"A{i+1}{j+1}", value=float(i==j), key=f"m{i}{j}") for j in range(ordem)])
        if st.button("Calcular"):
            A = np.array(mat)
            det = np.linalg.det(A)
            st.write(f"Determinante: {det:.2f}")
            if abs(det) > 0.0001: st.write("Inversa:", np.linalg.inv(A))

    # SISTEMAS
    elif menu == "Sistemas Lineares":
        st.header("📏 Sistemas Lineares")
        
        ord_s = st.selectbox("Equações:", [2, 3], key="s_o")
        mA, vB = [], []
        for i in range(ord_s):
            cols = st.columns(ord_s + 1)
            mA.append([cols[j].number_input(f"A{i}{j}", value=float(i==j), key=f"sA{i}{j}") for j in range(ord_s)])
            vB.append(cols[ord_s].number_input(f"B{i}", value=1.0, key=f"sB{i}"))
        if st.button("Resolver"):
            try: st.success(f"Solução: {np.linalg.solve(np.array(mA), np.array(vB))}")
            except: st.error("Sistema Impossível.")

    # ÁLGEBRA E GEOMETRIA
    elif menu == "Álgebra e Geometria":
        st.subheader("🔍 Bhaskara")
        

[Image of the quadratic formula]

        c1, c2, c3 = st.columns(3)
        va = c1.number_input("a", value=1.0, key="al_a"); vb = c2.number_input("b", value=-5.0, key="al_b"); vc = c3.number_input("c", value=6.0, key="al_c")
        if st.button("Raízes"):
            d = vb**2 - 4*va*vc
            if d >= 0: st.write(f"x1: {(-vb+np.sqrt(d))/(2*va):.2f}, x2: {(-vb-np.sqrt(d))/(2*va):.2f}")
            else: st.error("Delta < 0")
        st.divider()
        st.subheader("📐 Pitágoras")
        

[Image of the Pythagorean theorem diagram]

        p1 = st.number_input("Cateto A", value=3.0, key="al_p1"); p2 = st.number_input("Cateto B", value=4.0, key="al_p2")
        if st.button("Hipotenusa"): st.success(f"H = {np.sqrt(p1**2 + p2**2):.2f}")

    # GERADOR
    elif menu == "Gerador de Listas":
        st.header("📝 Gerador de Exercícios")
        tema = st.selectbox("Tema:", ["Logaritmos", "Matrizes", "Função Divisor", "Financeiro"])
        if st.button("🚀 Gerar Atividade"):
            st.download_button("📥 Baixar PDF", gerar_material_pdf(tema, ["Questão 1..."], ["Gabarito 1..."]), f"{tema}.pdf")

    # DRIVE
    elif menu == "Pasta Professor":
        st.link_button("🚀 Abrir Google Drive", "COLE_LINK_AQUI")