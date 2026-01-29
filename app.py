import streamlit as st
import math
import numpy as np
import os
import random
import re
from fpdf import FPDF

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide", page_icon="🚀")

if 'perfil' not in st.session_state: st.session_state.perfil = None
if 'sub_menu' not in st.session_state: st.session_state.sub_menu = None
if 'preview_questoes' not in st.session_state: st.session_state.preview_questoes = []

def clean_txt(text):
    if not text: return ""
    text = str(text).replace("√", "V").replace("²", "^2").replace("³", "^3")
    return text.encode('latin-1', 'replace').decode('latin-1')

def tratar_math(texto):
    t = texto.strip()
    t = t.replace("²", "^{2}").replace("³", "^{3}")
    return t

def validar_acesso(pin_digitado):
    try:
        senha_aluno = str(st.secrets.get("acesso_aluno", "123456")).strip()
        senha_prof = str(st.secrets.get("chave_mestra", "chave_mestra")).strip().lower()
    except:
        senha_aluno, senha_prof = "123456", "chave_mestra"
    if pin_digitado == senha_aluno: return "aluno"
    elif pin_digitado == senha_prof: return "admin"
    return "negado"

# --- LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Login")
    pin = st.text_input("PIN:", type="password")
    if st.button("Entrar"):
        acesso = validar_acesso(pin)
        if acesso != "negado":
            st.session_state.perfil = acesso
            st.rerun()
        else: st.error("PIN incorreto.")
    st.stop()

# --- MENU LATERAL ---
perfil = st.session_state.perfil
st.sidebar.title(f"🚀 {'Professor' if perfil == 'admin' else 'Estudante'}")
if st.sidebar.button("Sair/Logout"):
    for key in list(st.session_state.keys()): del st.session_state[key]
    st.rerun()

# --- PAINEL ADMIN ---
if perfil == "admin":
    st.title("🛠️ Painel de Controle")
    
    st.subheader("📝 Geradores de Atividades (PDF)")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: 
        if st.button("🔢 Operações", use_container_width=True): 
            st.session_state.sub_menu = "op"; st.session_state.preview_questoes = []
    with c2: 
        if st.button("📐 Equações", use_container_width=True): 
            st.session_state.sub_menu = "eq"; st.session_state.preview_questoes = []
    with c3: 
        if st.button("📚 Colegial", use_container_width=True): 
            st.session_state.sub_menu = "col"; st.session_state.preview_questoes = []
    with c4: 
        if st.button("⚖️ Álgebra", use_container_width=True): 
            st.session_state.sub_menu = "alg"; st.session_state.preview_questoes = []
    with c5: 
        if st.button("📄 Manual", use_container_width=True): 
            st.session_state.sub_menu = "man"; st.session_state.preview_questoes = []

    st.markdown("---")
    st.subheader("🧮 Ferramentas de Cálculo Online")
    d1, d2, d3 = st.columns(3)
    with d1: 
        if st.button("𝑓(x) Funções", use_container_width=True): st.session_state.sub_menu = "calc_f"
    with d2: 
        if st.button("📊 PEMDAS", use_container_width=True): st.session_state.sub_menu = "pemdas"
    with d3: 
        if st.button("💰 Financeira", use_container_width=True): st.session_state.sub_menu = "fin"

    op_atual = st.session_state.sub_menu
    st.divider()

        
        return pdf.output(dest='S').encode('latin-1')

    # Interface de Download
    c1, c2 = st.columns(2)
    with c1:
        st.download_button("📄 PDF COM Cabeçalho", gerar_pdf_final(True), "atividade_completa.pdf")
    with c2:
        st.download_button("📄 PDF SEM Cabeçalho", gerar_pdf_final(False), "atividade_simples.pdf")
# --- 5. LÓGICA DE PROCESSAMENTO ---
if st.session_state.sub_menu == "📝 Modo Manual":
    st.header("Entrada de Dados")
    txt_input = st.text_area(
        "Digite sua prova (t. Título, -M Módulo, 1. Questão):",
        height=250,
        placeholder="t. AVALIAÇÃO\n-M1. SOMA\n1. Calcule:\n10+5\n20+2"
    )
    
    if st.button("🔄 PROCESSAR DADOS"):
        if txt_input:
            st.session_state.preview_questoes = txt_input.split('\n')
            st.toast("Atividade Processada!")

