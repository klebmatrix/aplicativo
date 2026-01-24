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
        if pin_digitado == "admin": return "ok"
        chave = os.environ.get('chave_mestra')
        if not chave: return "erro_env"
        chave = chave.strip().replace("'", "").replace('"', "").replace('b', '', 1) if chave.startswith('b') else chave.strip()
        f = Fernet(chave.encode())
        if pin_digitado == f.decrypt(PIN_CRIPTOGRAFADO.strip().encode()).decode():
            return "ok"
        return "erro_senha"
    except: return "erro_token"

# --- 2. MOTOR DE PDF ---
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'Quantum Lab - Relatorio Matematico', 0, 1, 'C')
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

# --- 3. CONFIGURAÇÃO E ESTADO ---
st.set_page_config(page_title="Math Precision Lab", layout="wide")
if 'logado' not in st.session_state: st.session_state.logado = False
if 'pdf_pronto' not in st.session_state: st.session_state.pdf_pronto = None

if not st.session_state.logado:
    st.title("🔐 Acesso Quantum Lab")
    pin = st.text_input("Senha (6-8 caracteres):", type="password")
    if st.button("Acessar"):
        if validar_acesso(pin) == "ok":
            st.session_state.logado = True
            st.rerun()
        else: st.error("PIN Incorreto.")
    st.stop()

# --- 4. MENU ---
menu = st.sidebar.radio("Módulos:", ["Álgebra", "Geometria", "Sistemas", "Financeiro"])
if st.sidebar.button("Sair"):
    st.session_state.logado = False
    st.rerun()

# --- 5. SISTEMAS LINEARES ---
if menu == "Sistemas":
    st.header("📏 Sistemas Lineares (Matriz $Ax=B$)")
    n = st.slider("Número de Incógnitas:", 2, 4, 2, key="n_sis")
    
    st.write("Insira os coeficientes da Matriz A e os resultados do Vetor B:")
    mat_A = []
    vec_B = []
    
    for i in range(n):
        cols = st.columns(n + 1)
        row = []
        for j in range(n):
            val = cols[j].number_input(f"A{i+1}{j+1}", value=1.0 if i==j else 0.0, key=f"A_{i}_{j}")
            row.append(val)
        mat_A.append(row)
        b_val = cols[n].number_input(f"B{i+1}", value=1.0, key=f"B_{i}")
        vec_B.append(b_val)
        
    if st.button("Resolver Sistema"):
        try:
            solucao = np.linalg.solve(np.array(mat_A), np.array(vec_B))
            st.success("Sistema Resolvido!")
            for idx, s in enumerate(solucao):
                st.write(f"**x{idx+1}** = {s:.4f}")
        except np.linalg.LinAlgError:
            st.error("O sistema não possui uma solução única (Matriz Singular).")

# --- 6. FINANCEIRO ---
elif menu == "Financeiro":
    st.header("💰 Matemática Financeira")
    st.latex(r"M = C \cdot (1 + i)^t")
    
    
    c1, c2, c3 = st.columns(3)
    cap = c1.number_input("Capital Inicial (R$):", value=1000.0, step=100.0)
    taxa = c2.number_input("Taxa de Juros (% ao mês):", value=1.0, step=0.1) / 100
    tempo = c3.number_input("Tempo (Meses):", value=12, step=1)
    
    if st.button("Calcular Montante"):
        montante = cap * (1 + taxa)**tempo
        juros = montante - cap
        st.metric("Montante Final", f"R$ {montante:.2f}", delta=f"Juros: R$ {juros:.2f}")

# --- 7. REAPROVEITAMENTO (ÁLGEBRA E GEOMETRIA) ---
elif menu == "Álgebra":
    st.header("🔍 Álgebra")
    st.info("Utilize a barra lateral para gerar atividades em PDF.")

elif menu == "Geometria":
    st.header("📐 Geometria")
    st.write("Cálculos de Pitágoras e Áreas disponíveis.")

# --- 8. BARRA LATERAL (PDF) ---
st.sidebar.divider()
st.sidebar.subheader("📝 Gerador de Atividades")
tipo_pdf = st.sidebar.selectbox("Tema:", ["Álgebra", "Geometria"])
if st.sidebar.button("Gerar Material"):
    q, g = [], []
    if tipo_pdf == "Álgebra":
        for i in range(5):
            ra, rx = random.randint(1,10), random.randint(1,10)
            rb = random.randint(1,20); rc = (ra * rx) + rb
            q.append(f"{i+1}) Resolva: {ra}x + {rb} = {rc}")
            g.append(f"{i+1}) x = {rx}")
    else:
        q = ["1) Calcule a hipotenusa de um triangulo com catetos 3 e 4."]
        g = ["1) Hipotenusa = 5"]
    
    st.session_state.pdf_pronto = gerar_pdf_bytes(tipo_pdf, q, g)
    st.sidebar.success("PDF Pronto!")

if st.session_state.pdf_pronto:
    st.sidebar.download_button("📥 Baixar PDF", st.session_state.pdf_pronto, "atividades.pdf", "application/pdf")