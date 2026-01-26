import streamlit as st
import os
import numpy as np
from cryptography.fernet import Fernet
from fpdf import FPDF
import random
import math

# --- 1. SEGURANÇA E AMBIENTE ---
# PIN de 6 dígitos configurado [cite: 2026-01-19]
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

# --- 4. ÁREA ADMIN ---
elif st.session_state.perfil == "admin":
    st.sidebar.title("🛠 Painel Professor")
    menu = st.sidebar.radio("Navegação", [
        "Gerador de Listas", "Logaritmos", "Matrizes (Sarrus)", 
        "Sistemas Lineares", "Álgebra (Bhaskara)", 
        "Geometria (Pitágoras)", "Financeiro", "Pasta Professor"
    ])
    st.sidebar.button("Sair", on_click=lambda: st.session_state.update({"perfil": None}))

    # LOGARITMOS
    if menu == "Logaritmos":
        st.header("🔢 Calculadora de Logaritmos")
        st.latex(r"\log_{b}(a) = x")
        c1, c2 = st.columns(2)
        la = c1.number_input("Logaritmando (a):", min_value=0.1, value=100.0, key="l_a")
        lb = c2.number_input("Base (b):", min_value=0.1, value=10.0, key="l_b")
        if st.button("Calcular"):
            try: st.success(f"Resultado: {math.log(la, lb):.4f}")
            except: st.error("Cálculo impossível.")

    # MATRIZES
    elif menu == "Matrizes (Sarrus)":
        st.header("🧮 Matriz e Determinante")
        ordem = st.selectbox("Ordem:", [2, 3], key="m_ord")
        mat_M = []
        for i in range(ordem):
            cols = st.columns(ordem)
            mat_M.append([cols[j].number_input(f"A{i+1}{j+1}", value=float(i==j), key=f"mat_{i}_{j}") for j in range(ordem)])
        if st.button("Executar Cálculo"):
            A = np.array(mat_M)
            det = np.linalg.det(A)
            st.write(f"**Determinante:** {det:.2f}")
            if abs(det) > 0.0001: st.write("**Inversa:**", np.linalg.inv(A))

    # SISTEMAS
    elif menu == "Sistemas Lineares":
        st.header("📏 Sistemas Ax = B")
        ord_s = st.selectbox("Equações:", [2, 3], key="s_ord")
        mA, vB = [], []
        for i in range(ord_s):
            cols = st.columns(ord_s + 1)
            mA.append([cols[j].number_input(f"A{i}{j}", value=float(i==j), key=f"sA{i}{j}") for j in range(ord_s)])
            vB.append(cols[ord_s].number_input(f"B{i}", value=1.0, key=f"sB{i}"))
        if st.button("Resolver"):
            try: st.success(f"Solução: {np.linalg.solve(np.array(mA), np.array(vB))}")
            except: st.error("Sistema sem solução única.")

    # ÁLGEBRA
    elif menu == "Álgebra (Bhaskara)":
        st.header("🔍 Equação de 2º Grau")
        ca, cb, cc = st.columns(3)
        va = ca.number_input("a", value=1.0, key="b_a"); vb = cb.number_input("b", value=-5.0, key="b_b"); vc = cc.number_input("c", value=6.0, key="b_c")
        if st.button("Calcular"):
            d = vb**2 - 4*va*vc
            if d >= 0: st.success(f"x1: {(-vb+np.sqrt(d))/(2*va):.2f}, x2: {(-vb-np.sqrt(d))/(2*va):.2f}")
            else: st.error("Sem raízes reais.")

    # GEOMETRIA
    elif menu == "Geometria (Pitágoras)":
        st.header("📐 Pitágoras")
        p1 = st.number_input("Cateto A", value=3.0, key="p_a"); p2 = st.number_input("Cateto B", value=4.0, key="p_b")
        if st.button("Calcular"): st.success(f"Hipotenusa: {np.sqrt(p1**2 + p2**2):.2f}")

    # GERADOR
    elif menu == "Gerador de Listas":
        st.header("📝 Criador de PDF")
        tema = st.selectbox("Tema:", ["Logaritmos", "Matrizes", "Bhaskara", "Pitágoras"])
        if st.button("🚀 Gerar PDF"):
            qs, gs = [f"Questão 1: Calcule o valor de {tema}"], ["Resposta 1"]
            st.download_button("📥 Baixar Atividade", gerar_material_pdf(tema, qs, gs), f"{tema}.pdf")

    # DRIVE
    elif menu == "Pasta Professor":
        st.header("📂 Drive")
        st.link_button("🚀 Abrir Google Drive", "COLE_LINK_AQUI")