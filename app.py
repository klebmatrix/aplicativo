import streamlit as st
import numpy as np
import random
import os
import re
from fpdf import FPDF

# --- CONFIGURAÇÕES ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

def clean_txt(text):
    """Limpa o texto para o PDF não travar"""
    rep = {"√": "V", "²": "^2", "³": "^3", "÷": "/", "×": "*", "{": ""}
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
aba = st.sidebar.radio("Módulos:", ["🔢 Operações", "📐 Equações", "📚 Colegial", "⚖️ Álgebra Linear", "📄 Manual"])

# --- MÓDULO MANUAL ---
if aba == "📄 Manual":
    st.subheader("📝 Digitação Manual")
    txt_input = st.text_area("Digite ou cole sua atividade:", height=300, 
                             placeholder="1. Resolva:\na) ,2V36\nb) ,5^2\n2. Sistema:\na) { 2x+y=20 | x-y=5")
    if st.button("🔍 Gerar Visualização"):
        st.session_state.preview_questoes = txt_input.split('\n')

# --- PROCESSADOR DE MATEMÁTICA ---
def process_math(text):
    # Remove as vírgulas de formatação e letras manuais a), b)
    t = re.sub(r'^[a-z][\)\.]\s*', '', text) # Remove a) ou a.
    t = t.replace(', ', '').replace(',', '') # Remove vírgulas iniciais
    
    # Raiz: 2V36 -> 2\sqrt{36}
    t = re.sub(r'(\d*)V(\d+)', r'\1\\sqrt{\2}', t)
    # Expoente: 5^2 -> 5^{2}
    t = re.sub(r'(\^)(\d+)', r'\1{\2}', t)
    # Fração: 3/4 -> \frac{3}{4}
    if "/" in t and "|" not in t:
        t = re.sub(r'(\d+)/(\d+)', r'\\frac{\1}{\2}', t)
    return t

# --- VISUALIZAÇÃO ---
if st.session_state.preview_questoes:
    st.divider()
    letras = "abcdefghijklmnopqrstuvwxyz"; l_idx = 0
    
    with st.container(border=True):
        for q in st.session_state.preview_questoes:
            line = q.strip()
            if not line: continue
            
            # Títulos
            if line.startswith("t."):
                st.markdown(f"<h2 style='text-align: center;'>{line[2:].strip()}</h2>", unsafe_allow_html=True)
            
            # Sistemas (Detecta [SIS] ou a chave { )
            elif "[SIS]" in line or "{" in line:
                conteudo = line.replace("[SIS]", "").replace("{", "").strip()
                if "|" in conteudo:
                    partes = conteudo.split("|")
                    st.write(f"**{letras[l_idx%26]})**")
                    st.latex(r" \begin{cases} " + partes[0].strip() + r" \\ " + partes[1].strip() + r" \end{cases} ")
                    l_idx += 1
                else:
                    st.write(f"**{letras[l_idx%26]})** {line}")
                    l_idx += 1
            
            # Números (Reseta letras)
            elif re.match(r'^\d+', line):
                st.markdown(f"### {line}")
                l_idx = 0
            
            # Itens
            else:
                formatted = process_math(line)
                if "\\" in formatted or "{" in formatted:
                    st.write(f"**{letras[l_idx%26]})**")
                    st.latex(formatted)
                else:
                    st.write(f"**{letras[l_idx%26]})** {line.replace(',', '')}")
                l_idx += 1

    # --- PDF ---
    if st.button("📥 Baixar PDF"):
        pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=11); l_idx = 0
        if os.path.exists("cabecalho.png"): pdf.image("cabecalho.png", x=12.5, y=8, w=185); pdf.set_y(46)
        
        for q in st.session_state.preview_questoes:
            line = q.strip()
            if not line: continue
            if "[SIS]" in line or "{" in line:
                conteudo = line.replace("[SIS]", "").replace("{", "").strip()
                partes = conteudo.split("|") if "|" in conteudo else [conteudo, ""]
                pdf.set_font("Arial", 'B', 11); pdf.cell(10, 10, f"{letras[l_idx%26]})")
                cx, cy = pdf.get_x(), pdf.get_y()
                pdf.set_font("Courier", size=18); pdf.text(cx, cy + 7, "{"); pdf.set_font("Arial", size=11)
                pdf.text(cx + 5, cy + 4, clean_txt(partes[0])); pdf.text(cx + 5, cy + 9, clean_txt(partes[1]))
                pdf.ln(12); l_idx += 1
            elif line.startswith("t."):
                pdf.ln(5); pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, clean_txt(line[2:].strip()), ln=True, align='C'); pdf.set_font("Arial", size=11)
            elif re.match(r'^\d+', line):
                pdf.ln(4); pdf.set_font("Arial", 'B', 11); pdf.multi_cell(0, 8, clean_txt(line)); pdf.set_font("Arial", size=11); l_idx = 0
            else:
                clean_line = re.sub(r'^[a-z][\)\.]\s*', '', line).replace(',', '')
                pdf.multi_cell(0, 8, f"{letras[l_idx%26]}) {clean_txt(clean_line)}")
                l_idx += 1
        st.download_button("✅ Salvar Atividade", pdf.output(dest='S').encode('latin-1'), "atividade.pdf")