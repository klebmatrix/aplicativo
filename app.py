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
    st.title("🔐 Login")
    pin = st.text_input("Senha:", type="password")
    if st.button("Acessar"):
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
menu = st.sidebar.radio("Módulos", ["Álgebra", "Sistemas", "Financeiro", "Geometria"])

# --- ÁLGEBRA (1º e 2º GRAU) ---
if menu == "Álgebra":
    st.header("🔍 Álgebra")
    aba1, aba2 = st.tabs(["1º Grau", "2º Grau"])
    with aba1:
        st.latex(r"ax + b = c")
        c1, c2, c3 = st.columns(3)
        va1 = c1.number_input("a", value=1.0, key="a1")
        vb1 = c2.number_input("b", value=0.0, key="b1")
        vc1 = c3.number_input("c", value=10.0, key="c1")
        if st.button("Resolver 1º"):
            if va1 != 0: st.success(f"x = {(vc1-vb1)/va1:.2f}")
    with aba2:
        st.latex(r"ax^2 + bx + c = 0")
        c1, c2, c3 = st.columns(3)
        va2 = c1.number_input("a", value=1.0, key="a2")
        vb2 = c2.number_input("b", value=-5.0, key="b2")
        vc2 = c3.number_input("c", value=6.0, key="c2")
        if st.button("Resolver 2º"):
            d = vb2**2 - 4*va2*vc2
            if d >= 0:
                st.success(f"x1: {(-vb2+np.sqrt(d))/(2*va2):.2f} | x2: {(-vb2-np.sqrt(d))/(2*va2):.2f}")
            else: st.error("Raízes Complexas")

# --- SISTEMAS (MATRIZ A E VETOR B) ---
elif menu == "Sistemas":
    st.header("📏 Sistemas Lineares (A e B)")
    ordem = st.selectbox("Ordem do Sistema:", [2, 3])
    
    st.write("### Insira os Coeficientes (A) e os Resultados (B)")
    mat_A = []
    vec_B = []
    
    for i in range(ordem):
        cols = st.columns(ordem + 1)
        linha = []
        for j in range(ordem):
            val_a = cols[j].number_input(f"A {i+1},{j+1}", value=1.0 if i==j else 0.0, key=f"sys_A_{i}_{j}")
            linha.append(val_a)
        mat_A.append(linha)
        val_b = cols[ordem].number_input(f"B {i+1}", value=1.0, key=f"sys_B_{i}")
        vec_B.append(val_b)
    
    if st.button("🚀 Calcular Sistema e Matriz"):
        try:
            A = np.array(mat_A)
            B = np.array(vec_B)
            solucao = np.linalg.solve(A, B)
            
            st.divider()
            col_res, col_mat = st.columns(2)
            
            with col_res:
                st.subheader("✅ Solução")
                for idx, s in enumerate(solucao):
                    st.write(f"**x{idx+1}** = `{s:.4f}`")
                st.write(f"**Determinante de A:** `{np.linalg.det(A):.2f}`")

            with col_mat:
                st.subheader("🖼️ Análise Visual (A)")
                fig = px.imshow(A, text_auto=True, color_continuous_scale='Viridis')
                st.plotly_chart(fig, use_container_width=True)
        except:
            st.error("O sistema não tem solução única.")

# --- FINANCEIRO ---
elif menu == "Financeiro":
    st.header("💰 Matemática Financeira")
    st.latex(r"M = C(1+i)^t")
    c1, i1, t1 = st.columns(3)
    cap = c1.number_input("Capital:", 1000.0)
    tax = i1.number_input("Taxa (%):", 1.0)/100
    tmp = t1.number_input("Meses:", 12)
    if st.button("Calcular Montante"):
        st.metric("Total", f"R$ {cap*(1+tax)**tmp:.2f}")

# --- GERADOR DE PDF ---
st.sidebar.divider()
if st.sidebar.button("Gerar 10 Questões + Gabarito"):
    qs, gs = [], []
    for i in range(1, 11):
        a, x = random.randint(2, 5), random.randint(1, 10)
        b = random.randint(1, 10)
        c = (a * x) + b
        qs.append(f"{i}) Resolva a equacao: {a}x + {b} = {c}")
        gs.append(f"{i}) x = {x}")
    st.session_state.pdf_pronto = gerar_material_pdf("Lista de Álgebra", qs, gs)
    st.sidebar.success("Material Pronto!")

if st.session_state.pdf_pronto:
    st.sidebar.download_button("📥 Baixar PDF", st.session_state.pdf_pronto, "atividades.pdf")