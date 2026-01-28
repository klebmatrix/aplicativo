import streamlit as st
import numpy as np
import random
import os
import re
from fpdf import FPDF

# --- 1. CONFIGURAÇÕES INICIAIS ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

# Inicialização de estado para evitar que o menu suma
if 'perfil' not in st.session_state: st.session_state.perfil = None
if 'preview_questoes' not in st.session_state: st.session_state.preview_questoes = []

def clean_txt(text):
    rep = {"√": "V", "²": "^2", "³": "^3", "÷": "/", "×": "x", "{": ""}
    for o, n in rep.items(): text = text.replace(o, n)
    return str(text).encode('latin-1', 'replace').decode('latin-1')

# --- 2. LOGIN (SIMPLIFICADO) ---
if st.session_state.perfil is None:
    st.title("🔐 Acesso Quantum Lab")
    pin = st.text_input("PIN:", type="password")
    if st.button("Entrar"):
        # Se o secrets falhar, o login será 'chave_mestra' por padrão
        try:
            chave = str(st.secrets.get("chave_mestra", "chave_mestra")).strip().lower()
        except:
            chave = "chave_mestra"
            
        if pin == chave: 
            st.session_state.perfil = "admin"
            st.rerun()
        else: 
            st.error("PIN incorreto.")
    st.stop()

# --- 3. MENU LATERAL (SEGURO) ---
with st.sidebar:
    st.header("🚀 Menu Principal")
    aba = st.radio("Módulos:", ["📄 Manual", "🔢 Operações", "📐 Equações", "📚 Colegial"])
    st.divider()
    if st.button("Sair"):
        st.session_state.perfil = None
        st.rerun()

# --- 4. FUNÇÃO DE MATEMÁTICA ---
def formatar_math(texto):
    t = re.sub(r'^[a-z][\)\.]\s*', '', texto) # Limpa a), b)
    t = t.replace(', ', '').replace(',', '').strip() # Limpa vírgulas
    t = re.sub(r'(\d*)V(\d+)', r'\1\\sqrt{\2}', t) # Raiz
    t = re.sub(r'(\^)(\d+)', r'\1{\2}', t) # Potência
    if "/" in t and "|" not in t: 
        t = re.sub(r'(\d+)/(\d+)', r'\\frac{\1}{\2}', t) # Fração
    return t

# --- 5. INTERFACE ---
st.title(f"Módulo: {aba}")

if aba == "📄 Manual":
    txt_input = st.text_area("Digite sua atividade:", height=250, 
                             value="1. Operações:\na) ,2V36\nb) ,5^2\n2. Sistema:\na) { 2x+y=20 | x-y=5")
    if st.button("🔍 Gerar Preview"):
        st.session_state.preview_questoes = txt_input.split('\n')
else:
    st.info("Módulo em manutenção. Use o Manual para criar questões.")

# --- 6. PREVIEW COM CARDS NATIVOS ---
if st.session_state.preview_questoes:
    st.divider()
    letras = "abcdefghijklmnopqrstuvwxyz"; l_idx = 0
    
    # Cabeçalho no Topo
    if os.path.exists("cabecalho.png"):
        st.image("cabecalho.png", use_container_width=True)

    for q in st.session_state.preview_questoes:
        line = q.strip()
        if not line: continue
        
        if line.startswith("t."):
            st.markdown(f"<h2 style='text-align: center;'>{line[2:].strip()}</h2>", unsafe_allow_html=True)
        elif re.match(r'^\d+', line):
            st.markdown(f"### {line}")
            l_idx = 0
        else:
            # CARD NATIVO COM BORDA
            with st.container(border=True):
                c1, c2 = st.columns([0.1, 0.9])
                with c1: st.write(f"**{letras[l_idx%26]})**")
                with c2:
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

    # --- 7. PDF ---
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
        st.download_button("✅ Salvar PDF", pdf.output(dest='S').encode('latin-1'), "atividade.pdf")