# --- 6. VISUALIZAÇÃO NA TELA ---
questoes = st.session_state.get('preview_questoes', [])

if questoes:
    st.divider()
    if os.path.exists("cabecalho.png"):
        st.image("cabecalho.png", use_container_width=True)
    
    letras = "abcdefghijklmnopqrstuvwxyz"
    l_idx = 0
    
    for linha in questoes:
        l = linha.strip()
        if not l: continue
        
        if l.lower().startswith("t."):
            st.markdown(f"<h1 style='text-align:center;'>{l[2:]}</h1>", unsafe_allow_html=True)
            l_idx = 0
        elif l.startswith("-M"):
            st.markdown(f"<div style='border-bottom:3px solid #333;'><h3>{l[1:]}</h3></div>", unsafe_allow_html=True)
            l_idx = 0
        elif re.match(r'^\d+', l):
            st.markdown(f"#### {l}")
            l_idx = 0
        else:
            cols = st.columns(2)
            alvo = cols[0] if l_idx % 2 == 0 else cols[1]
            with alvo:
                st.markdown(f"**{letras[l_idx%26]})** {l}")
            l_idx += 1

# --- 7. MOTOR GERADOR DE PDF ---
    st.divider()
    
    def criar_pdf(com_header):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        y_atual = 20
        if com_header and os.path.exists("cabecalho.png"):
            pdf.image("cabecalho.png", x=10, y=10, w=190)
            y_atual = 55
        
        pdf.set_y(y_atual)
        l_pdf_idx = 0
        y_max_linha = y_atual
        y_col_esquerda = y_atual

        for linha in questoes:
            l = linha.strip()
            if not l: continue

            if l.lower().startswith("t.") or l.startswith("-M") or re.match(r'^\d+', l):
                if l_pdf_idx > 0:
                    pdf.set_y(y_max_linha + 5)
                l_pdf_idx = 0

            if l.lower().startswith("t."):
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(0, 10, clean_txt(l[2:]), ln=True, align='C')
                y_max_linha = pdf.get_y()
            elif l.startswith("-M"):
                pdf.ln(5)
                pdf.set_font("Arial", 'B', 14)
                pdf.cell(0, 10, clean_txt(l[1:]), ln=True, align='L')
                pdf.line(10, pdf.get_y(), 200, pdf.get_y())
                y_max_linha = pdf.get_y()
            elif re.match(r'^\d+', l):
                pdf.ln(2)
                pdf.set_font("Arial", '', 12)
                pdf.multi_cell(0, 8, clean_txt(l))
                y_max_linha = pdf.get_y()
            else:
                pdf.set_font("Arial", '', 11)
                item_txt = f"{letras[l_pdf_idx%26]}) {clean_txt(l)}"
                y_antes = pdf.get_y()
                
                if l_pdf_idx % 2 == 0:
                    pdf.set_xy(10, y_antes)
                    pdf.multi_cell(90, 7, item_txt)
                    y_col_esquerda = pdf.get_y()
                    pdf.set_y(y_antes)
                    y_max_linha = y_col_esquerda
                else:
                    pdf.set_xy(105, y_antes)
                    pdf.multi_cell(90, 7, item_txt)
                    y_max_linha = max(y_col_esquerda, pdf.get_y())
                    pdf.set_y(y_max_linha)
                l_pdf_idx += 1
                
        return pdf.output(dest='S').encode('latin-1')

    # BOTÕES DE DOWNLOAD
    st.subheader("📥 Baixar Atividade")
    c1, c2 = st.columns(2)
    with c1:
        # Aqui chamamos a função dentro do botão
        pdf_com = criar_pdf(True)
        st.download_button("📄 Com Cabeçalho", pdf_com, "prova_completa.pdf", "application/pdf")
    with c2:
        pdf_sem = criar_pdf(False)
        st.download_button("📄 Sem Cabeçalho", pdf_sem, "prova_simples.pdf", "application/pdf")