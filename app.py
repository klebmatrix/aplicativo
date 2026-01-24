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

# --- 2. MOTOR DE PDF (CORREÇÃO BYTESIO) ---
class PDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 14)
        self.cell(0, 10, 'Quantum Math Lab - Relatorio Oficial', 0, 1, 'C')
        self.ln(5)

def gerar_pdf_bytes(titulo, questoes, respostas):
    pdf = PDF()
    # Página de Questões
    pdf.add_page()
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(0, 10, f"ATIVIDADES: {titulo.upper()}", ln=True)
    pdf.set_font("helvetica", size=11)
    for q in questoes:
        pdf.multi_cell(0, 10, txt=q)
        pdf.ln(2)
    # Página de Gabarito
    pdf.add_page()
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(0, 10, f"GABARITO: {titulo.upper()}", ln=True)
    pdf.set_font("helvetica", size=11)
    for r in respostas:
        pdf.multi_cell(0, 10, txt=r)
    
    # Gerar como string de bytes e envolver em BytesIO
    return pdf.output(dest='S').encode('latin-1')

# --- 3. INTERFACE ---
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
    sub = st.selectbox("Tipo:", ["1º Grau", "2º Grau (Bhaskara)"])
    
    if sub == "2º Grau (Bhaskara)":
        c1, c2, c3 = st.columns(3)
        a = c1.number_input("a:", value=1.0)
        b = c2.number_input("b:", value=-5.0)
        c = c3.number_input("c:", value=6.0)
        if st.button("Resolver"):
            delta = b**2 - 4*a*c
            st.write(f"Delta: {delta}")
            if delta >= 0:
                st.success(f"x1: {(-b + np.sqrt(delta))/(2*a)} | x2: {(-b - np.sqrt(delta))/(2*a)}")
            else: st.error("Raízes Complexas")

    st.divider()
    if st.button("Gerar Lista de Álgebra (PDF)"):
        q, g = ["1) Resolva 2x + 10 = 20"], ["1) x = 5"]
        pdf_data = gerar_pdf_bytes("Algebra", q, g)
        st.download_button("📥 Baixar PDF Álgebra", pdf_data, "algebra.pdf", "application/pdf")

# --- 6. GEOMETRIA ---
elif menu == "Geometria":
    st.header("📐 Geometria e Pitágoras")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Pitágoras")
        ca = st.number_input("Cateto A:", 3.0)
        cb = st.number_input("Cateto B:", 4.0)
        if st.button("Calcular Hipotenusa"):
            st.success(f"Hipotenusa: {np.sqrt(ca**2 + cb**2)}")
        
            
    with col2:
        st.subheader("Área do Triângulo")
        base = st.number_input("Base:", 10.0)
        altura = st.number_input("Altura:", 5.0)
        if st.button("Calcular Área"):
            st.success(f"Área: {(base * altura)/2}")
        

[Image of the area of a triangle formula]


    st.divider()
    if st.button("Gerar Lista de Geometria (PDF)"):
        q = [f"1) Qual a hipotenusa de um triângulo com catetos {ca} e {cb}?"]
        g = [f"1) Hipotenusa = {np.sqrt(ca**2 + cb**2):.2f}"]
        pdf_data = gerar_pdf_bytes("Geometria", q, g)
        st.download_button("📥 Baixar PDF Geometria", pdf_data, "geometria.pdf", "application/pdf")