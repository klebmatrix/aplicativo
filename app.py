import streamlit as st
import numpy as np
import random
import os
import re
from fpdf import FPDF

# --- 1. CONFIGURAÇÕES E LIMPEZA ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

def clean_txt(text):
    """Garante que o PDF não trave com símbolos especiais"""
    rep = {"√": "V", "²": "^2", "³": "^3", "÷": "/", "×": "x"}
    for o, n in rep.items():
        text = text.replace(o, n)
    return str(text).encode('latin-1', 'replace').decode('latin-1')

if 'perfil' not in st.session_state: st.session_state.perfil = None
if 'preview_questoes' not in st.session_state: st.session_state.preview_questoes = []

# --- 2. LOGIN (chave_mestra) ---
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

# --- 3. MENU LATERAL ---
st.sidebar.title(f"🚀 {st.session_state.perfil.upper()}")
aba = st.sidebar.radio("Módulos:", ["🔢 Operações", "📐 Equações", "📚 Colegial", "⚖️ Álgebra Linear", "📄 Manual", "🧮 Calculadoras"])

# --- 4. LÓGICA DO MANUAL (Aprimorada) ---
if aba == "📄 Manual":
    st.subheader("📝 Criar Atividade Manual")
    st.info("💡 Use: V para Raiz | ^ para Potência | / para Fração | [SIS] eq1 | eq2 para Sistema")
    txt_input = st.text_area("Digite sua atividade aqui:", height=300, placeholder="t. TÍTULO\n1. Resolva:\nV25\n5^2\n1/2 + 1/4\n[SIS] x+y=5 | x-y=1")
    if st.button("🔍 Gerar Visualização"):
        st.session_state.preview_questoes = txt_input.split('\n')

# --- MÓDULOS AUTOMÁTICOS (Resumidos para estabilidade) ---
elif aba == "📚 Colegial":
    if st.button("🎲 Gerar Exemplos Colegial"):
        st.session_state.preview_questoes = ["t. EXERCÍCIOS","1. Calcule:","V144","2^3","3/4 + 1/2","20% de 500"]
elif aba == "⚖️ Álgebra Linear":
    if st.button("🎲 Gerar Sistema"):
        st.session_state.preview_questoes = ["1. Resolva o sistema:","[SIS] x + y = 10 | x - y = 4"]

# --- 5. VISUALIZAÇÃO (PREVIEW) - ONDE A MÁGICA ACONTECE ---
if st.session_state.preview_questoes and aba != "🧮 Calculadoras":
    st.divider()
    st.subheader("👀 Preview da Atividade")
    letras = "abcdefghijklmnopqrstuvwxyz"; l_idx = 0
    
    # Cabeçalho da Atividade
    if os.path.exists("cabecalho.png"):
        st.image("cabecalho.png")

    with st.container(border=True):
        for q in st.session_state.preview_questoes:
            line = q.strip()
            if not line: continue
            
            # 1. Tratar Títulos
            if line.startswith("t."):
                st.markdown(f"<h2 style='text-align: center;'>{line[2:].strip()}</h2>", unsafe_allow_html=True)
            
            # 2. Tratar Sistemas
            elif "[SIS]" in line:
                partes = line.replace("[SIS]", "").split("|")
                st.write(f"**{letras[l_idx%26]})**")
                st.latex(r" \begin{cases} " + partes[0].strip() + r" \\ " + partes[1].strip() + r" \end{cases} ")
                l_idx += 1
            
            # 3. Tratar Números (Reset de letras)
            elif re.match(r'^\d+', line):
                st.markdown(f"### {line}")
                l_idx = 0
            
            # 4. Tratar Itens (Raiz, Potência, Fração)
            else:
                # Converter texto para LaTeX bonito no Preview
                d_line = line.replace("V", r"\sqrt").replace("^", "^{").strip()
                if "^{" in d_line: d_line += "}" # Fecha a chave da potência
                
                # Se tiver fração ou raiz, usa LaTeX, senão texto comum
                if "sqrt" in d_line or "/" in d_line or "^{" in d_line:
                    st.write(f"**{letras[l_idx%26]})**")
                    st.latex(d_line.replace("/", r"\over "))
                else:
                    st.write(f"**{letras[l_idx%26]})** {line}")
                l_idx += 1

    # --- 6. BOTÃO DE PDF ---
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
                pdf.multi_cell(0, 8, f"{letras[l_idx%26]}) {clean_txt(line)}")
                l_idx += 1
        st.download_button("✅ Download Atividade", pdf.output(dest='S').encode('latin-1'), "atividade.pdf")