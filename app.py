import streamlit as st
import numpy as np
import random
import os
import re
from fpdf import FPDF

# --- CONFIGURAÇÕES ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

def clean_txt(text):
    """Limpa o texto para o PDF não dar erro de fonte"""
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

# --- LÓGICA MANUAL ---
if aba == "📄 Manual":
    st.subheader("📝 Módulo Manual")
    st.info("💡 Raiz: 3V27 (cúbica) | Expoente: 5^4 | Fração: 1/2 | Sistema: [SIS] x+y=5 | x-y=1")
    txt_input = st.text_area("Digite sua atividade:", height=250)
    if st.button("🔍 Gerar Visualização"):
        st.session_state.preview_questoes = txt_input.split('\n')

# --- OUTROS MÓDULOS (Simplificados) ---
elif aba == "📚 Colegial":
    if st.button("🎲 Gerar Exemplos"):
        st.session_state.preview_questoes = ["t. EXERCÍCIOS", "1. Calcule:", "3V27", "V144", "2^4", "1/5 + 2/5"]

# --- VISUALIZAÇÃO (PREVIEW) ---
if st.session_state.preview_questoes and aba != "🧮 Calculadoras":
    st.divider()
    letras = "abcdefghijklmnopqrstuvwxyz"; l_idx = 0
    
    with st.container(border=True):
        for q in st.session_state.preview_questoes:
            line = q.strip()
            if not line: continue
            
            # Títulos
            if line.startswith("t."):
                st.markdown(f"<h2 style='text-align: center;'>{line[2:].strip()}</h2>", unsafe_allow_html=True)
            
            # Sistemas
            elif "[SIS]" in line:
                partes = line.replace("[SIS]", "").split("|")
                st.write(f"**{letras[l_idx%26]})**")
                st.latex(r" \begin{cases} " + partes[0].strip() + r" \\ " + partes[1].strip() + r" \end{cases} ")
                l_idx += 1
            
            # Reset de letras com números
            elif re.match(r'^\d+', line):
                st.markdown(f"### {line}")
                l_idx = 0
            
            # Raízes, Potências e Frações (Lógica LaTeX)
            else:
                # Trata Raiz: 3V27 vira \sqrt[3]{27} | V25 vira \sqrt{25}
                d_line = re.sub(r'(\d+)V(\d+)', r'\\sqrt[\1]{\2}', line) # Raiz com índice
                d_line = re.sub(r'(?<!\[)V(\d+)', r'\\sqrt{\1}', d_line) # Raiz quadrada simples
                
                # Trata Expoente: 5^4 vira 5^{4}
                d_line = re.sub(r'(\^)(\d+)', r'\1{\2}', d_line)
                
                # Trata Fração: 1/2 vira \frac{1}{2}
                if "/" in d_line and not "[" in d_line:
                    f_parts = d_line.split("/")
                    if len(f_parts) == 2:
                        d_line = r"\frac{" + f_parts[0].strip() + "}{" + f_parts[1].strip() + "}"

                if "\\" in d_line or "{" in d_line:
                    st.write(f"**{letras[l_idx%26]})**")
                    st.latex(d_line)
                else:
                    st.write(f"**{letras[l_idx%26]})** {line}")
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
                pdf.multi_cell(0, 8, f"{letras[l_idx%26]}) {clean_txt(line)}")
                l_idx += 1
        st.download_button("✅ Download", pdf.output(dest='S').encode('latin-1'), "atividade.pdf")