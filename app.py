import streamlit as st
import math
import numpy as np
import os
import random
import re
from fpdf import FPDF

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide", page_icon="🚀")

def clean_txt(text):
    return str(text).encode('latin-1', 'replace').decode('latin-1')

def validar_acesso(pin_digitado):
    try:
        s_aluno = str(st.secrets.get("acesso_aluno", "123456")).strip()
        s_prof = str(st.secrets.get("chave_mestra", "chave_mestra")).strip()
    except:
        s_aluno, s_prof = "123456", "chave_mestra"
    if pin_digitado == s_aluno: return "aluno"
    elif pin_digitado == s_prof: return "admin"
    return "negado"

if 'perfil' not in st.session_state: st.session_state.perfil = None
if 'sub_menu' not in st.session_state: st.session_state.sub_menu = None
if 'preview_data' not in st.session_state: st.session_state.preview_data = []

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

# --- 2. SIDEBAR E MENU ---
perfil = st.session_state.perfil
st.sidebar.title(f"🚀 {perfil.upper()}")
if st.sidebar.button("Sair/Logout"):
    for key in list(st.session_state.keys()): del st.session_state[key]
    st.rerun()

# --- 3. PAINEL PROFESSOR ---
if perfil == "admin":
    st.title("🛠️ Painel de Controle")
    
    st.subheader("📝 Geradores de Atividades (PDF)")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: 
        if st.button("🔢 Operações", use_container_width=True): st.session_state.sub_menu = "op"; st.session_state.preview_data = []
    with c2: 
        if st.button("📐 Equações", use_container_width=True): st.session_state.sub_menu = "eq"; st.session_state.preview_data = []
    with c3: 
        if st.button("📚 Colegial", use_container_width=True): st.session_state.sub_menu = "col"; st.session_state.preview_data = []
    with c4: 
        if st.button("⚖️ Álgebra", use_container_width=True): st.session_state.sub_menu = "alg"; st.session_state.preview_data = []
    with c5: 
        if st.button("📄 Manual", use_container_width=True): st.session_state.sub_menu = "man"; st.session_state.preview_data = []

    op_atual = st.session_state.sub_menu
    if op_atual: st.divider()

    # --- LÓGICA DO MÓDULO COLEGIAL ---
    if op_atual == "col":
        st.header("📚 Gerador Colegial")
        temas = st.multiselect("Escolha o que incluir:", 
                              ["Frações", "Potenciação", "Radiciação", "Sistemas 2x2", "Matrizes Básicas", "Domínio de Funções"], 
                              ["Frações", "Potenciação"])
        qtd_col = st.number_input("Total de questões:", 1, 40, 10)
        
        if st.button("🔍 Gerar/Sortear Novas Questões"):
            qs = []
            for _ in range(qtd_col):
                tema = random.choice(temas)
                if tema == "Frações":
                    op = random.choice(['+', '-', 'x', '÷'])
                    qs.append(f"{random.randint(1,9)}/{random.randint(2,5)} {op} {random.randint(1,9)}/{random.randint(2,5)} =")
                elif tema == "Potenciação":
                    qs.append(f"{random.randint(2,15)}^{random.randint(2,3)} =")
                elif tema == "Radiciação":
                    n = random.randint(2, 12)**2
                    qs.append(f"√{n} =")
                elif tema == "Sistemas 2x2":
                    x, y = random.randint(1,5), random.randint(1,5)
                    a1, b1 = random.randint(1,3), random.randint(1,3)
                    a2, b2 = random.randint(1,3), random.randint(1,3)
                    qs.append(f"Resolva o sistema: {{ {a1}x + {b1}y = {a1*x + b1*y} | {a2}x + {b2}y = {a2*x + b2*y} }}")
                elif tema == "Matrizes Básicas":
                    m = np.random.randint(1, 10, size=(2, 2))
                    qs.append(f"Calcule o determinante da matriz:\n{m}")
                else:
                    qs.append(f"Determine o domínio de f(x) = {random.randint(1,9)} / (x - {random.randint(1,20)})")
            st.session_state.preview_data = qs

    # (Lógica dos outros módulos como Operações e Manual seguem o mesmo padrão...)

    # --- ÁREA DE PREVIEW E PDF ---
    if st.session_state.preview_data:
        st.subheader("👀 Visualização Prévia")
        letras = "abcdefghijklmnopqrstuvwxyz"; l_idx = 0
        with st.container(border=True):
            for linha in st.session_state.preview_data:
                st.write(f"**{letras[l_idx%26]})** {linha}")
                l_idx += 1
        
        if st.button("📥 Gerar PDF"):
            pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=10); l_idx = 0
            if os.path.exists("cabecalho.png"): pdf.image("cabecalho.png", x=12.5, y=8, w=185); pdf.set_y(46)
            pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, clean_txt("Atividade Colegial"), ln=True, align='C'); pdf.ln(5)
            
            for q in st.session_state.preview_data:
                pdf.multi_cell(0, 10, f"{letras[l_idx%26]}) {clean_txt(q)}")
                l_idx += 1
            
            st.download_button("✅ Baixar PDF Agora", pdf.output(dest='S').encode('latin-1', 'replace'), "atividade.pdf")

# --- FERRAMENTAS ONLINE ---
# (Manter calculadoras f(x), PEMDAS e Financeira funcionando normalmente abaixo)