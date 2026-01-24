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

# --- 2. CLASSE PDF ---
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'Quantum Math Lab - Relatorio de Atividades', 0, 1, 'C')
        self.ln(5)

def gerar_pdf_atividades(questoes, respostas):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "LISTA DE EXERCICIOS", ln=True)
    pdf.set_font("Arial", size=11)
    for q in questoes:
        pdf.multi_cell(0, 10, txt=q)
        pdf.ln(2)
    
    pdf.add_page()
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "GABARITO (RESPOSTAS)", ln=True)
    pdf.set_font("Arial", size=11)
    for r in respostas:
        pdf.multi_cell(0, 10, txt=r)
    return pdf.output(dest='S').encode('latin-1')

# --- 3. CONFIGURAÇÃO ---
st.set_page_config(page_title="Math Precision Lab", layout="wide")

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
menu = st.sidebar.radio("Navegação:", ["Álgebra (Equações)", "Geometria (Área/Vol)", "Sistemas Lineares", "Gerador de Atividades"])

# --- MÓDULO: ÁLGEBRA ---
if menu == "Álgebra (Equações)":
    st.header("🔍 Equação de 1º Grau: $ax + b = c$")
    c1, c2, c3 = st.columns(3)
    a = c1.number_input("a (Inteiro, ≠ 0):", value=1, step=1)
    b = c2.number_input("b (Inteiro):", value=0, step=1)
    c_eq = c3.number_input("Igual a c:", value=0, step=1)
    
    if a == 0:
        st.error("Pela definição matemática, 'a' deve ser diferente de zero.")
    elif st.button("Resolver"):
        x = (c_eq - b) / a
        res_txt = f"x = {int(x) if x == int(x) else round(x, 4)}"
        st.success(f"Equação: {a}x + {b} = {c_eq} | {res_txt}")

# --- MÓDULO: GEOMETRIA ---
elif menu == "Geometria (Área/Vol)":
    st.header("📐 Geometria Espacial e Plana")
    fig = st.selectbox("Escolha a Figura:", ["Esfera", "Cilindro", "Cubo", "Círculo"])
    r = st.number_input("Medida (Raio ou Lado):", min_value=0, value=10, step=1)
    
    if fig == "Esfera":
        vol = (4/3) * np.pi * (r**3)
        st.latex(r"V = \frac{4}{3}\pi r^3")
        st.metric("Volume da Esfera", f"{vol:.4f}")
    elif fig == "Cilindro":
        h = st.number_input("Altura (h):", min_value=0, value=10, step=1)
        vol = np.pi * (r**2) * h
        st.metric("Volume do Cilindro", f"{vol:.4f}")
    elif fig == "Cubo":
        vol = r**3
        st.metric("Volume do Cubo", f"{vol}")
    elif fig == "Círculo":
        area = np.pi * (r**2)
        st.metric("Área do Círculo", f"{area:.4f}")

# --- MÓDULO: ATIVIDADES ---
elif menu == "Gerador de Atividades":
    st.header("📝 Atividades com Gabarito")
    qtd = st.slider("Quantidade:", 1, 15, 5)
    
    if st.button("Gerar Nova Lista"):
        questoes, gabarito = [], []
        for i in range(qtd):
            tipo = random.choice(["equacao", "geometria"])
            if tipo == "equacao":
                ra, rx = random.randint(1, 10), random.randint(1, 10)
                rb = random.randint(1, 20)
                rc = (ra * rx) + rb
                questoes.append(f"{i+1}) Resolva a equacao: {ra}x + {rb} = {rc}")
                gabarito.append(f"{i+1}) x = {rx}")
            else:
                lado = random.randint(2, 20)
                questoes.append(f"{i+1}) Qual o volume de um cubo de lado {lado}?")
                gabarito.append(f"{i+1}) Volume = {lado**3}")
        
        st.session_state.q, st.session_state.g = questoes, gabarito

    if 'q' in st.session_state:
        for ex in st.session_state.q: st.write(ex)
        pdf_bytes = gerar_pdf_atividades(st.session_state.q, st.session_state.g)
        st.download_button("📥 Baixar PDF com Gabarito", pdf_bytes, "atividades.pdf")