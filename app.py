import streamlit as st
import numpy as np
import random
import os
import re
from fpdf import FPDF

# --- 1. CONFIGURAÇÕES TÉCNICAS ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

def clean_txt(text):
    """Garante que o PDF não quebre"""
    rep = {"√": "V", "²": "^2", "³": "^3", "÷": "/", "×": "x", "{": ""}
    for o, n in rep.items():
        text = text.replace(o, n)
    return str(text).encode('latin-1', 'replace').decode('latin-1')

# Inicialização segura das variáveis
if 'perfil' not in st.session_state: st.session_state.perfil = None
if 'preview_questoes' not in st.session_state: st.session_state.preview_questoes = []

# --- 2. LOGIN (chave_mestra) ---
if st.session_state.perfil is None:
    st.title("🔐 Acesso ao Sistema")
    pin = st.text_input("Digite seu PIN:", type="password")
    if st.button("Entrar"):
        # Pega do Render ou usa padrão 'chave_mestra'
        s_prof = str(st.secrets.get("chave_mestra", "chave_mestra")).strip().lower()
        if pin == s_prof: 
            st.session_state.perfil = "admin"
            st.rerun()
        else:
            st.error("PIN incorreto. Tente novamente.")
    st.stop()

# --- 3. MENU LATERAL (BLINDADO) ---
with st.sidebar:
    st.title(f"🚀 {st.session_state.perfil.upper()}")
    aba = st.radio("Selecione o Módulo:", 
        ["🔢 Operações", "📐 Equações", "📚 Colegial", "⚖️ Álgebra Linear", "📄 Manual"])
    
    st.divider()
    if st.button("Sair do Sistema"):
        st.session_state.perfil = None
        st.rerun()

st.title(f"Módulo: {aba}")

# --- 4. PROCESSADOR DE SÍMBOLOS ---
def formatar_para_preview(texto):
    # Remove vírgulas iniciais e letras como a), b)
    t = re.sub(r'^[a-z][\)\.]\s*', '', texto)
    t = t.replace(', ', '').replace(',', '').strip()
    
    # Raiz (ex: 2V36 ou V25)
    t = re.sub(r'(\d*)V(\d+)', r'\1\\sqrt{\2}', t)
    # Potência (ex: 5^2)
    t = re.sub(r'(\^)(\d+)', r'\1{\2}', t)
    # Fração (ex: 3/4)
    if "/" in t and "|" not in t:
        t = re.sub(r'(\d+)/(\d+)', r'\\frac{\1}{\2}', t)
    return t

# --- 5. LÓGICA DO MANUAL ---
if aba == "📄 Manual":
    st.info("Digite como no exemplo: ,2V36 ou { 2x+y=20 | x-y=5")
    txt_input = st.text_area("Área de Digitação:", height=300, 
                             value="1. Calcule:\na) ,2V36 =\nb) ,5^2 + 10 =\nc) ,3/4 de 200 =\n2. Resolva o sistema:\na) { 2x + y = 20 | x - y = 5")
    if st.button("🔍 Visualizar Atividade"):
        st.session_state.preview_questoes = txt_input.split('\n')

# (Outros módulos mantidos de forma simples para evitar erro)
elif aba == "📚 Colegial":
    if st.button("Gerar Exemplos"):
        st.session_state.preview_questoes = ["1. Colegial:", "V144", "2^3", "10% de 500"]

# --- 6. ÁREA DE PREVIEW (VISUALIZAÇÃO) ---
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
            # Sistemas (chave {)
            elif "{" in line or "|" in line:
                conteudo = line.replace("{", "").strip()
                if "|" in conteudo:
                    partes = conteudo.split("|")
                    st.write(f"**{letras[l_idx%26]})**")
                    st.latex(r" \begin{cases} " + partes[0].strip() + r" \\ " + partes[1].strip() + r" \end{cases} ")
                    l_idx += 1
                else: st.write(f"{line}")
            # Números (Reset)
            elif re.match(r'^\d+', line):
                st.markdown(f"### {line}")
                l_idx = 0
            # Itens Matemáticos
            else:
                formato = formatar_para_preview(line)
                if "\\" in formato or "{" in formato:
                    st.write(f"**{letras[l_idx%26]})**")
                    st.latex(formato)
                else:
                    st.write(f"**{letras[l_idx%26]})** {line.replace(',', '')}")
                l_idx += 1

    # --- 7. GERAÇÃO DE PDF ---
    if st.button("📥 Baixar Atividade em PDF"):
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
        st.download_button("✅ Clique para Salvar", pdf.output(dest='S').encode('latin-1'), "atividade.pdf")