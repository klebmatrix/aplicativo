import streamlit as st
import numpy as np
import random
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
if 'titulo_atividade' not in st.session_state: st.session_state.titulo_atividade = "ATIVIDADE QUANTUM"

# --- 2. MOTOR DE RENDERIZAÇÃO DE CARDS (UNIFICADO) ---
def renderizar_atividade(questoes, titulo):
    st.divider()
    # Header Image sempre no topo
    if os.path.exists("cabecalho.png"):
        st.image("cabecalho.png", use_container_width=True)
    
    st.markdown(f"<h1 style='text-align: center;'>{titulo}</h1>", unsafe_allow_html=True)
    
    letras = "abcdefghijklmnopqrstuvwxyz"
    l_idx = 0
    
    for q in questoes:
        line = str(q).strip()
        if not line: continue
        
        # Se começar com número: Título da questão e RESETA as letras
        if re.match(r'^\d+', line):
            st.markdown(f"### {line}")
            l_idx = 0
        else:
            # CARD PARA QUALQUER ITEM
            with st.container(border=True):
                col1, col2 = st.columns([0.05, 0.95])
                with col1:
                    st.write(f"**{letras[l_idx%26]})**")
                with col2:
                    # Se for sistema de equações
                    if "{" in line or "|" in line:
                        p = line.replace("{", "").split("|")
                        if len(p) > 1:
                            st.latex(r" \begin{cases} " + p[0].strip() + r" \\ " + p[1].strip() + r" \end{cases} ")
                        else: st.write(line)
                    # Se for matemática (Raiz, Potência)
                    elif any(c in line for c in ["V", "^", "/"]):
                        clean_line = line.lstrip(',')
                        # Formatação básica de LaTeX
                        f = clean_line.replace("V", "\\sqrt{") + "}" if "V" in clean_line else clean_line
                        st.latex(f.replace("^", "^{") + "}" if "^" in f else f)
                    else:
                        st.write(line.lstrip(','))
                l_idx += 1

# --- 3. LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Login")
    pin = st.text_input("PIN:", type="password")
    if st.button("Entrar"):
        try: chave = str(st.secrets.get("chave_mestra", "chave_mestra")).strip().lower()
        except: chave = "chave_mestra"
        if pin == chave: 
            st.session_state.perfil = "admin"
            st.rerun()
        else: st.error("PIN incorreto.")
    st.stop()

# --- 4. MENU LATERAL ---
with st.sidebar:
    st.header("🚀 Módulos")
    aba = st.radio("Escolha:", ["🔢 Operações", "📐 Equações", "📚 Colegial", "📄 Manual"])
    if st.button("Sair"):
        st.session_state.perfil = None
        st.rerun()

# --- 5. LÓGICA DOS MÓDULOS ---
st.title(f"Módulo: {aba}")

if aba == "🔢 Operações":
    qtd = st.slider("Quantidade:", 1, 20, 10)
    if st.button("Gerar Operações"):
        st.session_state.titulo_atividade = "OPERAÇÕES BÁSICAS"
        st.session_state.preview_questoes = ["1. Efetue os cálculos abaixo:"] + [f"{random.randint(10,99)} + {random.randint(10,99)}" for _ in range(qtd)]

elif aba == "📐 Equações":
    if st.button("Gerar Equações"):
        st.session_state.titulo_atividade = "EQUAÇÕES DE 1º GRAU"
        st.session_state.preview_questoes = ["1. Resolva as equações:"] + [f"{random.randint(2,9)}x + {random.randint(1,20)} = {random.randint(21,99)}" for _ in range(5)]

elif aba == "📄 Manual":
    txt_m = st.text_area("Digite sua atividade:", value="1. Questão Manual:\n,2V36\n,5^2")
    if st.button("Gerar Manual"):
        st.session_state.titulo_atividade = "ATIVIDADE MANUAL"
        st.session_state.preview_questoes = txt_m.split('\n')

# --- 6. EXECUÇÃO DO PREVIEW (TODOS OS CARDS) ---
if st.session_state.preview_questoes:
    renderizar_atividade(st.session_state.preview_questoes, st.session_state.titulo_atividade)

    # --- 7. PDF ---
    if st.button("📥 Baixar PDF"):
        pdf = FPDF(); pdf.add_page()
        if os.path.exists("cabecalho.png"): pdf.image("cabecalho.png", x=10, y=8, w=190); pdf.set_y(50)
        pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, clean_txt(st.session_state.titulo_atividade), ln=True, align='C')
        pdf.set_font("Arial", size=11); letras = "abcdefghijklmnopqrstuvwxyz"; l_idx = 0
        for q in st.session_state.preview_questoes:
            line = str(q).strip()
            if not line: continue
            if re.match(r'^\d+', line):
                pdf.ln(5); pdf.set_font("Arial", 'B', 11); pdf.multi_cell(0, 8, clean_txt(line)); pdf.set_font("Arial", size=11); l_idx = 0
            else:
                pdf.multi_cell(0, 8, f"{letras[l_idx%26]}) {clean_txt(line.lstrip(','))}"); l_idx += 1
        st.download_button("✅ Download PDF", pdf.output(dest='S').encode('latin-1'), "atividade.pdf")