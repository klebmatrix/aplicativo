import streamlit as st
import numpy as np
import os
import re
from fpdf import FPDF

# --- 1. CONFIGURAÇÕES ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

def clean_txt(text):
    rep = {"√": "V", "²": "^2", "³": "^3", "÷": "/", "×": "x", "{": ""}
    for o, n in rep.items(): text = text.replace(o, n)
    return str(text).encode('latin-1', 'replace').decode('latin-1')

if 'perfil' not in st.session_state: st.session_state.perfil = None
if 'preview_questoes' not in st.session_state: st.session_state.preview_questoes = []

# --- 2. LOGIN ---
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

# --- 3. MENU LATERAL ---
with st.sidebar:
    st.header("🚀 Menu")
    aba = st.radio("Escolha:", ["📄 Manual", "🔢 Operações", "📐 Equações"])
    if st.button("Sair"):
        st.session_state.perfil = None
        st.rerun()

# --- 4. TRATAMENTO MATEMÁTICO ---
def tratar_math(texto):
    t = re.sub(r'^[a-z][\)\.]\s*', '', texto)
    t = t.replace(', ', '').replace(',', '').strip()
    t = re.sub(r'(\d*)V(\d+)', r'\1\\sqrt{\2}', t)
    t = re.sub(r'(\^)(\d+)', r'\1{\2}', t)
    if "/" in t and "|" not in t: 
        t = re.sub(r'(\d+)/(\d+)', r'\\frac{\1}{\2}', t)
    return t

# --- 5. INTERFACE MANUAL ---
st.title(f"Módulo: {aba}")

if aba == "📄 Manual":
    # Exemplo de como usar o título com t.
    txt_input = st.text_area("Digite sua atividade:", height=250, 
                             value="t. AVALIAÇÃO DE MATEMÁTICA\n1. Calcule as raízes:\na) ,V36\nb) ,V49\n2. Resolva o sistema:\na) { 2x+y=20 | x-y=5")
    if st.button("🔍 Gerar Atividade"):
        st.session_state.preview_questoes = txt_input.split('\n')

# --- 6. VISUALIZAÇÃO (PREVIEW) ---
if st.session_state.preview_questoes:
    st.divider()
    
    # CABEÇALHO (Sempre aparece no topo se o arquivo existir)
    if os.path.exists("cabecalho.png"):
        st.image("cabecalho.png", use_container_width=True)
    else:
        st.warning("⚠️ Arquivo 'cabecalho.png' não encontrado no servidor.")

    letras = "abcdefghijklmnopqrstuvwxyz"
    l_idx = 0

    for q in st.session_state.preview_questoes:
        line = q.strip()
        if not line: continue
        
        # RECONHECIMENTO DE TÍTULO (t. ou TÍTULO:)
        if line.lower().startswith("t.") or line.lower().startswith("titulo:"):
            titulo_limpo = line.replace("t.", "").replace("titulo:", "").replace("TITULO:", "").strip()
            st.markdown(f"<h1 style='text-align: center; color: #007bff;'>{titulo_limpo}</h1>", unsafe_allow_html=True)
            st.divider()
        
        # Questões Numeradas
        elif re.match(r'^\d+', line):
            st.markdown(f"### {line}")
            l_idx = 0
            
        # Itens em Cards
        else:
            with st.container(border=True):
                col1, col2 = st.columns([0.1, 0.9])
                with col1:
                    st.write(f"**{letras[l_idx%26]})**")
                with col2:
                    if "{" in line or "|" in line:
                        cont = line.replace("{", "").strip()
                        if "|" in cont:
                            partes = cont.split("|")
                            st.latex(r" \begin{cases} " + partes[0].strip() + r" \\ " + partes[1].strip() + r" \end{cases} ")
                        else: st.write(line)
                    else:
                        f = tratar_math(line)
                        if "\\" in f or "{" in f: st.latex(f)
                        else: st.write(line.replace(',', ''))
            l_idx += 1

    # --- 7. PDF ---
    if st.button("📥 Baixar PDF"):
        pdf = FPDF()
        pdf.add_page()
        
        # Cabeçalho no PDF
        if os.path.exists("cabecalho.png"):
            pdf.image("cabecalho.png", x=10, y=8, w=190)
            pdf.set_y(50)
        else:
            pdf.set_y(20)
            
        pdf.set_font("Arial", size=12)
        l_idx = 0
        
        for q in st.session_state.preview_questoes:
            line = q.strip()
            if not line: continue
            
            # Título no PDF
            if line.lower().startswith("t.") or line.lower().startswith("titulo:"):
                titulo_limpo = line.replace("t.", "").replace("titulo:", "").replace("TITULO:", "").strip()
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(0, 10, clean_txt(titulo_limpo), ln=True, align='C')
                pdf.ln(5)
                pdf.set_font("Arial", size=12)
            
            elif re.match(r'^\d+', line):
                pdf.ln(5)
                pdf.set_font("Arial", 'B', 12)
                pdf.multi_cell(0, 8, clean_txt(line))
                pdf.set_font("Arial", size=12)
                l_idx = 0
            
            elif "{" in line and "|" in line:
                partes = line.replace("{", "").split("|")
                pdf.cell(10, 10, f"{letras[l_idx%26]})")
                cx, cy = pdf.get_x(), pdf.get_y()
                pdf.set_font("Courier", size=18); pdf.text(cx, cy + 7, "{"); pdf.set_font("Arial", size=12)
                pdf.text(cx + 5, cy + 4, clean_txt(partes[0].strip()))
                pdf.text(cx + 5, cy + 9, clean_txt(partes[1].strip()))
                pdf.ln(15)
                l_idx += 1
            else:
                item = re.sub(r'^[a-z][\)\.]\s*', '', line).replace(',', '')
                pdf.multi_cell(0, 8, f"{letras[l_idx%26]}) {clean_txt(item)}")
                l_idx += 1
                
        st.download_button("✅ Download Final", pdf.output(dest='S').encode('latin-1'), "atividade.pdf")