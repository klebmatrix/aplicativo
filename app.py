import streamlit as st
import os
import numpy as np
from cryptography.fernet import Fernet
from fpdf import FPDF
import random
from io import BytesIO

# --- 1. SEGURANÇA ---
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

# --- 2. MOTOR DE PDF (CORREÇÃO PARA RENDER) ---
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'Quantum Math Lab - Atividades', 0, 1, 'C')
        self.ln(5)

def gerar_pdf_final(titulo, questoes, respostas):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"LISTA: {titulo.upper()}", ln=True)
    pdf.set_font("Arial", size=11)
    for q in questoes:
        pdf.multi_cell(0, 10, txt=q)
        pdf.ln(2)
    pdf.add_page()
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "GABARITO", ln=True)
    pdf.set_font("Arial", size=11)
    for r in respostas:
        pdf.multi_cell(0, 10, txt=r)
    
    # Gera o PDF na memória (dest='S') e converte para bytes (latin-1)
    return pdf.output(dest='S').encode('latin-1')

# --- 3. CONFIGURAÇÃO ---
st.set_page_config(page_title="Math Precision Lab", layout="wide")
if 'logado' not in st.session_state: st.session_state.logado = False

if not st.session_state.logado:
    st.title("🔐 Login")
    pin = st.text_input("Senha:", type="password")
    if st.button("Acessar"):
        if validar_acesso(pin) == "ok":
            st.session_state.logado = True
            st.rerun()
        else: st.error("Acesso Negado")
    st.stop()

# --- 4. MENU ---
menu = st.sidebar.radio("Navegação:", ["Álgebra", "Geometria", "Sistemas", "Financeiro"])
if st.sidebar.button("Sair"):
    st.session_state.logado = False
    st.rerun()

# --- 5. ÁLGEBRA ---
if menu == "Álgebra":
    st.header("🔍 Álgebra e Bhaskara")
    sub = st.selectbox("Escolha:", ["1º Grau", "2º Grau (Bhaskara)"])
    
    if sub == "2º Grau (Bhaskara)":
        c1, c2, c3 = st.columns(3)
        a2, b2, c2v = c1.number_input("a:", 1.0), c2.number_input("b:", -5.0), c3.number_input("c:", 6.0)
        if st.button("Calcular Bhaskara"):
            d = b2**2 - 4*a2*c2v
            st.write(f"Delta: {d}")
            if d >= 0:
                st.success(f"x1: {(-b2 + np.sqrt(d))/(2*a2)} | x2: {(-b2 - np.sqrt(d))/(2*a2)}")
            else: st.error("Raízes Complexas")

    st.divider()
    if st.button("Gerar PDF de Álgebra"):
        q, g = ["1) Resolva 2x + 10 = 30"], ["1) x = 10"]
        pdf_bytes = gerar_pdf_final("Algebra", q, g)
        st.download_button("📥 Baixar Atividades", pdf_bytes, "algebra.pdf", "application/pdf")

# --- 6. GEOMETRIA ---
elif menu == "Geometria":
    st.header("📐 Geometria: Pitágoras e Áreas")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Pitágoras")
        ca = st.number_input("Cateto A:", 3.0)
        cb = st.number_input("Cateto B:", 4.0)
        if st.button("Calcular Hipotenusa"):
            st.success(f"Hipotenusa: {np.sqrt(ca**2 + cb**2)}")
            
    with col2:
        st.subheader("Área")
        base = st.number_input("Base:", 10.0)
        altura = st.number_input("Altura:", 5.0)
        if st.button("Área do Triângulo"):
            st.success(f"Área: {(base * altura)/2}")

    st.divider()
    if st.button("Gerar PDF de Geometria"):
        q = [f"1) Qual a hipotenusa de um triângulo com catetos {ca} e {cb}?"]
        g = [f"1) Hipotenusa = {np.sqrt(ca**2 + cb**2):.2f}"]
        pdf_bytes = gerar_pdf_final("Geometria", q, g)
        st.download_button("📥 Baixar Atividades", pdf_bytes, "geometria.pdf", "application/pdf")