import streamlit as st
import math
import numpy as np
import os
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

# --- 3. INTERFACE ---
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

    # --- BLOCOS DE CONTEÚDO ---
    if menu == "Atividades (Drive)":
        st.header("📝 Pasta de Atividades")
        st.link_button("📂 Abrir Google Drive", "https://drive.google.com/drive/folders/1NkFeom_k3LUJYAFVBBDu4GD5aYVeNEZc?usp=drive_link")

    elif menu == "Expressões (PEMDAS)":
        st.header("🧮 Calculadora de Expressões")
        exp = st.text_input("Digite a expressão:")
        if st.button("Resolver"):
            try:
                res = eval(exp.replace('^', '**'), {"__builtins__": None}, {"math": math, "sqrt": math.sqrt})
                st.success(f"Resultado: {res}")
            except: st.error("Erro na expressão.")

    elif menu == "Gerador de Atividades":
        st.header("📄 Gerador de Atividades")
        titulo_pdf = st.text_input("Título:", "Atividade de Matemática")
        conteudo = st.text_area("Itens da atividade (cada linha vira uma letra a, b, c...):")
        
        if st.button("Gerar PDF"):
            if conteudo:
                pdf = FPDF()
                pdf.add_page()
                
                # Header com Imagem (Deve estar no seu GitHub como 'header.png')
                if os.path.exists("header.png"):
                    pdf.image("header.png", x=10, y=8, w=190)
                    pdf.ln(35)
                
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(200, 10, txt=titulo_pdf, ln=True, align='C')
                pdf.ln(10)
                
                pdf.set_font("Arial", size=12)
                letras = "abcdefghijklmnopqrstuvwxyz"
                for i, linha in enumerate(conteudo.split('\n')):
                    if linha.strip():
                        # Letramento a); b); c); conforme solicitado
                        pdf.multi_cell(0, 10, txt=f"{letras[i%26]}) {linha.strip()}")
                
                pdf_bytes = pdf.output(dest='S').encode('latin-1', 'replace')
                st.download_button("📥 Baixar PDF", data=pdf_bytes, file_name="atividade.pdf")
            else: st.warning("Escreva o conteúdo.")

    elif menu == "Financeiro":
        st.header("💰 Financeiro")
        c = st.number_input("Capital:", value=1000.0)
        i = st.number_input("Taxa (%):", value=5.0) / 100
        t = st.number_input("Tempo:", value=12.0)
        if st.button("Calcular"):
            st.success(f"Montante: R$ {c * (1 + i)**t:.2f}")

    # (Mantenha os outros menus como Logaritmos e Equações seguindo o mesmo alinhamento do elif)