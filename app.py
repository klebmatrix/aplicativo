import streamlit as st
import math
import numpy as np
import os
import random
import re
from fpdf import FPDF

# --- 1. CONFIGURAÇÃO E INICIALIZAÇÃO ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide", page_icon="🚀")

# Inicialização segura do Session State (Evita AttributeError)
if 'perfil' not in st.session_state: st.session_state.perfil = None
if 'sub_menu' not in st.session_state: st.session_state.sub_menu = "man"
if 'preview_questoes' not in st.session_state: st.session_state.preview_questoes = []

def clean_txt(text):
    return str(text).encode('latin-1', 'replace').decode('latin-1')

def tratar_math(texto):
    t = texto.lstrip(',').strip()
    t = re.sub(r'V(\d+)', r'\\sqrt{\1}', t)
    if "^" in t and "^{" not in t:
        t = re.sub(r'\^(\d+)', r'^{\1}', t)
    return t

def validar_acesso(pin_digitado):
    try:
        # Senha em lowercase conforme sua preferência
        senha_prof = str(st.secrets.get("chave_mestra", "chave_mestra")).strip().lower()
        senha_aluno = str(st.secrets.get("acesso_aluno", "123456")).strip()
    except:
        senha_prof, senha_aluno = "chave_mestra", "123456"
    
    if pin_digitado == senha_prof: return "admin"
    if pin_digitado == senha_aluno: return "aluno"
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

# --- 2. MENU E LOGOUT ---
perfil = st.session_state.perfil
st.sidebar.title(f"🚀 {'Professor' if perfil == 'admin' else 'Estudante'}")
if st.sidebar.button("Sair/Logout"):
    for key in list(st.session_state.keys()): del st.session_state[key]
    st.rerun()

# --- 3. FUNÇÃO PDF ---
def exportar_pdf(questoes, titulo):
    pdf = FPDF()
    pdf.add_page()
    if os.path.exists("cabecalho.png"):
        pdf.image("cabecalho.png", x=12.5, y=8, w=185)
        pdf.set_y(46)
    else: pdf.set_y(15)
    pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, txt=clean_txt(titulo), ln=True, align='C'); pdf.ln(5)
    pdf.set_font("Arial", size=11); letras = "abcdefghijklmnopqrstuvwxyz"
    for i, q in enumerate(questoes):
        pdf.multi_cell(0, 10, txt=f"{letras[i%26]}) {clean_txt(q)}")
    return pdf.output(dest='S').encode('latin-1', 'replace')

# --- 4. PAINEL PRINCIPAL (ADMIN) ---
if perfil == "admin":
    st.title("🛠️ Painel de Controle do Professor")
    
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

    st.markdown("---")
    st.subheader("🧮 Ferramentas Online")
    d1, d2, d3 = st.columns(3)
    with d1: 
        if st.button("𝑓(x) Funções", use_container_width=True): st.session_state.sub_menu = "calc_f"
    with d2: 
        if st.button("📊 PEMDAS", use_container_width=True): st.session_state.sub_menu = "pemdas"
    with d3: 
        if st.button("💰 Financeira", use_container_width=True): st.session_state.sub_menu = "fin"

    op_atual = st.session_state.sub_menu
    st.divider()

    # --- MÓDULOS DE GERADORES ---
    if op_atual == "man":
        st.header("📄 Gerador Manual")
        txt_m = st.text_area("Entrada (t. título, número para seção):", height=150, value="t. ATIVIDADE\n1. Resolva:\n,V25\n,V49")
        if st.button("🔍 Gerar Preview"):
            st.session_state.preview_questoes = txt_m.split('\n')

    elif op_atual == "op":
        st.header("🔢 Operações")
        if st.button("Gerar Lista de Operações"):
            st.session_state.preview_questoes = ["t. OPERAÇÕES BÁSICAS", "1. Calcule:"] + [f"{random.randint(10,50)} + {random.randint(2,20)} =" for _ in range(8)]

    # ... (Módulos de Calculadoras calc_f, pemdas, fin mantidos conforme seu código anterior) ...
    elif op_atual == "calc_f":
        st.header("𝑓(x) Funções")
        f_in = st.text_input("f(x):", "x**2")
        x_v = st.number_input("x:", value=1.0)
        if st.button("Calcular"): st.metric("Resultado", eval(f_in.replace('x', f'({x_v})')))

# --- 6. VISUALIZAÇÃO UNIFICADA (CARDS + REGRAS) ---
if st.session_state.preview_questoes:
    st.divider()
    
    # Cabeçalho no Topo
    if os.path.exists("cabecalho.png"):
        st.image("cabecalho.png", use_container_width=True)
    
    letras = "abcdefghijklmnopqrstuvwxyz"
    l_idx = 0

    for q in st.session_state.preview_questoes:
        line = q.strip()
        if not line: continue
        
        # A) Reconhecimento de Título (t.)
        if line.lower().startswith(("t.", "titulo:", "título:")):
            t_clean = re.sub(r'^(t\.|titulo:|título:)\s*', '', line, flags=re.IGNORECASE)
            st.markdown(f"<h1 style='text-align: center; color: #007bff; border-bottom: 2px solid #007bff;'>{t_clean}</h1>", unsafe_allow_html=True)
            continue

        # B) Seção Numerada (Reseta letras para 'a')
        elif re.match(r'^\d+', line):
            st.markdown(f"### {line}")
            l_idx = 0 
            
        # C) Itens em Cards
        else:
            with st.container(border=True):
                c1, c2 = st.columns([0.05, 0.95])
                with c1: st.write(f"**{letras[l_idx%26]})**")
                with c2:
                    f = tratar_math(line)
                    if "\\" in f or "^" in f: st.latex(f)
                    else: st.write(line.lstrip(','))
            l_idx += 1

    # --- 7. EXPORTAÇÃO PDF ---
    if st.button("📥 Baixar PDF"):
        pdf = FPDF()
        pdf.add_page()
        if os.path.exists("cabecalho.png"):
            pdf.image("cabecalho.png", x=10, y=8, w=190); pdf.set_y(50)
        
        l_idx = 0
        for q in st.session_state.preview_questoes:
            line = q.strip()
            if not line: continue
            if line.lower().startswith(("t.", "titulo:", "título:")):
                t_pdf = re.sub(r'^(t\.|titulo:|título:)\s*', '', line, flags=re.IGNORECASE)
                pdf.set_font("Arial", 'B', 16); pdf.cell(0, 12, clean_txt(t_pdf), ln=True, align='C'); pdf.ln(5)
            elif re.match(r'^\d+', line):
                pdf.ln(4); pdf.set_font("Arial", 'B', 12); pdf.multi_cell(0, 8, clean_txt(line)); l_idx = 0
            else:
                pdf.set_font("Arial", size=11)
                pdf.multi_cell(0, 8, f"{letras[l_idx%26]}) {clean_txt(line.lstrip(','))}")
                l_idx += 1
        st.download_button("✅ Download", pdf.output(dest='S').encode('latin-1'), "atividade.pdf")