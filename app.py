import streamlit as st
import numpy as np
import random
import os
import re
from fpdf import FPDF

# --- CONFIGURAÇÕES ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

def clean_txt(text):
    return str(text).encode('latin-1', 'replace').decode('latin-1')

if 'perfil' not in st.session_state: st.session_state.perfil = None
if 'menu_ativo' not in st.session_state: st.session_state.menu_ativo = "🔢 Operações"
if 'preview_questoes' not in st.session_state: st.session_state.preview_questoes = []

# --- LOGIN (chave_mestra em minúsculo) ---
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

# --- MENU LATERAL ---
st.sidebar.title(f"🚀 {st.session_state.perfil.upper()}")
st.session_state.menu_ativo = st.sidebar.radio("Módulos:", 
    ["🔢 Operações", "📐 Equações", "📚 Colegial", "⚖️ Álgebra Linear", "📄 Manual", "🧮 Calculadoras"])

menu = st.session_state.menu_ativo
st.title(f"Módulo: {menu}")

# --- LÓGICA DE ÁLGEBRA LINEAR (Sistemas com Formatação Especial) ---
if menu == "⚖️ Álgebra Linear":
    sub = st.radio("Escolha:", ["Sistemas", "Matrizes", "Funções"], horizontal=True)
    if sub == "Sistemas":
        if st.button("🎲 Gerar Sistemas"):
            qs = []
            for _ in range(3):
                x, y = random.randint(1,5), random.randint(1,5)
                # Usamos um marcador [SIS] para o PDF saber que deve desenhar a chave
                qs.append(f"[SIS] x + y = {x+y} | x - y = {x-y}")
            st.session_state.preview_questoes = qs
    # ... (outros sub-módulos mantidos)

# --- MÓDULO MANUAL ---
elif menu == "📄 Manual":
    st.info("Para sistema, use: [SIS] eq1 | eq2")
    txt = st.text_area("Conteúdo:", height=200)
    if st.button("🔍 Visualizar"): st.session_state.preview_questoes = txt.split('\n')

# --- PREVIEW E GERAÇÃO DE PDF COM CHAVE ---
if st.session_state.preview_questoes and menu != "🧮 Calculadoras":
    st.divider()
    letras = "abcdefghijklmnopqrstuvwxyz"; l_idx = 0
    
    with st.container(border=True):
        for q in st.session_state.preview_questoes:
            line = q.strip()
            if not line: continue
            if "[SIS]" in line:
                partes = line.replace("[SIS]", "").split("|")
                st.write(f"**{letras[l_idx%26]})**")
                st.latex(r" \begin{cases} " + partes[0].strip() + r" \\ " + partes[1].strip() + r" \end{cases} ")
                l_idx += 1
            elif line.startswith("t."): st.markdown(f"### {line[2:].strip()}")
            elif re.match(r'^\d+', line): st.markdown(f"**{line}**"); l_idx = 0
            else:
                st.write(f"**{letras[l_idx%26]})** {line.replace('.', '').strip()}")
                l_idx += 1

    if st.button("📥 Baixar PDF"):
        pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=10); l_idx = 0
        if os.path.exists("cabecalho.png"): pdf.image("cabecalho.png", x=12.5, y=8, w=185); pdf.set_y(46)
        
        for q in st.session_state.preview_questoes:
            line = q.strip()
            if not line: continue
            
            if "[SIS]" in line: # LÓGICA DA CHAVE NO PDF
                partes = line.replace("[SIS]", "").split("|")
                pdf.set_font("Arial", 'B', 10)
                pdf.cell(10, 10, f"{letras[l_idx%26]})")
                curr_x, curr_y = pdf.get_x(), pdf.get_y()
                
                # Desenha a chave e as equações
                pdf.set_font("Courier", size=20) # Fonte para a chave parecer grande
                pdf.text(curr_x, curr_y + 7, "{")
                pdf.set_font("Arial", size=10)
                pdf.text(curr_x + 5, curr_y + 4, clean_txt(partes[0].strip()))
                pdf.text(curr_x + 5, curr_y + 9, clean_txt(partes[1].strip()))
                pdf.ln(12)
                l_idx += 1
            elif line.startswith("t."):
                pdf.ln(5); pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, clean_txt(line[2:].strip()), ln=True, align='C'); pdf.set_font("Arial", size=10)
            elif re.match(r'^\d+', line):
                pdf.ln(4); pdf.set_font("Arial", 'B', 11); pdf.multi_cell(0, 8, clean_txt(line)); pdf.set_font("Arial", size=10); l_idx = 0
            else:
                pdf.multi_cell(0, 8, f"{letras[l_idx%26]}) {clean_txt(line.replace('.',''))}"); l_idx += 1
        
        st.download_button("✅ Download", pdf.output(dest='S').encode('latin-1', 'replace'), "atividade.pdf")