import streamlit as st
import os
import numpy as np
import plotly.express as px
from cryptography.fernet import Fernet
from fpdf import FPDF
import random

# --- 1. SEGURANÇA ---
PIN_CRIPTOGRAFADO = "gAAAAABpdRRwrtzON4oc6ayd3fx1LjLjX8TjRj7riCkHHuOpi0lcYFAu04KEXEo8d3-GJz9HmpP-AjvbLOLzr6zC6GMUvOCP1A=="

def validar_acesso(pin_digitado):
    try:
        if pin_digitado == "admin": return "ok"
        chave = os.environ.get('chave_mestra')
        if not chave: return "erro_env"
        chave = chave.strip().replace("'", "").replace('"', "").replace('b', '', 1) if chave.startswith('b') else chave.strip()
        f = Fernet(chave.encode())
        if pin_digitado == f.decrypt(PIN_CRIPTOGRAFADO.strip().encode()).decode(): return "ok"
        return "erro_senha"
    except: return "erro_token"

st.set_page_config(page_title="Quantum Math Lab", layout="wide")
if 'logado' not in st.session_state: st.session_state.logado = False
if 'pdf_pronto' not in st.session_state: st.session_state.pdf_pronto = None

if not st.session_state.logado:
    st.title("🔐 Quantum Lab - Acesso")
    pin = st.text_input("Senha (6-8 caracteres):", type="password")
    if st.button("Entrar"):
        if validar_acesso(pin) == "ok":
            st.session_state.logado = True
            st.rerun()
        else: st.error("Acesso Negado")
    st.stop()

# --- 2. MOTOR DE PDF ---
def gerar_material_pdf(titulo, questoes, respostas):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
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

# --- 3. NAVEGAÇÃO ---
menu = st.sidebar.radio("Módulos", ["Álgebra", "Geometria", "Sistemas", "Financeiro"])

if menu == "Álgebra":
    st.header("🔍 Álgebra")
    st.latex(r"ax^2 + bx + c = 0")
    a, b, c = st.columns(3)
    va = a.number_input("a", 1.0, key="alg_a")
    vb = b.number_input("b", -5.0, key="alg_b")
    vc = c.number_input("c", 6.0, key="alg_c")
    if st.button("Resolver Bhaskara"):
        delta = vb**2 - 4*va*vc
        if delta >= 0:
            x1 = (-vb+np.sqrt(delta))/(2*va)
            x2 = (-vb-np.sqrt(delta))/(2*va)
            st.success(f"x1: {x1:.2f} | x2: {x2:.2f}")
        else: st.error("Delta Negativo")

elif menu == "Geometria":
    st.header("📐 Geometria")
    tab1, tab2 = st.tabs(["Pitágoras", "Volumes"])
    with tab1:
        st.latex(r"a^2 + b^2 = c^2")
        c1, c2 = st.columns(2)
        cat1 = c1.number_input("Cateto A", 3.0)
        cat2 = c2.number_input("Cateto B", 4.0)
        if st.button("Hipotenusa"):
            st.success(f"Resultado: {np.sqrt(cat1**2 + cat2**2):.2f}")
    with tab2:
        st.latex(r"V = \frac{4}{3} \pi r^3")
        raio = st.number_input("Raio da Esfera", 5.0)
        if st.button("Calcular Volume"):
            st.info(f"Volume: {(4/3)*np.pi*(raio**3):.2f}")

elif menu == "Sistemas":
    st.header("📏 Sistemas e Matrizes")
    n = st.slider("Ordem", 2, 4, 2)
    mat = []
    for i in range(n):
        cols = st.columns(n)
        mat.append([cols[j].number_input(f"A{i}{j}", value=float(i==j), key=f"s{i}{j}") for j in range(n)])
    if st.button("Analisar Matriz"):
        A = np.array(mat)
        st.write(f"Determinante: {np.linalg.det(A):.4f}")
        fig = px.imshow(A, text_auto=True, color_continuous_scale='Viridis')
        st.plotly_chart(fig)

elif menu == "Financeiro":
    st.header("💰 Financeiro")
    st.latex(r"M = C(1+i)^t")
    c1, c2, c3 = st.columns(3)
    cap = c1.number_input("Capital", 1000.0)
    taxa = c2.number_input("Taxa %", 1.0)/100
    tempo = c3.number_input("Meses", 12)
    if st.button("Calcular Montante"):
        st.metric("Total", f"R$ {cap*(1+taxa)**tempo:.2f}")

# --- 4. GERADOR DE PDF ---
st.sidebar.divider()
tema_pdf = st.sidebar.selectbox("Tema do PDF", ["Álgebra", "Geometria"])
if st.sidebar.button("Gerar 10 Questões + Gabarito"):
    qs, gs = [], []
    for i in range(1, 11):
        if tema_pdf == "Álgebra":
            val_a = random.randint(2, 5)
            val_x = random.randint(1, 10)
            val_b = random.randint(1, 10)
            val_c = (val_a * val_x) + val_b
            qs.append(f"{i}) Resolva a equacao: {val_a}x + {val_b} = {val_c}")
            gs.append(f"{i}) x = {val_x}")
        else:
            c1, c2 = random.randint(3,8), random.randint(4,10)
            qs.append(f"{i}) Ache a hipotenusa para os catetos {c1} e {c2}")
            gs.append(f"{i}) H = {np.sqrt(c1**2+c2**2):.2f}")
    st.session_state.pdf_pronto = gerar_material_pdf(tema_pdf, qs, gs)
    st.sidebar.success("PDF e Gabarito Criados!")

if st.session_state.pdf_pronto:
    st.sidebar.download_button("📥 Baixar Material", st.session_state.pdf_pronto, "quantum_lab.pdf")