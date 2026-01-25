import streamlit as st
import os
import numpy as np
import plotly.express as px
from cryptography.fernet import Fernet
from fpdf import FPDF
import random
from datetime import datetime

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
    pdf.cell(0, 10, "Gabarito Oficial", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    for r in respostas:
        pdf.multi_cell(0, 10, txt=r); pdf.ln(2)
    return pdf.output(dest='S').encode('latin-1')

# --- TELA DE LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Quantum Math Lab")
    pin = st.text_input("Digite o PIN:", type="password")
    if st.button("Entrar"):
        acesso = validar_acesso(pin)
        if acesso != "negado":
            st.session_state.perfil = acesso
            st.rerun()
        else: st.error("PIN incorreto.")
    st.stop()

# --- ÁREA DO ALUNO ---
if st.session_state.perfil == "aluno":
    st.title("🎓 Portal do Aluno")
    if st.sidebar.button("Sair"):
        st.session_state.perfil = None
        st.rerun()

    if not st.session_state.nuvem_pdf:
        st.info("Nenhuma atividade disponível no momento.")
    else:
        for i, item in enumerate(st.session_state.nuvem_pdf):
            c1, c2 = st.columns([4, 1])
            c1.write(f"📌 **{item['nome']}** | {item['tema']}")
            c2.download_button("Download", item['bin'], file_name=f"{item['nome']}.pdf", key=f"aluno_{i}")
            st.divider()

# --- ÁREA DO PROFESSOR ---
elif st.session_state.perfil == "admin":
    st.sidebar.title("🛠 Painel Admin")
    menu = st.sidebar.radio("Navegação", ["Gerador e Nuvem", "Cálculos Avançados"])
    if st.sidebar.button("Sair"):
        st.session_state.perfil = None
        st.rerun()

    if menu == "Gerador e Nuvem":
        st.header("📝 Gerar e Publicar Atividades")
        tema = st.selectbox("Escolha o Tema:", ["Álgebra", "Geometria"])
        nome_doc = st.text_input("Nome da Lista:", "Atividade_01")
        
        if st.button("Publicar para Alunos"):
            qs, gs = ["Questao exemplo 1?"], ["Resposta 1"]
            pdf_bin = gerar_material_pdf(tema, qs, gs)
            st.session_state.nuvem_pdf.append({
                "nome": nome_doc, "tema": tema, "bin": pdf_bin, "data": datetime.now().strftime("%H:%M")
            })
            st.success("Publicado!")

        st.divider()
        st.subheader("🗑️ Gerenciar Nuvem (Excluir)")
        for idx, doc in enumerate(st.session_state.nuvem_pdf):
            col_n, col_b = st.columns([4, 1])
            col_n.write(f"📄 {doc['nome']}")
            if col_b.button("Excluir", key=f"del_{idx}"):
                st.session_state.nuvem_pdf.pop(idx)
                st.rerun()

    elif menu == "Cálculos Avançados":
        t1, t2 = st.tabs(["Sistemas Ax=B", "Geometria/Financeiro"])
        with t1:
            st.latex(r"Ax = B")
            # Código de Matrizes aqui (remova qualquer etiqueta de imagem)
            st.info("Insira os dados da matriz para resolver.")
        with t2:
            st.latex(r"a^2 + b^2 = c^2")
            st.latex(r"M = C(1+i)^t")