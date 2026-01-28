import streamlit as st
import numpy as np
import random
import os
import re
from fpdf import FPDF

# --- 1. CONFIGURAÇÕES E UTILITÁRIOS ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide", page_icon="🚀")

def clean_txt(text):
    """Trata caracteres especiais para o PDF."""
    rep = {"√": "V", "²": "^2", "³": "^3", "÷": "/", "×": "x", "{": ""}
    for o, n in rep.items(): text = text.replace(o, n)
    return str(text).encode('latin-1', 'replace').decode('latin-1')

def tratar_math(texto):
    """Converte sintaxe simplificada em LaTeX para o Streamlit."""
    t = texto.lstrip(',').strip()
    # Converte V36 para \sqrt{36}
    t = re.sub(r'V(\d+)', r'\\sqrt{\1}', t)
    # Converte ^2 para ^{2} se necessário
    if "^" in t and "^{" not in t:
        t = re.sub(r'\^(\d+)', r'^{\1}', t)
    return t

def validar_acesso(pin_digitado):
    try:
        # Recupera as senhas do ambiente (Render)
        senha_prof = str(st.secrets.get("chave_mestra", "12345678")).strip()
        senha_aluno = str(st.secrets.get("acesso_aluno", "123456")).strip()
    except:
        senha_prof, senha_aluno = "12345678", "123456"
    
    if pin_digitado == senha_prof: return "admin"
    if pin_digitado == senha_aluno: return "aluno"
    return "negado"

# --- 2. LOGIN ---
if 'perfil' not in st.session_state: st.session_state.perfil = None
if 'preview_questoes' not in st.session_state: st.session_state.preview_questoes = []
if 'sub_menu' not in st.session_state: st.session_state.sub_menu = "man"

if st.session_state.perfil is None:
    st.title("🔐 Login Quantum")
    pin = st.text_input("PIN de Acesso:", type="password")
    if st.button("Entrar"):
        acesso = validar_acesso(pin)
        if acesso != "negado":
            st.session_state.perfil = acesso
            st.rerun()
        else: st.error("PIN incorreto.")
    st.stop()

# --- 3. MENU LATERAL ---
perfil = st.session_state.perfil
st.sidebar.title(f"🚀 {'Professor' if perfil == 'admin' else 'Estudante'}")

if perfil == "admin":
    st.sidebar.subheader("Geradores")
    if st.sidebar.button("📄 Gerador Manual"): st.session_state.sub_menu = "man"
    if st.sidebar.button("🔢 Operações Básicas"): st.session_state.sub_menu = "op"
    if st.sidebar.button("📐 Equações"): st.session_state.sub_menu = "eq"
    if st.sidebar.button("⚖️ Álgebra Linear"): st.session_state.sub_menu = "alg"

if st.sidebar.button("Sair/Logout"):
    st.session_state.perfil = None
    st.session_state.preview_questoes = []
    st.rerun()

# --- 4. ÁREA DE CRIAÇÃO (SÓ ADMIN) ---
if perfil == "admin":
    aba = st.session_state.sub_menu
    st.title(f"🛠️ Painel: {aba.upper()}")

    if aba == "man":
        txt_input = st.text_area("Entrada (t. para título, número para seção):", height=200, 
                                 value="t. ATIVIDADE DE TESTE\n1. Seção de Cálculo:\n,V36\n,5^2\n2. Seção de Texto:\nQuestão exemplo")
        if st.button("🔍 Gerar Preview"):
            st.session_state.preview_questoes = txt_input.split('\n')

    elif aba == "op":
        qtd = st.number_input("Qtd questões:", 4, 30, 10)
        if st.button("Gerar Operações"):
            st.session_state.preview_questoes = ["t. OPERAÇÕES MATEMÁTICAS", "1. Calcule:"] + [f"{random.randint(10,99)} + {random.randint(10,99)} =" for _ in range(qtd)]

    elif aba == "eq":
        if st.button("Gerar Equações"):
            st.session_state.preview_questoes = ["t. EQUAÇÕES", "1. Resolva x:"] + [f"{random.randint(2,9)}x + {random.randint(1,10)} = {random.randint(11,50)}" for _ in range(5)]

# --- 5. RENDERIZAÇÃO UNIFICADA (CARDS + REGRAS) ---
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
        
        # A) Reconhecimento de Título
        if line.lower().startswith(("t.", "titulo:", "título:")):
            t_clean = re.sub(r'^(t\.|titulo:|título:)\s*', '', line, flags=re.IGNORECASE)
            st.markdown(f"<h1 style='text-align: center; color: #007bff;'>{t_clean}</h1>", unsafe_allow_html=True)
            st.divider()
            continue

        # B) Seção Numerada (Reseta letras)
        elif re.match(r'^\d+', line):
            st.markdown(f"### {line}")
            l_idx = 0 
            
        # C) Itens em Cards
        else:
            with st.container(border=True):
                c1, c2 = st.columns([0.05, 0.95])
                with c1: st.write(f"**{letras[l_idx%26]})**")
                with c2:
                    if "{" in line or "|" in line:
                        cont = line.replace("{", "").strip()
                        partes = cont.split("|") if "|" in cont else [cont]
                        if len(partes) > 1:
                            st.latex(r" \begin{cases} " + partes[0].strip() + r" \\ " + partes[1].strip() + r" \end{cases} ")
                        else: st.write(line)
                    else:
                        f = tratar_math(line)
                        if "\\" in f or "^" in f: st.latex(f)
                        else: st.write(line.lstrip(','))
            l_idx += 1

    # --- 6. EXPORTAÇÃO PDF ---
    if st.button("📥 Baixar Atividade em PDF"):
        pdf = FPDF()
        pdf.add_page()
        if os.path.exists("cabecalho.png"):
            pdf.image("cabecalho.png", x=10, y=8, w=190)
            pdf.set_y(50)
        
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
                
        st.download_button("✅ Download PDF", pdf.output(dest='S').encode('latin-1'), "atividade.pdf")