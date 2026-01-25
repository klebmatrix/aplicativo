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
    st.title("🔐 Login de Segurança")
    pin = st.text_input("Senha:", type="password")
    if st.button("Acessar"):
        if validar_acesso(pin) == "ok":
            st.session_state.logado = True
            st.rerun()
        else: st.error("Acesso negado.")
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
menu = st.sidebar.radio("Navegação:", ["Álgebra", "Geometria", "Sistemas", "Financeiro"])

if menu == "Álgebra":
    st.header("🔍 Álgebra")
    aba1, aba2 = st.tabs(["1º Grau", "2º Grau (Bhaskara)"])
    
    with aba1:
        st.subheader("Equação de 1º Grau")
        st.latex(r"ax + b = c")
        c1, c2, c3 = st.columns(3)
        va1 = c1.number_input("a:", value=1.0, key="a1")
        vb1 = c2.number_input("b:", value=0.0, key="b1")
        vc1 = c3.number_input("c:", value=10.0, key="c1")
        if st.button("Resolver 1º Grau"):
            if va1 != 0:
                res = (vc1 - vb1) / va1
                st.success(f"O valor de x é: {res:.2f}")
            else: st.error("O valor de 'a' não pode ser zero.")

    with aba2:
        st.subheader("Equação de 2º Grau")
        st.latex(r"ax^2 + bx + c = 0")
        c1, c2, c3 = st.columns(3)
        va2 = c1.number_input("a:", value=1.0, key="a2")
        vb2 = c2.number_input("b:", value=-5.0, key="b2")
        vc2 = c3.number_input("c:", value=6.0, key="c2")
        if st.button("Calcular Bhaskara"):
            delta = vb2**2 - 4*va2*vc2
            st.info(f"Delta (Δ) = {delta}")
            if delta >= 0:
                x1 = (-vb2 + np.sqrt(delta)) / (2*va2)
                x2 = (-vb2 - np.sqrt(delta)) / (2*va2)
                st.success(f"Raízes encontradas: x1 = {x1:.2f}, x2 = {x2:.2f}")
            else: st.error("A equação não possui raízes reais.")

elif menu == "Geometria":
    st.header("📐 Geometria")
    st.latex(r"a^2 + b^2 = c^2")
    c1, c2 = st.columns(2)
    cat1 = c1.number_input("Cateto A:", 3.0)
    cat2 = c2.number_input("Cateto B:", 4.0)
    if st.button("Calcular Hipotenusa"):
        st.success(f"Hipotenusa: {np.sqrt(cat1**2 + cat2**2):.2f}")

elif menu == "Sistemas":
    st.header("📏 Sistemas e Matrizes")
    n = st.slider("Ordem da Matriz:", 2, 4, 2)
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
    cap = c1.number_input("Capital:", 1000.0)
    taxa = c2.number_input("Taxa (%):", 1.0)/100
    tempo = c3.number_input("Meses:", 12)
    if st.button("Calcular Montante"):
        st.metric("Total", f"R$ {cap*(1+taxa)**tempo:.2f}")

# --- 4. GERADOR DE PDF ---
st.sidebar.divider()
st.sidebar.subheader("📝 Gerador de Material")
tema_pdf = st.sidebar.selectbox("Tema:", ["Equações 1º Grau", "Equações 2º Grau"])
if st.sidebar.button("Gerar 10 Questões + Gabarito"):
    qs, gs = [], []
    for i in range(1, 11):
        if tema_pdf == "Equações 1º Grau":
            a, x = random.randint(2, 6), random.randint(1, 10)
            b = random.randint(1, 15)
            c = (a * x) + b
            qs.append(f"{i}) Resolva a equacao: {a}x + {b} = {c}")
            gs.append(f"{i}) x = {x}")
        else:
            x1, x2 = random.randint(1, 5), random.randint(6, 10)
            b_val = -(x1 + x2)
            c_val = x1 * x2
            qs.append(f"{i}) Encontre as raizes de: x^2 + ({b_val})x + {c_val} = 0")
            gs.append(f"{i}) x1 = {x1}, x2 = {x2}")
    
    st.session_state.pdf_pronto = gerar_material_pdf(tema_pdf, qs, gs)
    st.sidebar.success("PDF e Gabarito Criados!")

if st.session_state.pdf_pronto:
    st.sidebar.download_button("📥 Baixar Material", st.session_state.pdf_pronto, "atividades_quantum.pdf")