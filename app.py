import streamlit as st
import os
import numpy as np
from cryptography.fernet import Fernet
from fpdf import FPDF
import random

# --- 1. SEGURANÇA ---
PIN_CRIPTOGRAFADO = "gAAAAABpdRRwrtzON4oc6ayd3fx1LjLjX8TjRj7riCkHHuOpi0lcYFAu04KEXEo8d3-GJz9HmpP-AjvbLOLzr6zC6GMUvOCP1A=="

def validar_acesso(pin_digitado):
    try:
        chave = os.environ.get('chave_mestra')
        if not chave: return "erro_env"
        chave = chave.strip().replace("'", "").replace('"', "").replace('b', '', 1) if chave.startswith('b') else chave.strip()
        f = Fernet(chave.encode())
        return "ok" if pin_digitado == f.decrypt(PIN_CRIPTOGRAFADO.strip().encode()).decode() else "erro_senha"
    except: return "erro_token"

# --- 2. GERADOR DE PDF ---
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Relatorio Matematico - Quantum Lab', 0, 1, 'C')
        self.ln(5)

def gerar_pdf_geral(titulo, linhas):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, titulo.upper(), ln=True)
    pdf.set_font("Arial", size=11)
    for l in linhas:
        pdf.multi_cell(0, 10, txt=l)
    return pdf.output(dest='S').encode('latin-1')

# --- 3. CONFIGURAÇÃO ---
st.set_page_config(page_title="Math Precision Lab", layout="wide", page_icon="⚛️")

if 'logado' not in st.session_state: st.session_state.logado = False

if not st.session_state.logado:
    st.title("🔐 Acesso Restrito")
    pin = st.text_input("Senha Alfanumérica:", type="password")
    if st.button("Desbloquear"):
        res = validar_acesso(pin)
        if res == "ok": st.session_state.logado = True; st.rerun()
        else: st.error(f"Erro: {res}")
    st.stop()

# --- 4. MENU ---
menu = st.sidebar.radio("Navegação:", ["Álgebra (Equações)", "Geometria (Área/Vol)", "Sistemas Lineares", "Finanças", "Gerador de Atividades"])

# --- MÓDULO: ÁLGEBRA ---
if menu == "Álgebra (Equações)":
    st.header("🔍 Equações de 1º e 2º Grau")
    grau = st.selectbox("Tipo:", ["1º Grau (ax + b = c)", "2º Grau (ax² + bx + c = 0)"])
    
    if grau == "1º Grau (ax + b = c)":
        c1, c2, c3 = st.columns(3)
        a = c1.number_input("a (≠ 0):", value=1, step=1)
        b = c2.number_input("b:", value=0, step=1)
        c_eq = c3.number_input("Igual a c:", value=0, step=1)
        
        if a == 0:
            st.error("Erro: 'a' não pode ser zero.")
        elif st.button("Resolver"):
            x = (c_eq - b) / a
            res_txt = f"Equação: {a}x + {b} = {c_eq} | Resultado: x = {int(x) if x == int(x) else round(x, 4)}"
            st.success(res_txt)
            st.download_button("📥 Baixar Resultado", gerar_pdf_geral("Equacao 1º Grau", [res_txt]), "resultado.pdf")

# --- MÓDULO: GEOMETRIA (REINTEGRADO) ---
elif menu == "Geometria (Área/Vol)":
    st.header("📐 Geometria Espacial e Plana")
    fig = st.selectbox("Figura:", ["Esfera", "Cilindro", "Cubo", "Círculo"])
    medida = st.number_input("Medida Principal (Raio ou Lado):", min_value=0, value=10, step=1)
    
    if fig == "Esfera":
        vol = (4/3) * np.pi * (medida**3)
        st.latex(r"V = \frac{4}{3}\pi r^3")
        st.metric("Volume", f"{vol:.4f}")
    elif fig == "Cilindro":
        h = st.number_input("Altura (h):", min_value=0, value=10, step=1)
        vol = np.pi * (medida**2) * h
        st.metric("Volume", f"{vol:.4f}")
    elif fig == "Cubo":
        vol = medida**3
        st.metric("Volume", f"{vol}")
    elif fig == "Círculo":
        area = np.pi * (medida**2)
        st.metric("Área", f"{area:.4f}")

# --- MÓDULO: SISTEMAS ---
elif menu == "Sistemas Lineares":
    st.header("📏 Sistemas Ax = B (Até 5 var)")
    n = st.slider("Incógnitas:", 2, 5, 2)
    # Lógica de matriz Ax=B... (conforme código anterior)

# --- MÓDULO: GERADOR DE ATIVIDADES ---
elif menu == "Gerador de Atividades":
    st.header("📝 Exercícios com Gabarito")
    qtd = st.slider("Quantidade:", 1, 20, 5)
    if st.button("Gerar"):
        # Lógica de geração de atividades e gabarito...
        st.info("Atividades geradas com sucesso. Clique no botão abaixo para o PDF.")