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
    rep = {"√": "V", "²": "^2", "³": "^3", "÷": "/", "×": "x", "{": ""}
    for o, n in rep.items(): text = text.replace(o, n)
    return str(text).encode('latin-1', 'replace').decode('latin-1')

def validar_acesso(pin_digitado):
    try:
        senha_aluno = str(st.secrets.get("acesso_aluno", "123456")).strip()
        senha_prof = str(st.secrets.get("chave_mestra", "chave_mestra")).strip().lower()
    except:
        senha_aluno, senha_prof = "123456", "chave_mestra"
    if pin_digitado == senha_aluno: return "aluno"
    elif pin_digitado == senha_prof: return "admin"
    return "negado"

if 'perfil' not in st.session_state: st.session_state.perfil = None
if 'sub_menu' not in st.session_state: st.session_state.sub_menu = None
if 'preview_questoes' not in st.session_state: st.session_state.preview_questoes = []

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
    st.session_state.perfil = None
    st.session_state.sub_menu = None
    st.rerun()

# --- 3. PAINEL PRINCIPAL (ADMIN) ---
if perfil == "admin":
    st.title("🛠️ Painel de Controle")
    
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

    # --- MÓDULO MANUAL COM CARDS E REGRAS ---
    if op_atual == "man":
        st.header("📄 Gerador Manual")
        tit_m = st.text_input("Título da Atividade:", "ATIVIDADE DE MATEMÁTICA")
        txt_m = st.text_area("Digite as questões (Linha com número reseta as letras):", height=200,
                             value="1. Resolva as expressões:\n,2V36\n,5^2 + 10\n2. Calcule o X:\n,2x + 5 = 15")
        
        if st.button("🔍 Visualizar Cards"):
            st.session_state.preview_questoes = txt_m.split('\n')

        if st.session_state.preview_questoes:
            st.divider()
            # 1. IMAGEM NO TOPO (HEADER)
            if os.path.exists("cabecalho.png"):
                st.image("cabecalho.png", use_container_width=True)
            
            # 2. TÍTULO
            st.markdown(f"<h1 style='text-align: center;'>{tit_m}</h1>", unsafe_allow_html=True)
            
            letras = "abcdefghijklmnopqrstuvwxyz"
            l_idx = 0
            
            for linha in st.session_state.preview_questoes:
                t = linha.strip()
                if not t: continue
                
                # Regra: Se a linha começa com número, exibe título e reseta letra
                if re.match(r'^\d+', t):
                    st.markdown(f"### {t}")
                    l_idx = 0
                else:
                    # Estilo de CARD para os itens
                    with st.container(border=True):
                        col_letra, col_math = st.columns([0.1, 0.9])
                        with col_letra:
                            st.write(f"**{letras[l_idx%26]})**")
                        with col_math:
                            # Lógica para Sistemas ou Math
                            if "{" in t or "|" in t:
                                p = t.replace("{", "").split("|")
                                if len(p) > 1:
                                    st.latex(r" \begin{cases} " + p[0].strip() + r" \\ " + p[1].strip() + r" \end{cases} ")
                                else: st.write(t)
                            else:
                                # Limpeza de vírgula inicial e formatação básica
                                math_line = t.lstrip(',')
                                if "V" in math_line or "^" in math_line or "/" in math_line:
                                    # Formatação simples para o latex
                                    f = math_line.replace("V", "\\sqrt{") + "}" if "V" in math_line else math_line
                                    st.latex(f.replace("^", "^{") + "}" if "^" in f else f)
                                else:
                                    st.write(math_line)
                    l_idx += 1

            # --- BOTÃO DE EXPORTAR PDF (MANUAL) ---
            if st.button("📥 Baixar PDF Manual"):
                pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=11)
                if os.path.exists("cabecalho.png"):
                    pdf.image("cabecalho.png", x=12.5, y=8, w=185)
                    pdf.set_y(50)
                
                pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, clean_txt(tit_m), ln=True, align='C'); pdf.ln(5)
                pdf.set_font("Arial", size=11); l_idx = 0
                
                for linha in st.session_state.preview_questoes:
                    t = linha.strip()
                    if not t: continue
                    if re.match(r'^\d+', t):
                        pdf.ln(5); pdf.set_font("Arial", 'B', 12); pdf.multi_cell(0, 8, clean_txt(t))
                        pdf.set_font("Arial", size=11); l_idx = 0
                    else:
                        item = t.lstrip(',')
                        pdf.multi_cell(0, 8, f"{letras[l_idx%26]}) {clean_txt(item)}")
                        l_idx += 1
                st.download_button("✅ Download PDF", pdf.output(dest='S').encode('latin-1'), "manual.pdf")

    # (Mantenha os outros ELIFs de op, eq, col, alg conforme seu código original...)
    elif op_atual == "op":
        st.header("🔢 Operações")
        # ... seu código original aqui ...