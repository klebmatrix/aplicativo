import streamlit as st
import math
import numpy as np
from fpdf import FPDF

# --- 1. SEGURANÇA ---
def validar_acesso(pin_digitado):
    try:
        senha_aluno = str(st.secrets["acesso_aluno"]).strip()
        senha_professor = str(st.secrets["chave_mestra"]).strip()
        if pin_digitado == senha_aluno: return "aluno"
        elif pin_digitado == senha_professor: return "admin"
    except: return "negado"
    return "negado"

st.set_page_config(page_title="Quantum Math Lab", layout="wide")
if 'perfil' not in st.session_state: st.session_state.perfil = None

if st.session_state.perfil is None:
    st.title("🔐 Login")
    pin = st.text_input("Senha:", type="password")
    if st.button("Entrar"):
        acesso = validar_acesso(pin)
        if acesso != "negado":
            st.session_state.perfil = acesso
            st.rerun()
        else: st.error("Acesso negado")
    st.stop()

# --- 2. INTERFACE ---
perfil = st.session_state.perfil
itens = ["Atividades (Drive)", "Expressões (PEMDAS)", "Equações (1º e 2º Grau)", "Cálculo de Funções", "Logaritmos", "Funções Aritméticas"]
if perfil == "admin":
    itens += ["Gerador de Atividades", "Sistemas Lineares", "Matrizes", "Financeiro"]

menu = st.sidebar.radio("Navegação:", itens)
if st.sidebar.button("Sair"):
    st.session_state.perfil = None
    st.rerun()

# --- 3. GERADOR DE ATIVIDADES (CONSERTADO) ---
if menu == "Gerador de Atividades":
    st.header("📄 Gerador de Atividades em PDF")
    
    with st.form("form_pdf"):
        titulo = st.text_input("Título da Atividade:", "Lista de Exercícios")
        disciplina = st.text_input("Disciplina:", "Matemática")
        conteudo = st.text_area("Questões (uma por linha):", "1. Calcule x: 2x + 4 = 10\n2. Resolva log de 100 na base 10.")
        submit = st.form_submit_button("Gerar PDF")

    if submit:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, txt=titulo, ln=True, align='C')
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Disciplina: {disciplina}", ln=True, align='L')
        pdf.ln(10)
        
        for linha in conteudo.split('\n'):
            pdf.multi_cell(0, 10, txt=linha)
        
        pdf_output = pdf.output(dest='S').encode('latin-1')
        st.download_button(label="📥 Baixar Atividade em PDF", data=pdf_output, file_name="atividade.pdf", mime="application/pdf")
        st.success("PDF gerado com sucesso!")

# --- 4. EXPRESSÕES (PEMDAS) ---
elif menu == "Expressões (PEMDAS)":
    st.header("🧮 Calculadora de Expressões")
    exp = st.text_input("Expressão:")
    if st.button("Resolver"):
        try:
            res = eval(exp.replace('^', '**'), {"__builtins__": None}, {"math": math, "sqrt": math.sqrt})
            st.success(f"Resultado: {res}")
        except: st.error("Erro na expressão.")

# --- 5. FINANCEIRO ---
elif menu == "Financeiro":
    st.header("💰 Juros Compostos")
    c = st.number_input("Capital:", value=1000.0)
    i = st.number_input("Taxa (%):", value=5.0) / 100
    t = st.number_input("Tempo:", value=12.0)
    if st.button("Calcular"):
        m = c * (1 + i)**t
        st.metric("Montante", f"R$ {m:.2f}")

# --- 6. LOGARITMOS ---
elif menu == "Logaritmos":
    st.header("🔢 Logaritmo")
    n = st.number_input("Número:", value=100.0)
    b = st.number_input("Base:", value=10.0)
    if st.button("Calcular"):
        st.success(f"Resultado: {math.log(n, b):.4f}")

# (Mantenha os outros elif para Equações, Matrizes, etc. conforme os códigos anteriores)