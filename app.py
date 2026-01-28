import streamlit as st
import math
import numpy as np
import os
import random
import re
from fpdf import FPDF

# --- 1. CONFIGURAÇÃO E ESTADO ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide", page_icon="🚀")

if 'perfil' not in st.session_state: st.session_state.perfil = None
if 'sub_menu' not in st.session_state: st.session_state.sub_menu = "man"
if 'preview_questoes' not in st.session_state: st.session_state.preview_questoes = []

def clean_txt(text):
    """Limpa texto para PDF (Latin-1)"""
    if not text: return ""
    rep = {"√": "Raiz de ", "²": "^2", "³": "^3", "÷": "/", "×": "x"}
    for o, n in rep.items(): text = text.replace(o, n)
    return str(text).encode('latin-1', 'replace').decode('latin-1')

def tratar_math(texto):
    """Formata para LaTeX no Streamlit"""
    t = texto.lstrip(',').strip()
    t = re.sub(r'V(\d+)', r'\\sqrt{\1}', t)
    if "^" in t and "^{" not in t:
        t = re.sub(r'\^(\d+)', r'^{\1}', t)
    return t

def validar_acesso(pin_digitado):
    try:
        senha_prof = str(st.secrets.get("chave_mestra", "chave_mestra")).strip().lower()
        senha_aluno = str(st.secrets.get("acesso_aluno", "123456")).strip()
    except:
        senha_prof, senha_aluno = "chave_mestra", "123456"
    if pin_digitado == senha_prof: return "admin"
    if pin_digitado == senha_aluno: return "aluno"
    return "negado"

# --- 2. LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Login Quantum")
    pin = st.text_input("PIN:", type="password")
    if st.button("Entrar"):
        acesso = validar_acesso(pin)
        if acesso != "negado":
            st.session_state.perfil = acesso
            st.rerun()
        else: st.error("PIN incorreto.")
    st.stop()

# --- 3. MENU ---
perfil = st.session_state.perfil
st.sidebar.title(f"🚀 {'Professor' if perfil == 'admin' else 'Estudante'}")
if st.sidebar.button("Sair/Logout"):
    st.session_state.perfil = None
    st.rerun()

# --- 4. PAINEL PROFESSOR ---
if perfil == "admin":
    st.title("🛠️ Painel de Controle")
    
    # Grid de botões para Sub-menus
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: 
        if st.button("🔢 Operações"): st.session_state.sub_menu = "op"
    with c2: 
        if st.button("📐 Equações"): st.session_state.sub_menu = "eq"
    with c3: 
        if st.button("📚 Colegial"): st.session_state.sub_menu = "col"
    with c4: 
        if st.button("💰 Calculadoras"): st.session_state.sub_menu = "calc"
    with c5: 
        if st.button("📄 Manual"): st.session_state.sub_menu = "man"

    op_atual = st.session_state.sub_menu
    st.divider()

    # --- LÓGICA DOS MÓDULOS ---
    if op_atual == "man":
        st.header("📄 Gerador Manual")
        txt_m = st.text_area("Texto (t. Título, . colunas, 1. Seção):", height=200, 
                             value="t. ATIVIDADE DE TESTE\n1. Calcule as raízes:\n,V36\n,V49\n2. Potenciação:\n,5^2\n,10^3")
        if st.button("Gerar Preview"):
            st.session_state.preview_questoes = txt_m.split('\n')

    elif op_atual == "op":
        st.header("🔢 Operações Rápidas")
        qtd = st.number_input("Qtd:", 4, 20, 8)
        if st.button("Gerar Lista"):
            st.session_state.preview_questoes = ["t. OPERAÇÕES", "1. Resolva:"] + [f"{random.randint(10,99)} + {random.randint(10,99)} =" for _ in range(qtd)]

    elif op_atual == "calc":
        st.header("🧮 Calculadoras Online")
        tipo = st.radio("Tipo:", ["f(x)", "Financeira"], horizontal=True)
        if tipo == "f(x)":
            f = st.text_input("f(x):", "x**2")
            x = st.number_input("x:", value=1.0)
            if st.button("Calcular"): st.metric("Resultado", eval(f.replace('x', f'({x})')))
        else:
            pv = st.number_input("Capital:", 1000.0)
            i = st.number_input("Taxa %:", 1.0)
            n = st.number_input("Meses:", 1.0)
            if st.button("Simular"): st.success(f"Montante: {pv * (1 + i/100)**n:.2f}")

# --- 5. VISUALIZAÇÃO UNIFICADA (CARDS + REGRAS) ---
if st.session_state.preview_questoes:
    st.divider()
    if os.path.exists("cabecalho.png"):
        st.image("cabecalho.png", use_container_width=True)
    
    letras = "abcdefghijklmnopqrstuvwxyz"
    l_idx = 0

    for q in st.session_state.preview_questoes:
        line = q.strip()
        if not line: continue
        
        # Título
        if line.lower().startswith(("t.", "titulo:", "título:")):
            t_clean = re.sub(r'^(t\.|titulo:|título:)\s*', '', line, flags=re.IGNORECASE)
            st.markdown(f"<h1 style='text-align: center; color: #007bff;'>{t_clean}</h1>", unsafe_allow_html=True)
            continue

        # Seção Numerada (Reseta letras)
        elif re.match(r'^\d+', line):
            st.markdown(f"### {line}")
            l_idx = 0 
            
        # Itens em Cards
        else:
            with st.container(border=True):
                c1, c2 = st.columns([0.05, 0.95])
                with c1: st.write(f"**{letras[l_idx%26]})**")
                with c2:
                    f = tratar_math(line)
                    if "\\" in f or "^" in f: st.latex(f)
                    else: st.write(line.lstrip(','))
            l_idx += 1

    # --- 6. EXPORTAÇÃO PDF ---
    if st.button("📥 Baixar PDF"):
        pdf = FPDF()
        pdf.add_page()
        if os.path.exists("cabecalho.png"):
            pdf.image("cabecalho.png", x=10, y=8, w=190); pdf.set_y(50)
        else: pdf.set_y(20)
        
        l_idx = 0
        for q in st.session_state.preview_questoes:
            line = q.strip()
            if not line: continue
            
            # Título
            if line.lower().startswith(("t.", "titulo:", "título:")):
                t_pdf = re.sub(r'^(t\.|titulo:|título:)\s*', '', line, flags=re.IGNORECASE)
                pdf.set_font("Arial", 'B', 16); pdf.cell(0, 12, clean_txt(t_pdf), ln=True, align='C'); pdf.ln(5)
            # Número (Reset)
            elif re.match(r'^\d+', line):
                pdf.ln(4); pdf.set_font("Arial", 'B', 12); pdf.multi_cell(0, 8, clean_txt(line)); l_idx = 0
            # Itens
            else:
                pdf.set_font("Arial", size=11)
                # No PDF, Raiz vira "Raiz de" para não bugar
                txt_pdf = line.replace("V", "Raiz de ").replace("√", "Raiz de ").lstrip(',')
                pdf.multi_cell(0, 8, f"{letras[l_idx%26]}) {clean_txt(txt_pdf)}")
                l_idx += 1
        
        st.download_button("✅ Download", pdf.output(dest='S').encode('latin-1'), "atividade.pdf")

else:
    if perfil == "aluno":
        st.title("📖 Área do Estudante")
        st.info("Aguarde o conteúdo do professor.")