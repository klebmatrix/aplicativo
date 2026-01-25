import streamlit as st
import os
import numpy as np
import plotly.express as px
from cryptography.fernet import Fernet
from fpdf import FPDF
import random
from datetime import datetime

# 1. GARANTIR A EXISTÊNCIA DA PASTA
PASTA_DESTINO = "atividades"
if not os.path.exists(PASTA_DESTINO):
    os.makedirs(PASTA_DESTINO)

# --- SEGURANÇA ---
PIN_CRIPTOGRAFADO = "gAAAAABpdRRwrtzON4oc6ayd3fx1LjLjX8TjRj7riCkHHuOpi0lcYFAu04KEXEo8d3-GJz9HmpP-AjvbLOLzr6zC6GMUvOCP1A=="

def validar_acesso(pin_digitado):
    senha_aluno_env = os.environ.get('acesso_aluno')
    if senha_aluno_env and pin_digitado == senha_aluno_env:
        return "aluno"
    try:
        chave = os.environ.get('chave_mestra')
        if not chave: return "erro_env"
        chave = chave.strip().replace("'", "").replace('"', "").replace('b', '', 1) if chave.startswith('b') else chave.strip()
        f = Fernet(chave.encode())
        if pin_digitado == f.decrypt(PIN_CRIPTOGRAFADO.strip().encode()).decode():
            return "admin"
    except:
        pass
    return "negado"

st.set_page_config(page_title="Quantum Lab", layout="wide")

# Inicializa a lista de atividades na memória para não sumir da tela
if 'nuvem_pdf' not in st.session_state:
    st.session_state.nuvem_pdf = []
if 'perfil' not in st.session_state:
    st.session_state.perfil = None

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
    pdf.cell(0, 10, "Gabarito Oficial", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    for r in respostas:
        pdf.multi_cell(0, 10, txt=r); pdf.ln(2)
    return pdf.output(dest='S').encode('latin-1')

# --- LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Login")
    pin = st.text_input("PIN:", type="password")
    if st.button("Entrar"):
        acesso = validar_acesso(pin)
        if acesso != "negado":
            st.session_state.perfil = acesso
            st.rerun()
        else: st.error("Acesso Negado")
    st.stop()

# --- TELA ALUNO ---
if st.session_state.perfil == "aluno":
    st.title("🎓 Área do Aluno")
    if st.sidebar.button("Sair"):
        st.session_state.perfil = None
        st.rerun()
    
    if not st.session_state.nuvem_pdf:
        st.info("Nenhuma atividade disponível.")
    else:
        for i, item in enumerate(st.session_state.nuvem_pdf):
            st.write(f"📄 {item['nome']} ({item['tema']})")
            st.download_button("Baixar PDF", item['bin'], file_name=f"{item['nome']}.pdf", key=f"al_{i}")
            st.divider()

# --- TELA ADMIN ---
elif st.session_state.perfil == "admin":
    st.sidebar.title("Painel Professor")
    menu = st.sidebar.radio("Menu", ["Gerador", "Cálculos"])
    if st.sidebar.button("Sair"):
        st.session_state.perfil = None
        st.rerun()

    if menu == "Gerador":
        st.header("📝 Criar Nova Atividade")
        tema = st.selectbox("Tema:", ["Álgebra", "Geometria"])
        nome_doc = st.text_input("Nome do Arquivo:", "Atividade_01")
        
        if st.button("🚀 Gerar e Salvar"):
            qs, gs = [f"Questão 1 de {tema}"], ["Resposta 1"]
            pdf_bin = gerar_material_pdf(tema, qs, gs)
            
            # SALVAMENTO FÍSICO NA PASTA
            caminho_completo = os.path.join(PASTA_DESTINO, f"{nome_doc}.pdf")
            with open(caminho_completo, "wb") as f:
                f.write(pdf_bin)
            
            # ADICIONAR NA NUVEM PARA O ALUNO VER
            st.session_state.nuvem_pdf.append({
                "nome": nome_doc,
                "tema": tema,
                "bin": pdf_bin
            })
            
            st.success(f"✅ Arquivo salvo em: {caminho_completo}")
            st.info("A atividade já está disponível na tela do aluno!")

    elif menu == "Cálculos":
        st.header("🧮 Calculadoras Avançadas")
        st.latex(r"ax^2 + bx + c = 0")
        st.info("Aqui você pode realizar seus cálculos de Álgebra, Geometria e Sistemas.")