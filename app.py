import streamlit as st
import math
import numpy as np
import os
from fpdf import FPDF  # Import necessário para o PDF

# --- 1. SEGURANÇA (Acesso Comum) ---
def validar_acesso(pin_digitado):
    try:
        senha_aluno = str(st.secrets["acesso_aluno"]).strip()
        senha_professor = str(st.secrets["chave_mestra"]).strip()
        if pin_digitado == senha_aluno: return "aluno"
        elif pin_digitado == senha_professor: return "admin"
    except:
        st.error("Erro: Configure 'acesso_aluno' e 'chave_mestra' nos Secrets do Streamlit!")
    return "negado"

st.set_page_config(page_title="Quantum Math Lab", layout="wide")
if 'perfil' not in st.session_state: st.session_state.perfil = None

# --- 2. LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Quantum Math Lab")
    pin = st.text_input("PIN de Acesso:", type="password", key="login_pass")
    if st.button("Entrar"):
        acesso = validar_acesso(pin)
        if acesso != "negado":
            st.session_state.perfil = acesso
            st.rerun()
        else: st.error("Acesso negado.")
    st.stop()

# --- 3. INTERFACE COMPLETA ---
else:
    perfil = st.session_state.perfil
    st.sidebar.title(f"🚀 {'Professor' if perfil == 'admin' else 'Estudante'}")
    
    itens = ["Atividades (Drive)", "Expressões (PEMDAS)", "Equações (1º e 2º Grau)", "Cálculo de Funções", "Logaritmos", "Funções Aritméticas"]
    if perfil == "admin":
        itens += ["Gerador de Atividades", "Sistemas Lineares", "Matrizes", "Financeiro"]
        
    menu = st.sidebar.radio("Navegação:", itens)
    if st.sidebar.button("Sair"):
        st.session_state.perfil = None
        st.rerun()

    # --- GERADOR DE ATIVIDADES (CONSERTADO) ---
    if menu == "Gerador de Atividades":
        st.header("📄 Gerador de Atividades em PDF")
        
        titulo = st.text_input("Título da Lista:", "Atividade de Matemática")
        questoes = st.text_area("Digite as questões (uma por linha):", height=200)
        
        if st.button("Gerar e Baixar PDF"):
            if questoes:
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(200, 10, txt=titulo, ln=True, align='C')
                pdf.ln(10)
                pdf.set_font("Arial", size=12)
                
                for i, linha in enumerate(questoes.split('\n'), 1):
                    pdf.multi_cell(0, 10, txt=f"{i}. {linha}")
                
                # Gera o PDF em memória
                pdf_bytes = pdf.output(dest='S').encode('latin-1')
                
                st.download_button(
                    label="📥 Clique aqui para Baixar o PDF",
                    data=pdf_bytes,
                    file_name="atividade_quantum.pdf",
                    mime="application/pdf"
                )
                st.success("PDF pronto para download!")
            else:
                st.warning("Escreva algumas questões antes de gerar.")

    # --- Mantenha todos os outros elif (Expressões, Equações, etc.) como estão no seu código ---
    elif menu == "Atividades (Drive)":
        st.header("📝 Pasta de Atividades")
        st.link_button("📂 Abrir Google Drive", "https://drive.google.com/drive/folders/1NkFeom_k3LUJYAFVBBDu4GD5aYVeNEZc?usp=drive_link")

    elif menu == "Expressões (PEMDAS)":
        st.header("🧮 Calculadora de Expressões")
        exp = st.text_input("Digite a expressão (ex: (5+3)*2^2):")
        if st.button("Resolver"):
            try:
                res = eval(exp.replace('^', '**'), {"__builtins__": None}, {"math": math, "sqrt": math.sqrt})
                st.success(f"Resultado: {res}")
            except: st.error("Erro na expressão.")

    elif menu == "Equações (1º e 2º Grau)":
        st.header("📐 Resolução de Equações")
        grau = st.selectbox("Escolha o Grau:", ["1º Grau", "2º Grau"])
        if grau == "1º Grau":
            a1 = st.number_input("a:", value=1.0); b1 = st.number_input("b:", value=0.0)
            if st.button("Calcular 1º"):
                if a1 != 0: st.success(f"x = {-b1/a1:.2f}")
        else:
            a2 = st.number_input("a:", value=1.0, key="a2"); b2 = st.number_input("b:", value=-5.0); c2 = st.number_input("c:", value=6.0)
            if st.button("Calcular 2º"):
                delta = b2**2 - 4*a2*c2
                if delta >= 0:
                    x1 = (-b2 + math.sqrt(delta))/(2*a2); x2 = (-b2 - math.sqrt(delta))/(2*a2)
                    st.success(f"x1 = {x1:.2f}, x2 = {x2:.2f}")
                else: st.error("Delta negativo.")
    
    # ... Repita os outros elif para Logaritmos, Funções Aritméticas, Sistemas, Matrizes e Financeiro ...