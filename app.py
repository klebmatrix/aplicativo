import streamlit as st
import numpy as np
import random
import os
import re
from fpdf import FPDF

# --- 1. CONFIGURAÇÕES E UTILITÁRIOS ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide", page_icon="🚀")

def clean_txt(text):
    """Limpa caracteres especiais para o PDF (latin-1)."""
    rep = {"√": "V", "²": "^2", "³": "^3", "÷": "/", "×": "x", "{": ""}
    for o, n in rep.items(): text = text.replace(o, n)
    return str(text).encode('latin-1', 'replace').decode('latin-1')

def tratar_math(texto):
    """Prepara o texto para exibição em LaTeX no Streamlit."""
    t = texto.lstrip(',').strip()
    # Converte V36 para \sqrt{36} e ^2 para ^{2}
    t = re.sub(r'V(\d+)', r'\\sqrt{\1}', t)
    t = re.sub(r'\^(\d+)', r'^{\1}', t)
    return t

# --- 2. LOGIN E ACESSO ---
if 'perfil' not in st.session_state: st.session_state.perfil = None
if 'preview_questoes' not in st.session_state: st.session_state.preview_questoes = []

if st.session_state.perfil is None:
    st.title("🔐 Acesso Restrito")
    pin = st.text_input("PIN de Acesso:", type="password")
    if st.button("Entrar"):
        try:
            # Busca chave_mestra das variáveis de ambiente do Render
            chave = str(st.secrets.get("chave_mestra", "12345678")).strip().lower()
        except: chave = "12345678"
        
        if pin == chave:
            st.session_state.perfil = "admin"
            st.rerun()
        else: st.error("PIN incorreto.")
    st.stop()

# --- 3. INTERFACE PRINCIPAL ---
st.sidebar.title("🚀 Menu Professor")
aba = st.sidebar.radio("Atividades:", ["📄 Manual", "🔢 Operações", "📐 Equações"])

if st.sidebar.button("Sair"):
    st.session_state.perfil = None
    st.rerun()

st.title(f"Módulo: {aba}")

# --- 4. COLETA DE DADOS ---
if aba == "📄 Manual":
    txt_input = st.text_area("Digite sua atividade:", height=250, 
                             value="t. AVALIAÇÃO DE MATEMÁTICA\n1. Calcule as raízes:\n,V36\n,V49\n2. Resolva as potências:\n,5^2\n,10^3")
    if st.button("🔍 Gerar Atividade"):
        st.session_state.preview_questoes = txt_input.split('\n')

elif aba == "🔢 Operações":
    qtd = st.slider("Quantidade:", 4, 20, 10)
    if st.button("Gerar Aleatório"):
        st.session_state.preview_questoes = ["t. EXERCÍCIOS DE OPERAÇÕES", "1. Efetue as somas:"] + [f"{random.randint(10,99)} + {random.randint(10,99)} =" for _ in range(qtd)]

# --- 5. MOTOR DE RENDERIZAÇÃO (CARDS + REGRAS) ---
if st.session_state.preview_questoes:
    st.divider()
    
    # Header Image sempre no topo
    if os.path.exists("cabecalho.png"):
        st.image("cabecalho.png", use_container_width=True)
    
    letras = "abcdefghijklmnopqrstuvwxyz"
    l_idx = 0

    for q in st.session_state.preview_questoes:
        line = q.strip()
        if not line: continue
        
        # A) RECONHECIMENTO DE TÍTULO (t. ou titulo:)
        if line.lower().startswith(("t.", "titulo:", "título:")):
            titulo = re.sub(r'^(t\.|titulo:|título:)\s*', '', line, flags=re.IGNORECASE)
            st.markdown(f"<h1 style='text-align: center; color: #1E88E5;'>{titulo}</h1>", unsafe_allow_html=True)
            st.divider()
            continue

        # B) QUESTÕES NUMERADAS (Ex: 1., 2.) - Reseta Letras
        elif re.match(r'^\d+', line):
            st.markdown(f"### {line}")
            l_idx = 0 
            
        # C) ITENS EM CARDS (Regra da letra posterior)
        else:
            with st.container(border=True):
                c1, c2 = st.columns([0.05, 0.95])
                with c1:
                    st.write(f"**{letras[l_idx%26]})**")
                with c2:
                    if "{" in line or "|" in line:
                        cont = line.replace("{", "").strip()
                        p = cont.split("|") if "|" in cont else [cont]
                        if len(p) > 1: st.latex(r" \begin{cases} " + p[0] + r" \\ " + p[1] + r" \end{cases} ")
                        else: st.write(line)
                    else:
                        f = tratar_math(line)
                        if "\\" in f or "^" in f: st.latex(f)
                        else: st.write(line.lstrip(','))
            l_idx += 1

    # --- 6. EXPORTAÇÃO PDF ---
    if st.button("📥 Baixar PDF"):
        pdf = FPDF()
        pdf.add_page()
        
        if os.path.exists("cabecalho.png"):
            pdf.image("cabecalho.png", x=10, y=8, w=190)
            pdf.set_y(50)
        else: pdf.set_y(20)
            
        l_idx = 0
        for q in st.session_state.preview_questoes:
            line = q.strip()
            if not line: continue
            
            if line.lower().startswith(("t.", "titulo:", "título:")):
                t_pdf = re.sub(r'^(t\.|titulo:|título:)\s*', '', line, flags=re.IGNORECASE)
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(0, 10, clean_txt(t_pdf), ln=True, align='C')
                pdf.ln(5); pdf.set_font("Arial", size=11)
            
            elif re.match(r'^\d+', line):
                pdf.ln(5); pdf.set_font("Arial", 'B', 12)
                pdf.multi_cell(0, 8, clean_txt(line))
                pdf.set_font("Arial", size=11); l_idx = 0
            
            else:
                pdf.multi_cell(0, 8, f"{letras[l_idx%26]}) {clean_txt(line.lstrip(','))}")
                l_idx += 1
                
        st.download_button("✅ Download Final", pdf.output(dest='S').encode('latin-1'), "atividade.pdf")