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

if st.sidebar.button("🧹 Limpar Tudo"):
    st.session_state.preview_questoes = []
    st.session_state.sub_menu = None
    st.rerun()

# --- PAINEL ADMIN ---
if perfil == "admin":
    st.title("🛠️ Painel de Controle")
    
    st.subheader("📝 Geradores de Atividades")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: 
        if st.button("🔢 Operações", use_container_width=True): st.session_state.sub_menu = "op"
    with c2: 
        if st.button("📐 Equações", use_container_width=True): st.session_state.sub_menu = "eq"
    with c3: 
        if st.button("📚 Colegial", use_container_width=True): st.session_state.sub_menu = "col"
    with c4: 
        if st.button("⚖️ Álgebra", use_container_width=True): st.session_state.sub_menu = "alg"
    with c5: 
        if st.button("📄 Manual", use_container_width=True): st.session_state.sub_menu = "man"

    op_atual = st.session_state.sub_menu
    st.divider()

    # --- LÓGICA DE GERAÇÃO ---
    if op_atual == "col":
        st.header("📚 Colegial")
        tema = st.radio("Tema:", ["Frações", "Potenciação", "Radiciação", "Porcentagem"], horizontal=True)
        if st.button("Gerar Preview"):
            if tema == "Frações": qs = [f"{random.randint(1,9)}/{random.randint(2,5)} + {random.randint(1,9)}/{random.randint(2,5)} =" for _ in range(8)]
            elif tema == "Potenciação": qs = [f"{random.randint(2,12)}^{random.randint(2,3)} =" for _ in range(8)]
            elif tema == "Radiciação": qs = [f"√{n**2} =" for n in random.sample(range(2, 15), 8)]
            else: qs = [f"{random.choice([10,25,50])}% de {random.randint(100, 1000)} =" for _ in range(8)]
            st.session_state.preview_questoes = [f"t. Atividade de {tema}"] + qs

    elif op_atual == "alg":
        st.header("⚖️ Álgebra")
        tipo = st.radio("Sistemas:", ["1º Grau (x, y)", "2º Grau"], horizontal=True)
        if st.button("Gerar Preview"):
            if "1º" in tipo: qs = [f"{random.randint(1,5)}x + {random.randint(1,5)}y = {random.randint(10,30)}\n{random.randint(1,5)}x - {random.randint(1,5)}y = {random.randint(1,10)}" for _ in range(4)]
            else: qs = [f"x + y = {random.randint(5,12)}\nx^2 + y^2 = {random.randint(40,150)}" for _ in range(3)]
            st.session_state.preview_questoes = [f"t. Sistemas de {tipo}"] + qs

    elif op_atual == "man":
        st.header("📄 Modo Manual")
        txt_m = st.text_area("Digite as questões (t. para Título):", height=200)
        if st.button("Processar"): st.session_state.preview_questoes = txt_m.split('\n')

# --- FUNÇÃO GERADORA DE PDF ---
def gerar_pdf(questoes, com_cabecalho=True):
    pdf = FPDF()
    pdf.add_page()
    y_at = 15
    if com_cabecalho and os.path.exists("cabecalho.png"):
        pdf.image("cabecalho.png", x=10, y=10, w=190)
        y_at = 55
    
    letras = "abcdefghijklmnopqrstuvwxyz"
    l_idx = 0
    y_base = y_at
    
    for q in questoes:
        line = q.strip()
        if not line: continue
        
        if line.lower().startswith("t."):
            pdf.set_font("Arial", 'B', 16); pdf.set_y(y_at)
            pdf.cell(0, 10, clean_txt(line[2:]), ln=True, align='C')
            y_at = pdf.get_y() + 5; l_idx = 0
        elif re.match(r'^\d+', line):
            pdf.set_font("Arial", 'B', 12); pdf.set_y(y_at + 2)
            pdf.multi_cell(0, 8, clean_txt(line))
            y_at, l_idx = pdf.get_y(), 0
        else:
            pdf.set_font("Arial", size=11)
            txt = f"{letras[l_idx%26]}) {line}"
            if l_idx % 2 == 0:
                y_base = y_at; pdf.set_xy(15, y_base); pdf.multi_cell(90, 8, clean_txt(txt))
                y_prox = pdf.get_y()
            else:
                pdf.set_xy(110, y_base); pdf.multi_cell(85, 8, clean_txt(txt))
                y_at = max(y_prox, pdf.get_y())
            l_idx += 1
    return pdf.output(dest='S').encode('latin-1')

# --- VISUALIZAÇÃO E BOTÕES DE DOWNLOAD ---
if st.session_state.preview_questoes:
    st.divider()
    
    # Preview na tela (Sempre com imagem se existir, para conferência)
    if os.path.exists("cabecalho.png"): st.image("cabecalho.png", use_container_width=True)
    
    letras = "abcdefghijklmnopqrstuvwxyz"
    l_idx = 0
    for q in st.session_state.preview_questoes:
        line = q.strip()
        if not line: continue
        if line.lower().startswith("t."):
            st.markdown(f"<h1 style='text-align: center; color: #007bff;'>{line[2:].strip()}</h1>", unsafe_allow_html=True)
            l_idx = 0
        elif re.match(r'^\d+', line):
            st.markdown(f"### {line}"); l_idx = 0
        else:
            col1, col2 = st.columns(2)
            with (col1 if l_idx % 2 == 0 else col2):
                with st.container(border=True): st.write(f"**{letras[l_idx%26]})** {line}")
            l_idx += 1

    st.subheader("📥 Escolha como baixar:")
    btn1, btn2 = st.columns(2)
    with btn1:
        pdf_com = gerar_pdf(st.session_state.preview_questoes, com_cabecalho=True)
        st.download_button("🖼️ PDF COM CABEÇALHO", pdf_com, "atividade_com_cabecalho.pdf", use_container_width=True)
    with btn2:
        pdf_sem = gerar_pdf(st.session_state.preview_questoes, com_cabecalho=False)
        st.download_button("📄 PDF SEM CABEÇALHO", pdf_sem, "atividade_sem_cabecalho.pdf", use_container_width=True)