import streamlit as st
import math
import numpy as np
import os
import random
import re
from fpdf import FPDF

# --- 1. FUNÇÕES GLOBAIS ---
def tratar_texto_pdf(text):
    if not text: return ""
    return str(text).replace("√", "V").replace("²", "^2").replace("³", "^3")

def validar_acesso(pin_digitado):
    senha_aluno = str(st.secrets.get("acesso_aluno", "123456")).strip()
    senha_prof = str(st.secrets.get("chave_mestra", "chave_mestra")).strip().lower()
    if pin_digitado == senha_aluno: return "aluno"
    elif pin_digitado == senha_prof: return "admin"
    return "negado"

# --- 2. CONFIGURAÇÃO ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide", page_icon="🚀")

for key in ['perfil', 'sub_menu', 'preview_questoes']:
    if key not in st.session_state:
        st.session_state[key] = [] if key == 'preview_questoes' else None

# --- 3. LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Login")
    pin = st.text_input("PIN de Acesso:", type="password", max_chars=8)
    if st.button("Entrar"):
        acesso = validar_acesso(pin)
        if acesso != "negado":
            st.session_state.perfil = acesso
            st.rerun()
        else: st.error("PIN incorreto.")
    st.stop()

# --- 4. INTERFACE ---
st.sidebar.title(f"🚀 {'Professor' if st.session_state.perfil == 'admin' else 'Estudante'}")
layout_colunas = st.sidebar.selectbox("Colunas no PDF:", [1, 2, 3], index=1)
usar_cabecalho = st.sidebar.checkbox("Incluir Cabeçalho", value=True)

if st.sidebar.button("🧹 Limpar Tudo"):
    st.session_state.preview_questoes = []
    st.session_state.sub_menu = None
    st.rerun()

# --- 5. PAINEL ADMIN (5 GERADORES + 3 CÁLCULOS) ---
if st.session_state.perfil == "admin":
    st.title("🛠️ Painel de Controle")
    
    # LINHA 1: OS 5 GERADORES
    st.subheader("📝 Geradores de PDF")
    g1, g2, g3, g4, g5 = st.columns(5)
    with g1: 
        if st.button("🔢 Operações", use_container_width=True): st.session_state.sub_menu = "op"
    with g2: 
        if st.button("📐 Equações", use_container_width=True): st.session_state.sub_menu = "eq"
    with g3: 
        if st.button("📚 Colegial", use_container_width=True): st.session_state.sub_menu = "col"
    with g4: 
        if st.button("⚖️ Álgebra", use_container_width=True): st.session_state.sub_menu = "alg"
    with g5: 
        if st.button("📄 Manual", use_container_width=True): st.session_state.sub_menu = "man"

    # LINHA 2: OS 3 CÁLCULOS
    st.markdown("---")
    st.subheader("🧮 Ferramentas de Cálculo")
    c1, c2, c3 = st.columns(3)
    with c1: 
        if st.button("𝑓(x) Funções", use_container_width=True): st.session_state.sub_menu = "calc_f"
    with c2: 
        if st.button("📊 PEMDAS", use_container_width=True): st.session_state.sub_menu = "pemdas"
    with c3: 
        if st.button("💰 Financeira", use_container_width=True): st.session_state.sub_menu = "fin"

    menu = st.session_state.sub_menu
    st.divider()

    # Lógica simplificada para os geradores funcionarem
    if menu == "op":
        st.header("🔢 Gerador de Operações")
        num_ini = st.number_input("Questão inicial nº:", value=6)
        if st.button("Gerar Agora"):
            st.session_state.preview_questoes = [".M1", "t. OPERAÇÕES", f"{num_ini}. Calcule:"] + \
                [f"{random.randint(10,99)} + {random.randint(10,99)} =" for _ in range(10)]
            st.rerun()

    elif menu == "man":
        st.header("📄 Módulo Manual")
        txt = st.text_area("Insira: .M1, t. Título, 6. Pergunta, .Item")
        if st.button("Aplicar"):
            st.session_state.preview_questoes = txt.split('\n')
            st.rerun()

# --- 6. PDF ENGINE ---
if st.session_state.preview_questoes:
    st.subheader("👁️ Preview")
    for item in st.session_state.preview_questoes: st.text(item)

    def export_pdf():
        try:
            pdf = FPDF()
            pdf.add_page()
            y = 20
            if usar_cabecalho and os.path.exists("cabecalho.png"):
                pdf.image("cabecalho.png", 10, 10, 190)
                y = 65

            letras = "abcdefghijklmnopqrstuvwxyz"
            l_idx = 0
            n_cols = int(layout_colunas)
            largura_col = 190 / n_cols
            y_inicio_linha = y

            for line in st.session_state.preview_questoes:
                line = line.strip()
                if not line: continue
                
                mod_match = re.match(r'^\.M(\d+)', line, re.IGNORECASE)

                if line.lower().startswith("t."):
                    pdf.set_font("Helvetica", 'B', 14)
                    pdf.set_xy(10, y)
                    pdf.multi_cell(190, 10, tratar_texto_pdf(line[2:].strip()), align='C')
                    y, y_inicio_linha, l_idx = pdf.get_y()+2, pdf.get_y()+2, 0
                elif mod_match:
                    pdf.set_font("Helvetica", 'B', 12)
                    pdf.set_xy(10, y)
                    pdf.multi_cell(190, 8, f"M{mod_match.group(1)}", align='L')
                    y, y_inicio_linha, l_idx = pdf.get_y()+2, pdf.get_y()+2, 0
                elif re.match(r'^\d+\.', line):
                    pdf.set_font("Helvetica", size=12) # Normal
                    pdf.set_xy(10, y)
                    pdf.multi_cell(190, 8, tratar_texto_pdf(line), align='L')
                    y, y_inicio_linha, l_idx = pdf.get_y()+2, pdf.get_y()+2, 0
                else:
                    pdf.set_font("Helvetica", size=12)
                    col_at = l_idx % n_cols
                    if col_at == 0 and l_idx > 0: y_inicio_linha = pdf.get_y()
                    pdf.set_xy(10 + (col_at * largura_col), y_inicio_linha)
                    pdf.multi_cell(largura_col-5, 7, f"{letras[l_idx%26]}) {re.sub(r'^[.\s]+','',line)}", align='L')
                    l_idx += 1
            
            pdf_out = pdf.output(dest='S')
            return pdf_out.encode('latin-1') if isinstance(pdf_out, str) else pdf_out
        except: return b""

    st.download_button("📥 Baixar PDF", data=export_pdf(), file_name="atividade.pdf")