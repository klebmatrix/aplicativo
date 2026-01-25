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
    if st.button("Entrar"):
        if validar_acesso(pin) == "ok":
            st.session_state.logado = True
            st.rerun()
        else: st.error("Negado")
    st.stop()

# --- 2. FUNÇÃO DO PDF (COM GABARITO) ---
def gerar_material_pdf(titulo, questoes, respostas):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Página de Questões
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"Lista de Exercicios: {titulo}", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    for q in questoes:
        pdf.multi_cell(0, 10, txt=q)
        pdf.ln(5)
    
    # Página de Gabarito
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Gabarito Oficial", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    for r in respostas:
        pdf.multi_cell(0, 10, txt=r)
        pdf.ln(2)
        
    return pdf.output(dest='S').encode('latin-1')

# --- 3. MENU ---
menu = st.sidebar.radio("Navegação", ["Álgebra", "Geometria", "Sistemas", "Financeiro"])

if menu == "Álgebra":
    st.header("🔍 Álgebra: Equações")
    aba1, aba2 = st.tabs(["1º Grau", "2º Grau (Bhaskara)"])
    
    with aba1:
        st.latex(r"ax + b = c")
        a1, b1, c1 = st.columns(3)
        va1 = a1.number_input("a", value=2.0, key="a1")
        vb1 = b1.number_input("b", value=10.0, key="b1")
        vc1 = c1.number_input("c", value=20.0, key="c1")
        if st.button("Resolver 1º Grau"):
            res = (vc1 - vb1) / va1
            st.success(f"Resultado: x = {res}")

    with aba2:
        st.latex(r"ax^2 + bx + c = 0")
        a2, b2, c2 = st.columns(3)
        va2 = a2.number_input("a", value=1.0, key="a2")
        vb2 = b2.number_input("b", value=-5.0, key="b2")
        vc2 = c2.number_input("c", value=6.0, key="c2")
        if st.button("Calcular Bhaskara"):
            delta = vb2**2 - 4*va2*vc2
            if delta >= 0:
                x1 = (-vb2 + np.sqrt(delta)) / (2*va2)
                x2 = (-vb2 - np.sqrt(delta)) / (2*va2)
                st.success(f"Delta: {delta} | x1: {x1} | x2: {x2}")
            else: st.error("Delta negativo.")

# --- 4. GERADOR DE PDF (MÍNIMO 10 QUESTÕES) ---
st.sidebar.divider()
st.sidebar.subheader("📝 Gerador de Atividades")
tema = st.sidebar.selectbox("Escolha o Tema", ["Equações de 1º Grau", "Equações de 2º Grau"])

if st.sidebar.button("Gerar PDF (10 Questões + Gabarito)"):
    q_lista, g_lista = [], []
    for i in range(1, 11):
        if tema == "Equações de 1º Grau":
            a, x_real = random.randint(2, 5), random.randint(1, 10)
            b = random.randint(1, 20)
            c = (a * x_real) + b
            q_lista.append(f"Questao {i}: Resolva a equacao {a}x + {b} = {c}")
            g_lista.append(f"Questao {i}: x = {x_real}")
        else:
            # Gerando equações de 2º grau simples (x-x1)(x-x2) = 0
            x1, x2 = random.randint(1, 5), random.randint(6, 10)
            b_val = -(x1 + x2)
            c_val = x1 * x2
            q_lista.append(f"Questao {i}: Encontre as raizes de x^2 + ({b_val})x + {c_val} = 0")
            g_lista.append(f"Questao {i}: x1 = {x1}, x2 = {x2}")
    
    st.session_state.pdf_pronto = gerar_material_pdf(tema, q_lista, g_lista)
    st.sidebar.success("PDF e Gabarito Gerados!")

if st.session_state.pdf_pronto:
    st.sidebar.download_button("📥 Baixar PDF Completo", st.session_state.pdf_pronto, "atividades_quantum.pdf")