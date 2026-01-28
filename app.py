import streamlit as st
import numpy as np
import random
import os
import re
from fpdf import FPDF

# --- 1. CONFIGURAÇÕES ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

def clean_txt(text):
    """Limpa texto para o PDF não travar"""
    rep = {"√": "V", "²": "^2", "³": "^3", "÷": "/", "×": "x", "{": ""}
    for o, n in rep.items(): text = text.replace(o, n)
    return str(text).encode('latin-1', 'replace').decode('latin-1')

if 'perfil' not in st.session_state: st.session_state.perfil = None
if 'preview_questoes' not in st.session_state: st.session_state.preview_questoes = []

# --- 2. LOGIN (SIMPLIFICADO PARA NÃO TRAVAR) ---
if st.session_state.perfil is None:
    st.title("🔐 Login")
    pin = st.text_input("PIN:", type="password")
    if st.button("Entrar"):
        # Se falhar o segredo, a senha é 'chave_mestra'
        try:
            chave = str(st.secrets.get("chave_mestra", "chave_mestra")).strip().lower()
        except:
            chave = "chave_mestra"
            
        if pin == chave: 
            st.session_state.perfil = "admin"
            st.rerun()
        else: st.error("PIN incorreto.")
    st.stop()

# --- 3. MENU LATERAL ---
with st.sidebar:
    st.header("🚀 Menu")
    aba = st.radio("Módulos:", ["📄 Manual", "🔢 Operações", "📐 Equações", "📚 Colegial"])
    if st.button("Sair"):
        st.session_state.perfil = None
        st.rerun()

# --- 4. TRATAMENTO MATEMÁTICO ---
def formatar_math(texto):
    t = re.sub(r'^[a-z][\)\.]\s*', '', texto) # Limpa a), b)
    t = t.replace(', ', '').replace(',', '').strip() # Limpa vírgulas
    
    # Raiz: 3V27 -> \sqrt[3]{27} | V25 -> \sqrt{25}
    t = re.sub(r'(\d+)V(\d+)', r'\\sqrt[\1]{\2}', t)
    t = re.sub(r'(?<!\[)V(\d+)', r'\\sqrt{\1}', t)
    
    # Potência: 5^4 -> 5^{4}
    t = re.sub(r'(\^)(\d+)', r'\1{\2}', t)
    
    # Fração: 1/2 -> \frac{1}{2}
    if "/" in t and "|" not in t:
        t = re.sub(r'(\d+)/(\d+)', r'\\frac{\1}{\2}', t)
    return t

# --- 5. INTERFACE ---
st.title(f"Módulo: {aba}")

if aba == "📄 Manual":
    st.info("💡 Use: V para Raiz | ^ para Potência | / para Fração | { eq1 | eq2 para Sistema")
    txt_input = st.text_area("Digite sua atividade:", height=250, 
                             value="1. Resolva:\na) ,2V36 =\nb) ,5^2 + 10 =\nc) ,3/4 de 200 =\n2. Sistema:\na) { 2x + y = 20 | x - y = 5")
    if st.button("🔍 Gerar Preview"):
        st.session_state.preview_questoes = txt_input.split('\n')
else:
    st.warning("Módulo em manutenção. Por favor, use o Manual.")

# --- 6. VISUALIZAÇÃO EM CARDS ---
if st.session_state.preview_questoes:
    st.divider()
    letras = "abcdefghijklmnopqrstuvwxyz"; l_idx = 0
    
    # Tenta carregar imagem se existir
    if os.path.exists("cabecalho.png"):
        st.image("cabecalho.png", use_container_width=True)

    for q in st.session_state.preview_questoes:
        line = q.strip()
        if not line: continue
        
        # Títulos
        if line.startswith("t."):
            st.markdown(f"<h2 style='text-align: center;'>{line[2:].strip()}</h2>", unsafe_allow_html=True)
        # Números (Reset de letras)
        elif re.match(r'^\d+', line):
            st.markdown(f"### {line}")
            l_idx = 0
        # Itens em Cards
        else:
            with st.container(border=True): # O card oficial do Streamlit
                col1, col2 = st.columns([0.1, 0.9])
                with col1: st.write(f"**{letras[l_idx%26]})**")
                with col2:
                    if "{" in line or "|" in line:
                        cont = line.replace("{", "").strip()
                        if "|" in cont:
                            p = cont.split("|")
                            st.latex(r" \begin{cases} " + p[0].strip() + r" \\ " + p[1].strip() + r" \end{cases} ")
                        else: st.write(line)
                    else:
                        f = formatar_math(line)
                        if "\\" in f or "{" in f: st.latex(f)
                        else: st.write(line.replace(',', ''))
            l_idx += 1

    # --- 7. DOWNLOAD ---
    if st.button("📥 Baixar PDF"):
        pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=11); l_idx = 0
        if os.path.exists("cabecalho.png"): pdf.image("cabecalho.png", x=12.5, y=8, w=185); pdf.set_y(46)
        
        for q in st.session_state.preview_questoes:
            line = q.strip()
            if not line: continue
            if "{" in line and "|" in line:
                p = line.replace("{", "").split("|")
                pdf.set_font("Arial", 'B', 11); pdf.cell(10, 10, f"{letras[l_idx%26]})")
                cx, cy = pdf.get_x(), pdf.get_y()
                pdf.set_font("Courier", size=18); pdf.text(cx, cy + 7, "{"); pdf.set_font("Arial", size=11)
                pdf.text(cx + 5, cy + 4, clean_txt(p[0])); pdf.text(cx + 5, cy + 9, clean_txt(p[1]))
                pdf.ln(12); l_idx += 1
            elif line.startswith("t."):
                pdf.ln(5); pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, clean_txt(line[2:].strip()), ln=True, align='C'); pdf.set_font("Arial", size=11)
            elif re.match(r'^\d+', line):
                pdf.ln(4); pdf.set_font("Arial", 'B', 11); pdf.multi_cell(0, 8, clean_txt(line)); pdf.set_font("Arial", size=11); l_idx = 0
            else:
                item = re.sub(r'^[a-z][\)\.]\s*', '', line).replace(',', '')
                pdf.multi_cell(0, 8, f"{letras[l_idx%26]}) {clean_txt(item)}")
                l_idx += 1
        st.download_button("✅ Download", pdf.output(dest='S').encode('latin-1'), "atividade.pdf")