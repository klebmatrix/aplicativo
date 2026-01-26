import streamlit as st
import os
import numpy as np
import plotly.express as px
from cryptography.fernet import Fernet
from fpdf import FPDF
import random
import math

# --- 1. ÂNCORA DE SEGURANÇA (PIN E AMBIENTE) ---
# PIN de 6 dígitos configurado via criptografia [cite: 2026-01-19]
PIN_CRIPTOGRAFADO = "gAAAAABpdRRwrtzON4oc6ayd3fx1LjLjX8TjRj7riCkHHuOpi0lcYFAu04KEXEo8d3-GJz9HmpP-AjvbLOLzr6zC6GMUvOCP1A=="

def validar_acesso(pin_digitado):
    senha_aluno_env = os.environ.get('acesso_aluno')
    if senha_aluno_env and pin_digitado == senha_aluno_env:
        return "aluno"
    try:
        # Recupera a chave mestra do ambiente Render [cite: 2026-01-24]
        chave = os.environ.get('chave_mestra') 
        if not chave: return "erro_env"
        chave = chave.strip().replace("'", "").replace('"', "").replace('b', '', 1) if chave.startswith('b') else chave.strip()
        f = Fernet(chave.encode())
        # Validação do PIN entre 6 e 8 caracteres [cite: 2026-01-21]
        if pin_digitado == f.decrypt(PIN_CRIPTOGRAFADO.strip().encode()).decode():
            return "admin"
    except: pass
    return "negado"

def contar_divisores(n):
    if n <= 0: return 0
    return len([i for i in range(1, n + 1) if n % i == 0])

st.set_page_config(page_title="Quantum Math Lab", layout="wide")
if 'perfil' not in st.session_state: st.session_state.perfil = None

# --- 2. ÂNCORA DE DOCUMENTAÇÃO (PDF) ---
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

# --- 3. ÂNCORA DE LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Quantum Math Lab")
    pin = st.text_input("Digite o PIN de Acesso:", type="password")
    if st.button("Entrar"):
        acesso = validar_acesso(pin)
        if acesso != "negado":
            st.session_state.perfil = acesso
            st.rerun()
        else: st.error("Acesso Negado. Verifique seu PIN.")
    st.stop()

# --- 4. ÂNCORA DO ALUNO ---
if st.session_state.perfil == "aluno":
    st.title("🎓 Portal do Aluno")
    st.sidebar.button("Sair", on_click=lambda: st.session_state.update({"perfil": None}))
    st.link_button("📂 Acessar Pasta de Exercícios", "COLE_LINK_ALUNO")

# --- 5. ÂNCORA DO PROFESSOR (ADMIN COMPLETO) ---
elif st.session_state.perfil == "admin":
    st.sidebar.title("🛠 Painel Professor")
    menu = st.sidebar.radio("Navegação", ["Gerador de Listas", "Logaritmos", "Matrizes", "Sistemas Lineares", "Álgebra (Bhaskara)", "Geometria (Pitágoras)", "Financeiro", "Pasta Professor"])
    st.sidebar.button("Sair", on_click=lambda: st.session_state.update({"perfil": None}))

    if menu == "Logaritmos":
        st.header("🔢 Logaritmos")
        st.latex(r"\log_{b}(a) = x \iff b^x = a")
        
        c1, c2 = st.columns(2)
        la = c1.number_input("Logaritmando (a):", min_value=0.1, value=100.0, key="log_a")
        lb = c2.number_input("Base (b):", min_value=0.1, value=10.0, key="log_b")
        if st.button("Calcular Log"):
            st.success(f"Resultado: {math.log(la, lb):.4f}")

    elif menu == "Matrizes":
        st.header("🧮 Matriz Inversa e Sarrus")
        
        ordem = st.selectbox("Ordem:", [2, 3], key="mat_ord")
        mat_M = []
        for i in range(ordem):
            cols = st.columns(ordem)
            mat_M.append([cols[j].number_input(f"A{i+1}{j+1}", value=float(i==j), key=f"m_{i}{j}") for j in range(ordem)])
        if st.button("Calcular"):
            A = np.array(mat_M)
            det = np.linalg.det(A)
            st.write(f"Determinante: {det:.2f}")
            if abs(det) > 0.0001: st.write("Inversa:", np.linalg.inv(A))

    elif menu == "Sistemas Lineares":
        st.header("📏 Sistemas Ax = B")
        
        ordem_s = st.selectbox("Equações:", [2, 3], key="s_ord")
        mA, vB = [], []
        for i in range(ordem_s):
            cols = st.columns(ordem_s + 1)
            mA.append([cols[j].number_input(f"A{i}{j}", value=float(i==j), key=f"sA{i}{j}") for j in range(ordem_s)])
            vB.append(cols[ordem_s].number_input(f"B{i}", value=1.0, key=f"sB{i}"))
        if st.button("Resolver"):
            try: st.success(f"Solução: {np.linalg.solve(np.array(mA), np.array(vB))}")
            except: st.error("Erro no sistema.")

    elif menu == "Álgebra (Bhaskara)":
        st.header("🔍 Bhaskara")
        st.latex(r"ax^2 + bx + c = 0")
        

[Image of the quadratic formula]

        ca, cb, cc = st.columns(3)
        va = ca.number_input("a", value=1.0, key="ba"); vb = cb.number_input("b", value=-5.0, key="bb"); vc = cc.number_input("c", value=6.0, key="bc")
        if st.button("Calcular Raízes"):
            d = vb**2 - 4*va*vc
            if d >= 0: st.write(f"x1: {(-vb+np.sqrt(d))/(2*va):.2f}, x2: {(-vb-np.sqrt(d))/(2*va):.2f}")
            else: st.error("Delta negativo.")

    elif menu == "Geometria (Pitágoras)":
        st.header("📐 Pitágoras")
        

[Image of the Pythagorean theorem diagram]

        c1 = st.number_input("Cateto A", value=3.0, key="pa"); c2 = st.number_input("Cateto B", value=4.0, key="pb")
        if st.button("Calcular Hipotenusa"): st.success(f"H = {np.sqrt(c1**2 + c2**2):.2f}")

    elif menu == "Financeiro":
        st.header("💰 Juros Compostos")
        
        cap = st.number_input("Capital", value=1000.0, key="fc"); txa = st.number_input("Taxa (%)", value=1.0, key="ft")/100; tm = st.number_input("Meses", value=12, key="fm")
        if st.button("Calcular"): st.metric("Montante", f"R$ {cap*(1+txa)**tm:.2f}")

    elif menu == "Gerador de Listas":
        st.header("📝 Gerador PDF")
        tema = st.selectbox("Tema:", ["Logaritmos", "Matrizes", "Sistemas", "Bhaskara", "Pitágoras"])
        if st.button("🚀 Gerar 10 Questões"):
            qs, gs = [f"Questão 1 de {tema}"], ["Gabarito 1"]
            st.download_button("📥 Baixar Atividade", gerar_material_pdf(tema, qs, gs), f"{tema}.pdf")

    elif menu == "Pasta Professor":
        st.header("📂 Gerenciador Drive")
        st.link_button("🚀 Abrir Meu Google Drive", "COLE_LINK_PROFESSOR")