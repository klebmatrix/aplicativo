import streamlit as st
import os
import numpy as np
import plotly.express as px
from cryptography.fernet import Fernet
from fpdf import FPDF
import random

# --- 1. SEGURANÇA ---
PIN_CRIPTOGRAFADO = "gAAAAABpdRRwrtzON4oc6ayd3fx1LjLjX8TjRj7riCkHHuOpi0lcYFAu04KEXEo8d3-GJz9HmpP-AjvbLOLzr6zC6GMUvOCP1A=="

def validar_acesso(pin_digitado):
    if pin_digitado == "123456": return "aluno"
    try:
        chave = os.environ.get('chave_mestra')
        if not chave: return "erro_env"
        chave = chave.strip().replace("'", "").replace('"', "").replace('b', '', 1) if chave.startswith('b') else chave.strip()
        f = Fernet(chave.encode())
        if pin_digitado == f.decrypt(PIN_CRIPTOGRAFADO.strip().encode()).decode(): return "admin"
    except: pass
    return "negado"

# --- CONFIGURAÇÃO E BANCO TEMPORÁRIO ---
st.set_page_config(page_title="Quantum Lab", layout="wide")

if 'perfil' not in st.session_state: st.session_state.perfil = None
if 'nuvem_pdf' not in st.session_state: st.session_state.nuvem_pdf = []

# --- MOTOR DE PDF ---
def gerar_material_pdf(titulo, questoes, respostas):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"Atividade: {titulo}", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    for q in questoes:
        pdf.multi_cell(0, 10, txt=q); pdf.ln(5)
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Gabarito", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    for r in respostas:
        pdf.multi_cell(0, 10, txt=r); pdf.ln(2)
    return pdf.output(dest='S').encode('latin-1')

# --- TELA DE LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Quantum Math Lab")
    pin = st.text_input("Digite o PIN (Admin ou Aluno):", type="password")
    if st.button("Entrar"):
        acesso = validar_acesso(pin)
        if acesso != "negado":
            st.session_state.perfil = acesso
            st.rerun()
        else: st.error("PIN incorreto.")
    st.stop()

# --- ÁREA DO ALUNO ---
if st.session_state.perfil == "aluno":
    st.title("🎓 Área do Aluno - Materiais Disponíveis")
    if st.sidebar.button("Sair"):
        st.session_state.perfil = None
        st.rerun()

    if not st.session_state.nuvem_pdf:
        st.info("Nenhuma atividade publicada pelo professor ainda.")
    else:
        for item in st.session_state.nuvem_pdf:
            col1, col2 = st.columns([3, 1])
            col1.write(f"📄 **{item['nome']}** (Gerada em: {item['data']})")
            col2.download_button("Baixar PDF", item['bin'], file_name=f"{item['nome']}.pdf", key=item['nome'])

# --- ÁREA DO PROFESSOR (ADMIN) ---
elif st.session_state.perfil == "admin":
    st.sidebar.title("🛠 Painel Admin")
    menu = st.sidebar.radio("Navegação", ["Gerador de PDF", "Sistemas Lineares", "Álgebra"])
    
    if st.sidebar.button("Sair"):
        st.session_state.perfil = None
        st.rerun()

    if menu == "Gerador de PDF":
        st.header("📝 Criar e Publicar Atividades")
        tema = st.selectbox("Tema da Atividade", ["Equações 1º Grau", "Equações 2º Grau"])
        nome_arquivo = st.text_input("Nome da Lista (ex: Atividade_Extra_01):", "Atividade_Quantum")
        
        if st.button("Gerar e Enviar para Alunos"):
            qs, gs = [], []
            for i in range(1, 11):
                a, x = random.randint(2, 5), random.randint(1, 10)
                qs.append(f"{i}) Resolva: {a}x + {random.randint(1,10)} = ...")
                gs.append(f"{i}) x = {x}")
            
            pdf_bin = gerar_material_pdf(tema, qs, gs)
            
            # Salva na "Nuvem" da sessão
            st.session_state.nuvem_pdf.append({
                "nome": nome_arquivo,
                "bin": pdf_bin,
                "data": "25/01/2026"
            })
            st.success("✅ Atividade publicada na tela do aluno!")

    elif menu == "Sistemas":
        st.header("📏 Sistema Ax = B")
        # Coloque aqui o código de matrizes que fizemos antes...

    elif menu == "Álgebra":
        st.header("🔍 Calculadora 1º e 2º Grau")
        # Coloque aqui o código de Álgebra...