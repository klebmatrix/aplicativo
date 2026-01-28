import streamlit as st
import numpy as np
import random
import os
import re
from fpdf import FPDF

# --- 1. CONFIGURAÇÕES E ESTILIZAÇÃO ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

# CSS para criar o efeito de Cards no Preview
st.markdown("""
    <style>
    .math-card {
        background-color: #f9f9f9;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        border-left: 5px solid #007bff;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

def clean_txt(text):
    rep = {"√": "V", "²": "^2", "³": "^3", "÷": "/", "×": "x", "{": ""}
    for o, n in rep.items(): text = text.replace(o, n)
    return str(text).encode('latin-1', 'replace').decode('latin-1')

if 'perfil' not in st.session_state: st.session_state.perfil = None
if 'preview_questoes' not in st.session_state: st.session_state.preview_questoes = []

# --- 2. LOGIN SEGURO ---
if st.session_state.perfil is None:
    st.title("🔐 Acesso")
    pin = st.text_input("PIN:", type="password")
    if st.button("Entrar"):
        try: s_prof = str(st.secrets.get("chave_mestra", "chave_mestra")).strip().lower()
        except: s_prof = "chave_mestra"
        if pin == s_prof: 
            st.session_state.perfil = "admin"
            st.rerun()
        else: st.error("PIN incorreto.")
    st.stop()

# --- 3. MENU LATERAL (ESTÁVEL) ---
with st.sidebar:
    st.header("🚀 Menu")
    aba = st.radio("Escolha:", ["🔢 Operações", "📐 Equações", "📚 Colegial", "⚖️ Álgebra Linear", "📄 Manual"])
    if st.button("Sair"):
        st.session_state.perfil = None
        st.rerun()

# --- 4. FUNÇÕES DE APOIO ---
def tratar_math(texto):
    t = re.sub(r'^[a-z][\)\.]\s*', '', texto)
    t = t.replace(', ', '').replace(',', '').strip()
    t = re.sub(r'(\d*)V(\d+)', r'\1\\sqrt{\2}', t)
    t = re.sub(r'(\^)(\d+)', r'\1{\2}', t)
    if "/" in t and "|" not in t: t = re.sub(r'(\d+)/(\d+)', r'\\frac{\1}{\2}', t)
    return t

# --- 5. INTERFACE DOS MÓDULOS ---
st.title(f"Módulo: {aba}")

if aba == "📄 Manual":
    txt_input = st.text_area("Digite sua atividade:", height=250, 
                             value="1. Operações:\na) ,2V36\nb) ,5^2\n2. Sistema:\na) { 2x+y=20 | x-y=5")
    if st.button("🔍 Gerar Atividade"):
        st.session_state.preview_questoes = txt_input.split('\n')

elif aba == "📚 Colegial":
    if st.button("Gerar Exemplos"):
        st.session_state.preview_questoes = ["1. Exercícios:", "V144", "3V27", "2^4", "3/5 + 1/5"]

# --- 6. VISUALIZAÇÃO EM CARDS (PREVIEW) ---
if st.session_state.preview_questoes:
    st.divider()
    letras = "abcdefghijklmnopqrstuvwxyz"
    l_idx = 0
    
    # Imagem de Cabeçalho (Sempre no topo como solicitado)
    if os.path.exists("cabecalho.png"):
        st.image("cabecalho.png", use_container_width=True)

    for q in st.session_state.preview_questoes:
        line = q.strip()
        if not line: continue
        
        # Títulos
        if line.startswith("t."):
            st.markdown(f"<h2 style='text-align: center;'>{line[2:].strip()}</h2>", unsafe_allow_html=True)
        
        # Números (Questões Principais)
        elif re.match(r'^\d+', line):
            st.markdown(f"### {line}")
            l_idx = 0
        
        # Itens em CARDS
        else:
            with st.container():
                st.markdown('<div class="math-card">', unsafe_allow_html=True)
                col1, col2 = st.columns([0.1, 0.9])
                with col1:
                    st.write(f"**{letras[l_idx%26]})**")
                with col2:
                    if "{" in line or "|" in line:
                        conteudo = line.replace("{", "").strip()
                        if "|" in conteudo:
                            partes = conteudo.split("|")
                            st.latex(r" \begin{cases} " + partes[0].strip() + r" \\ " + partes[1].strip() + r" \end{cases} ")
                        else: st.write(line)
                    else:
                        formato = tratar_math(line)
                        if "\\" in formato or "{" in formato: st.latex(formato)
                        else: st.write(line.replace(',', ''))
                st.markdown('</div>', unsafe_allow_html=True)
                l_idx += 1

    # --- 7. BOTÃO DE PDF ---
    if st.button("📥 Baixar Atividade"):
        pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=11); l_idx = 0
        if os.path.exists("cabecalho.png"): pdf.image("cabecalho.png", x=12.5, y=8, w=185); pdf.set_y(46)
        
        for q in st.session_state.preview_questoes:
            line = q.strip()
            if not line: continue
            if "{" in line and "|" in line:
                partes = line.replace("{", "").split("|")
                pdf.set_font("Arial", 'B', 11); pdf.cell(10, 10, f"{letras[l_idx%26]})")
                cx, cy = pdf.get_x(), pdf.get_y()
                pdf.set_font("Courier", size=18); pdf.text(cx, cy + 7, "{"); pdf.set_font("Arial", size=11)
                pdf.text(cx + 5, cy + 4, clean_txt(partes[0].strip())); pdf.text(cx + 5, cy + 9, clean_txt(partes[1].strip()))
                pdf.ln(12); l_idx += 1
            elif line.startswith("t."):
                pdf.ln(5); pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, clean_txt(line[2:].strip()), ln=True, align='C'); pdf.set_font("Arial", size=11)
            elif re.match(r'^\d+', line):
                pdf.ln(4); pdf.set_font("Arial", 'B', 11); pdf.multi_cell(0, 8, clean_txt(line)); pdf.set_font("Arial", size=11); l_idx = 0
            else:
                item = re.sub(r'^[a-z][\)\.]\s*', '', line).replace(',', '')
                pdf.multi_cell(0, 8, f"{letras[l_idx%26]}) {clean_txt(item)}")
                l_idx += 1
        st.download_button("✅ Download PDF", pdf.output(dest='S').encode('latin-1'), "atividade.pdf")