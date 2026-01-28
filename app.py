import streamlit as st
import numpy as np
import random
import os
import re
from fpdf import FPDF

# --- CONFIGURAÇÕES ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

def clean_txt(text):
    """Substitui símbolos para evitar erro no PDF"""
    rep = {"√": "V", "²": "^2", "³": "^3", "÷": "/", "×": "*"}
    for o, n in rep.items():
        text = text.replace(o, n)
    return str(text).encode('latin-1', 'replace').decode('latin-1')

if 'perfil' not in st.session_state: st.session_state.perfil = None
if 'preview_questoes' not in st.session_state: st.session_state.preview_questoes = []

# --- LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Login")
    pin = st.text_input("PIN:", type="password")
    if st.button("Entrar"):
        s_prof = str(st.secrets.get("chave_mestra", "chave_mestra")).strip().lower()
        if pin == s_prof: 
            st.session_state.perfil = "admin"
            st.rerun()
        else: st.error("PIN Inválido.")
    st.stop()

# --- MENU ---
st.sidebar.title(f"🚀 {st.session_state.perfil.upper()}")
aba = st.sidebar.radio("Módulos:", ["🔢 Operações", "📐 Equações", "📚 Colegial", "⚖️ Álgebra Linear", "📄 Manual", "🧮 Calculadoras"])

# --- MÓDULO MANUAL ---
if aba == "📄 Manual":
    st.subheader("📝 Módulo Manual")
    st.info("💡 Exemplo: 2V36 | 5^2 | 3/4 | [SIS] x+y=5 | x-y=1")
    txt_input = st.text_area("Digite sua atividade:", height=300, 
                             value="t. ATIVIDADE\n1. Resolva as questões:\n2V36 =\n5^2 + 10 =\n3/4 de 200 =\n2. Resolva o sistema:\n[SIS] x+y=10 | x-y=2")
    if st.button("🔍 Gerar Visualização"):
        st.session_state.preview_questoes = txt_input.split('\n')

# --- PROCESSADOR DE MATEMÁTICA (LaTeX) ---
def format_math_line(text):
    """Converte texto simples em LaTeX para o Preview"""
    # Trata Raiz: nVbase -> n \sqrt{base}
    text = re.sub(r'(\d+)V(\d+)', r'\1\\sqrt{\2}', text)
    # Trata Raiz simples: Vbase -> \sqrt{base}
    text = re.sub(r'(?<!\\)V(\d+)', r'\\sqrt{\1}', text)
    # Trata Expoente: x^y -> x^{y}
    text = re.sub(r'(\^)(\d+)', r'\1{\2}', text)
    # Trata Fração: a/b -> \frac{a}{b}
    if "/" in text and "|" not in text:
        text = re.sub(r'(\d+)/(\d+)', r'\\frac{\1}{\2}', text)
    return text

# --- VISUALIZAÇÃO ---
if st.session_state.preview_questoes:
    st.divider()
    letras = "abcdefghijklmnopqrstuvwxyz"; l_idx = 0
    
    with st.container(border=True):
        for q in st.session_state.preview_questoes:
            line = q.strip()
            if not line: continue
            
            # Títulos (t.)
            if line.startswith("t."):
                st.markdown(f"<h2 style='text-align: center;'>{line[2:].strip()}</h2>", unsafe_allow_html=True)
            
            # Sistemas ([SIS])
            elif "[SIS]" in line:
                partes = line.replace("[SIS]", "").split("|")
                st.write(f"**{letras[l_idx%26]})**")
                st.latex(r" \begin{cases} " + partes[0].strip() + r" \\ " + partes[1].strip() + r" \end{cases} ")
                l_idx += 1
            
            # Reset de letras com números (Ex: 1., 2.)
            elif re.match(r'^\d+[.\)]', line):
                st.markdown(f"### {line}")
                l_idx = 0
            
            # Itens normais (com Raiz, Expoente e Fração)
            else:
                # Remove a letra se o usuário já tiver digitado (ex: "a) ")
                clean_line = re.sub(r'^[a-z][\)\.]\s*', '', line)
                math_ready = format_math_line(clean_line)
                
                if "\\" in math_ready or "{" in math_ready:
                    st.write(f"**{letras[l_idx%26]})**")
                    st.latex(math_ready)
                else:
                    st.write(f"**{letras[l_idx%26]})** {clean_line}")
                l_idx += 1

    # --- PDF ---
    if st.button("📥 Baixar PDF"):
        pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=11); l_idx = 0
        if os.path.exists("cabecalho.png"): pdf.image("cabecalho.png", x=12.5, y=8, w=185); pdf.set_y(46)
        
        for q in st.session_state.preview_questoes:
            line = q.strip()
            if not line: continue
            if "[SIS]" in line:
                partes = line.replace("[SIS]", "").split("|")
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
                clean_line = re.sub(r'^[a-z][\)\.]\s*', '', line)
                pdf.multi_cell(0, 8, f"{letras[l_idx%26]}) {clean_txt(clean_line)}")
                l_idx += 1
        st.download_button("✅ Download", pdf.output(dest='S').encode('latin-1'), "atividade.pdf")