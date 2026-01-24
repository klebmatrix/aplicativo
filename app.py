import streamlit as st
import os
import numpy as np
from cryptography.fernet import Fernet
from fpdf import FPDF
import random

# --- 1. SEGURANÇA (TOKEN ALFANUMÉRICO) ---
# Usando o token que você forneceu
PIN_CRIPTOGRAFADO = "gAAAAABpdRRwrtzON4oc6ayd3fx1LjLjX8TjRj7riCkHHuOpi0lcYFAu04KEXEo8d3-GJz9HmpP-AjvbLOLzr6zC6GMUvOCP1A=="

def validar_acesso(pin_digitado):
    try:
        if pin_digitado == "admin": return "ok" # Fallback para testes
        
        chave = os.environ.get('chave_mestra')
        if not chave: return "erro_env"
        
        # Limpeza da chave para evitar erros de b'prefix'
        chave = chave.strip().replace("'", "").replace('"', "").replace('b', '', 1) if chave.startswith('b') else chave.strip()
        f = Fernet(chave.encode())
        
        # Comparação com o PIN de 6 dígitos descriptografado
        if pin_digitado == f.decrypt(PIN_CRIPTOGRAFADO.strip().encode()).decode():
            return "ok"
        return "erro_senha"
    except Exception:
        return "erro_token"

# --- 2. MOTOR DE PDF ---
class PDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 14)
        self.cell(0, 10, 'Quantum Math Lab - Relatorio Oficial', 0, 1, 'C')
        self.ln(5)

def gerar_pdf_atividades(titulo, questoes, respostas):
    pdf = PDF()
    # Página 1: Questões
    pdf.add_page()
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(0, 10, f"ATIVIDADES: {titulo.upper()}", ln=True)
    pdf.set_font("helvetica", size=11)
    for q in questoes:
        pdf.multi_cell(0, 10, txt=q)
        pdf.ln(2)
    # Página 2: Gabarito
    pdf.add_page()
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(0, 10, f"GABARITO: {titulo.upper()}", ln=True)
    pdf.set_font("helvetica", size=11)
    for r in respostas:
        pdf.multi_cell(0, 10, txt=r)
    return pdf.output() # Retorna bytes no fpdf2

# --- 3. CONFIGURAÇÃO STREAMLIT ---
st.set_page_config(page_title="Math Precision Lab", layout="wide")

if 'logado' not in st.session_state: st.session_state.logado = False

if not st.session_state.logado:
    st.title("🔐 Login de Segurança")
    pin = st.text_input("Senha Alfanumerica:", type="password")
    if st.button("Acessar"):
        res = validar_acesso(pin)
        if res == "ok":
            st.session_state.logado = True
            st.rerun()
        else:
            st.error(f"Erro: {res}")
    st.stop()

# --- 4. MENU LATERAL ---
st.sidebar.title("⚛️ Categorias")
menu = st.sidebar.radio("Navegação:", ["Álgebra", "Geometria", "Sistemas Lineares", "Matemática Financeira"])
if st.sidebar.button("Sair"):
    st.session_state.logado = False
    st.rerun()

# --- 5. CONTEÚDO ---
with st.container(key=f"sec_{menu.lower().replace(' ', '_')}"):
    
    if menu == "Álgebra":
        st.header("🔍 Álgebra e Equações")
        sub = st.selectbox("Tipo:", ["1º Grau", "2º Grau (Bhaskara)"])
        
        if sub == "1º Grau":
            c1, c2, c3 = st.columns(3)
            a = c1.number_input("a (≠ 0):", value=2, step=1, key="alg_a")
            b = c2.number_input("b:", value=40, step=1, key="alg_b")
            c_eq = c3.number_input("Igual a c:", value=50, step=1, key="alg_c")
            if a != 0 and st.button("Calcular"):
                st.success(f"x = {(c_eq - b) / a}")

        elif sub == "2º Grau (Bhaskara)":
            c1, c2, c3 = st.columns(3)
            a2, b2, c2v = c1.number_input("a:", 1.0), c2.number_input("b:", -5.0), c3.number_input("c:", 6.0)
            if st.button("Calcular Delta"):
                d = (b2**2) - (4 * a2 * c2v)
                st.write(f"Delta (Δ) = {d}")
                if d >= 0:
                    st.success(f"x1 = {(-b2 + np.sqrt(d))/(2*a2)} | x2 = {(-b2 - np.sqrt(d))/(2*a2)}")
                else: st.error("Raízes Complexas.")

        st.divider()
        qtd = st.slider("Exercícios:", 1, 10, 5, key="slider_alg")
        if st.button("Gerar PDF"):
            q, g = [], []
            for i in range(qtd):
                ra, rx = random.randint(1,10), random.randint(1,10)
                rb = random.randint(1,20); rc = (ra * rx) + rb
                q.append(f"{i+1}) Resolva: {ra}x + {rb} = {rc}")
                g.append(f"{i+1}) x = {rx}")
            pdf_bytes = gerar_pdf_atividades("Algebra", q, g)
            st.download_button("Baixar PDF", pdf_bytes, "algebra.pdf", "application/pdf")

    elif menu == "Geometria":
        st.header("📐 Geometria: Áreas e Volumes")
        fig = st.selectbox("Sólido:", ["Esfera", "Cilindro", "Cubo"])
        med = st.number_input("Medida Principal:", 10.0, key="geo_med")
        
        if fig == "Esfera":
            v = (4/3) * np.pi * (med**3)
            st.metric("Volume", f"{v:.4f}")
            st.latex(r"V = \frac{4}{3} \pi r^3")
            

[Image of sphere volume formula]

        elif fig == "Cilindro":
            h = st.number_input("Altura:", 10.0, key="geo_h")
            v = np.pi * (med**2) * h
            st.metric("Volume", f"{v:.4f}")
            st.latex(r"V = \pi r^2 h")
            

[Image of cylinder volume formula]

        elif fig == "Cubo":
            st.metric("Volume", f"{med**3}")
            st.latex(r"V = L^3")
            

[Image of cube volume formula]


    elif menu == "Sistemas Lineares":
        st.header("📏 Sistemas $Ax=B$")
        n = st.slider("Incógnitas:", 2, 5, 2)
        # Interface simplificada de matriz...
        st.info("Preencha os campos para resolver.")

    elif menu == "Matemática Financeira":
        st.header("💰 Finanças")
        c = st.number_input("Capital:", 1000.0)
        i = st.number_input("Taxa (%):", 1.0) / 100
        t = st.number_input("Tempo (meses):", 12)
        st.metric("Montante", f"R$ {c * (1 + i)**t:.2f}")
        st.latex(r"M = C(1 + i)^t")