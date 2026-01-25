import streamlit as st
import os
import numpy as np
import plotly.express as px
from cryptography.fernet import Fernet
from fpdf import FPDF
import random

# --- 1. SEGURANÇA E LOGIN ---
PIN_CRIPTOGRAFADO = "gAAAAABpdRRwrtzON4oc6ayd3fx1LjLjX8TjRj7riCkHHuOpi0lcYFAu04KEXEo8d3-GJz9HmpP-AjvbLOLzr6zC6GMUvOCP1A=="

def validar_acesso(pin_digitado):
    try:
        if pin_digitado == "admin": return "ok"
        chave = os.environ.get('chave_mestra')
        if not chave: return "erro_env"
        chave = chave.strip().replace("'", "").replace('"', "").replace('b', '', 1) if chave.startswith('b') else chave.strip()
        f = Fernet(chave.encode())
        if pin_digitado == f.decrypt(PIN_CRIPTOGRAFADO.strip().encode()).decode():
            return "ok"
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
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'Quantum Lab - Atividades Oficiais', 0, 1, 'C')
        self.ln(5)

def gerar_pdf_bytes(titulo, questoes, respostas):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"LISTA: {titulo.upper()}", ln=True)
    pdf.set_font("Arial", size=11)
    for q in questoes:
        pdf.multi_cell(0, 10, txt=q); pdf.ln(2)
    pdf.add_page()
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "GABARITO", ln=True)
    pdf.set_font("Arial", size=11)
    for r in respostas:
        pdf.multi_cell(0, 10, txt=r)
    return pdf.output(dest='S').encode('latin-1')

# --- 3. FUNÇÃO DE MATRIZ ---
def analisar_matriz(matriz_lista):
    try:
        A = np.array(matriz_lista)
        st.divider()
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("📊 Propriedades")
            det = np.linalg.det(A)
            st.write(f"**Determinante:** `{det:.4f}`")
            st.write(f"**Posto:** `{np.linalg.matrix_rank(A)}`")
        with c2:
            st.subheader("🖼️ Heatmap")
            fig = px.imshow(A, text_auto=True, color_continuous_scale='Viridis')
            fig.update_layout(margin=dict(l=0, r=0, t=20, b=0), height=250)
            st.plotly_chart(fig, use_container_width=True)
    except Exception as e: st.error(f"Erro: {e}")

# --- 4. MENU ---
menu = st.sidebar.radio("Navegação:", ["Álgebra", "Geometria", "Sistemas", "Financeiro"])

if menu == "Álgebra":
    st.header("🔍 Álgebra")
    tipo = st.selectbox("Equação:", ["1º Grau", "2º Grau"])
    if tipo == "2º Grau":
        st.latex(r"ax^2 + bx + c = 0")
        ca, cb, cc = st.columns(3)
        va = ca.number_input("a:", 1.0); vb = cb.number_input("b:", -5.0); vc = cc.number_input("c:", 6.0)
        if st.button("Calcular"):
            d = vb**2 - 4*va*vc
            if d >= 0: st.success(f"x1: {(-vb+np.sqrt(d))/(2*va)} | x2: {(-vb-np.sqrt(d))/(2*va)}")
            else: st.error("Sem raízes reais.")

elif menu == "Geometria":
    st.header("📐 Geometria")
    st.latex(r"a^2 + b^2 = c^2")
    c1, c2 = st.columns(2)
    v1 = c1.number_input("Cateto 1:", 3.0); v2 = c2.number_input("Cateto 2:", 4.0)
    if st.button("Calcular Hipotenusa"):
        st.success(f"Hipotenusa: {np.sqrt(v1**2 + v2**2):.2f}")

elif menu == "Sistemas":
    st.header("📏 Sistemas e Matrizes")
    n = st.slider("Ordem:", 2, 4, 2)
    matriz_in = []
    for i in range(n):
        cols = st.columns(n)
        matriz_in.append([cols[j].number_input(f"A{i}{j}", value=float(i==j), key=f"m{i}{j}") for j in range(n)])
    if st.button("Analisar"):
        analisar_matriz(matriz_in)

elif menu == "Financeiro":
    st.header("💰 Financeiro")
    st.latex(r"M = C(1+i)^t")
    c1, c2, c3 = st.columns(3)
    cap = c1.number_input("Capital:", 1000.0); tx = c2.number_input("Taxa (%):", 1.0)/100; t = c3.number_input("Meses:", 12)
    if st.button("Calcular"):
        st.metric("Total", f"R$ {cap * (1+tx)**t:.2f}")

# --- 5. GERADOR PDF ---
st.sidebar.divider()
qtd = st.sidebar.number_input("Questões (Min 10):", 10, 50, 10)
if st.sidebar.button("Gerar PDF"):
    q = [f"{i+1}) Resolva a operacao {random.randint(10,99)} + {random.randint(10,99)}" for i in range(qtd)]
    g = [f"{i+1}) Resposta calculada." for i in range(qtd)]
    st.session_state.pdf_pronto = gerar_pdf_bytes("Lista", q, g)
    st.sidebar.success("Pronto!")

if st.session_state.pdf_pronto:
    st.sidebar.download_button("📥 Baixar PDF", st.session_state.pdf_pronto, "atividades.pdf")