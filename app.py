import streamlit as st
import random
import re
import os
import math
from fpdf import FPDF
from io import BytesIO  # Importação necessária para lidar com memória

# --- 1. CONFIGURAÇÃO E PERSISTÊNCIA ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

# Inicializa estados se não existirem
for key in ['perfil', 'sub_menu', 'preview_questoes', 'res_calc']:
    if key not in st.session_state:
        st.session_state[key] = [] if key == 'preview_questoes' else None if key == 'perfil' else ""

# --- 2. LOGIN (Secrets Render) ---
def validar_acesso(pin):
    p_aluno = str(st.secrets.get("acesso_aluno", "123456")).strip()
    p_prof = str(st.secrets.get("chave_mestra", "chave_mestra")).strip().lower()
    return "admin" if pin == p_prof else "aluno" if pin == p_aluno else None

if st.session_state.perfil is None:
    st.title("🔐 Login")
    pin_input = st.text_input("PIN:", type="password")
    if st.button("Acessar"):
        res = validar_acesso(pin_input)
        if res: 
            st.session_state.perfil = res
            st.rerun()
        else: 
            st.error("PIN Incorreto")
    st.stop()

# --- 3. SIDEBAR (CONFIGURAÇÕES E LOGOUT) ---
st.sidebar.title(f"🚀 {st.session_state.perfil.upper()}")
usar_cabecalho = st.sidebar.checkbox("Usar cabecalho.png", value=True)
recuo_cabecalho = st.sidebar.slider("Altura do Título:", 20, 80, 45)
layout_cols = st.sidebar.selectbox("Colunas PDF:", [1, 2, 3], index=1)

st.sidebar.divider()
if st.sidebar.button("🧹 Limpar Atividade", use_container_width=True):
    st.session_state.preview_questoes = []
    st.session_state.res_calc = ""
    st.rerun()

if st.sidebar.button("🚪 Sair / Logout", use_container_width=True):
    st.session_state.clear()
    st.rerun()

# --- 4. CENTRO DE COMANDO ---
st.title("🛠️ Centro de Comando Quantum")
g1, g2, g3, g4, g5 = st.columns(5)
if g1.button("🔢 Operações", use_container_width=True): st.session_state.sub_menu = "op"
if g2.button("📐 Equações", use_container_width=True): st.session_state.sub_menu = "eq"
if g3.button("⛓️ Sistemas", use_container_width=True): st.session_state.sub_menu = "sis"
if g4.button("⚖️ Álgebra", use_container_width=True): st.session_state.sub_menu = "alg"
if g5.button("📄 Manual", use_container_width=True): st.session_state.sub_menu = "man"

c1, c2, c3 = st.columns(3)
if c1.button("𝑓(x) Bhaskara", use_container_width=True): st.session_state.sub_menu = "calc_f"
if c2.button("📊 PEMDAS", use_container_width=True): st.session_state.sub_menu = "pemdas"
if c3.button("💰 Financeira", use_container_width=True): st.session_state.sub_menu = "fin"

st.divider()
menu = st.session_state.sub_menu

# --- 5. LÓGICAS DOS GERADORES (Simplificado para o exemplo) ---
if menu == "op":
    tipo = st.radio("Escolha:", ["Soma", "Subtração", "Multiplicação", "Divisão"], horizontal=True)
    if st.button("Gerar Atividade"):
        s = {"Soma": "+", "Subtração": "-", "Multiplicação": "x", "Divisão": "÷"}[tipo]
        qs = [f"{random.randint(10, 999)} {s} {random.randint(10, 99)} =" for _ in range(12)]
        st.session_state.preview_questoes = [".M1", f"t. Atividade de {tipo}", "1. Calcule:"] + qs
# (Outras lógicas mantidas conforme seu original...)

# --- 7. MOTOR PDF (VERSÃO FINAL CORRIGIDA) ---
    def export_pdf():
        pdf = FPDF()
        pdf.add_page()
        y_ini = 10
        if usar_cabecalho and os.path.exists("cabecalho.png"):
            pdf.image("cabecalho.png", 10, 10, 190)
            y_ini = recuo_cabecalho 
        
        pdf.set_y(y_ini)
        letras = "abcdefghijklmnopqrstuvwxyz"
        l_idx = 0
        larg_col = 190 / int(layout_cols)
        
        for line in st.session_state.preview_questoes:
            line = line.strip()
            if not line: continue
            
            if line.startswith(".M"):
                pdf.set_font("Helvetica", size=12)
                pdf.cell(190, 10, line[1:], ln=True)
            elif line.lower().startswith("t."):
                pdf.set_font("Helvetica", 'B', 14)
                pdf.cell(190, 10, line[2:].strip(), ln=True, align='C')
            elif re.match(r'^\d+\.', line):
                pdf.set_font("Helvetica", size=12)
                pdf.cell(190, 10, line, ln=True)
                l_idx = 0
            else:
                pdf.set_font("Helvetica", size=12)
                col = l_idx % int(layout_cols)
                txt = f"{letras[l_idx%26]}) {line.lstrip('. ')}"
                pdf.cell(larg_col, 8, txt, ln=(col == int(layout_cols)-1))
                l_idx += 1
        
        # O fpdf2 retorna um bytearray. O Streamlit quer bytes puros.
        return bytes(pdf.output())

    # Processamento e Botão
    try:
        pdf_output = export_pdf()
        
        st.download_button(
            label="📥 Baixar PDF",
            data=pdf_output,
            file_name="atividade.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.error(f"Erro ao processar binários: {e}")
