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

# --- 2. MOTOR DE PDF ---
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'Quantum Math Lab - Relatorio de Algebra', 0, 1, 'C')
        self.ln(5)

def gerar_pdf_solucao(titulo, linhas):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, titulo.upper(), ln=True)
    pdf.set_font("Arial", size=11)
    for l in linhas:
        pdf.multi_cell(0, 10, txt=l)
    return pdf.output(dest='S').encode('latin-1')

# --- 3. CONFIGURAÇÃO DA INTERFACE ---
st.set_page_config(page_title="Math Precision Lab", layout="wide")
if 'logado' not in st.session_state: st.session_state.logado = False

if not st.session_state.logado:
    st.title("🔐 Acesso ao Laboratorio")
    pin = st.text_input("Senha Alfanumerica:", type="password")
    if st.button("Entrar"):
        res = validar_acesso(pin)
        if res == "ok": st.session_state.logado = True; st.rerun()
        else: st.error(f"Erro: {res}")
    st.stop()

# --- 4. MENU LATERAL ---
st.sidebar.title("⚛️ Categorias")
menu = st.sidebar.radio("Navegação:", ["Álgebra", "Geometria", "Sistemas Lineares", "Matemática Financeira"])
if st.sidebar.button("Logoff"): st.session_state.logado = False; st.rerun()

# --- MÓDULO: ÁLGEBRA (EQUAÇÕES) ---
if menu == "Álgebra":
    st.header("🔍 Álgebra: Equações")
    sub_tipo = st.radio("Escolha o Grau:", ["1º Grau (ax + b = c)", "2º Grau (ax² + bx + c = 0)"])
    
    if sub_tipo == "1º Grau (ax + b = c)":
        c1, c2, c3 = st.columns(3)
        a = c1.number_input("a (≠ 0):", value=2, step=1)
        b = c2.number_input("b:", value=40, step=1)
        c_eq = c3.number_input("Igual a c:", value=50, step=1)
        
        if a == 0:
            st.error("Erro Matemático: 'a' não pode ser zero.")
        elif st.button("Resolver 1º Grau"):
            x = (c_eq - b) / a
            txt_res = f"Equacao: {a}x + {b} = {c_eq}\nPasso: {a}x = {c_eq - b}\nResultado: x = {x}"
            st.success(f"x = {x}")
            st.download_button("Baixar PDF da Solucao", gerar_pdf_solucao("Equacao 1º Grau", [txt_res]), "solucao_1grau.pdf")

    elif sub_tipo == "2º Grau (ax² + bx + c = 0)":
        st.latex(r"ax^2 + bx + c = 0")
        c1, c2, c3 = st.columns(3)
        a2 = c1.number_input("Coeficiente a:", value=1, step=1)
        b2 = c2.number_input("Coeficiente b:", value=-5, step=1)
        c2 = c3.number_input("Coeficiente c:", value=6, step=1)
        
        if a2 == 0:
            st.warning("Com a=0, isto e uma equacao de 1º grau.")
        elif st.button("Calcular Bhaskara"):
            delta = (b2**2) - (4 * a2 * c2)
            st.write(f"**Delta ($\Delta$):** {delta}")
            
            if delta < 0:
                st.error("Delta negativo. As raizes sao complexas.")
                sol_txt = [f"Equacao: {a2}x² + {b2}x + {c2} = 0", f"Delta: {delta}", "Raizes: Complexas"]
            else:
                x1 = (-b2 + np.sqrt(delta)) / (2 * a2)
                x2 = (-b2 - np.sqrt(delta)) / (2 * a2)
                st.success(f"x1 = {x1} | x2 = {x2}")
                sol_txt = [
                    f"Equacao: {a2}x² + {b2}x + {c2} = 0",
                    f"Delta: {delta}",
                    f"x1 = {x1}",
                    f"x2 = {x2}"
                ]
            
            st.download_button("Baixar PDF da Solucao", gerar_pdf_solucao("Equacao 2º Grau (Bhaskara)", sol_txt), "bhaskara.pdf")

# --- MANTEM AS OUTRAS CATEGORIAS ABAIXO (GEOMETRIA, SISTEMAS, ETC.) ---
elif menu == "Geometria":
    st.header("📐 Geometria: Áreas e Volumes")
    # ... (mesmo código de geometria anterior)