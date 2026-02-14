import streamlit as st
import random
import re
import os
from fpdf import FPDF
from io import BytesIO

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

if 'autenticado' not in st.session_state: st.session_state.autenticado = False
if 'preview_questoes' not in st.session_state: st.session_state.preview_questoes = []

# --- LOGIN ---
if not st.session_state.autenticado:
    st.title("🔐 Login")
    chave = str(st.secrets.get("chave_mestra", ""))
    pin = st.text_input("Chave Mestra:", type="password")
    if st.button("ENTRAR"):
        if pin == chave:
            st.session_state.autenticado = True
            st.rerun()
        else: st.error("Erro!")
    st.stop()

# --- SIDEBAR ---
st.sidebar.title("🚀 QUANTUM LAB")
menu = st.sidebar.selectbox("MENU:", ["🔢 Operações", "📄 Manual"])
layout_cols = st.sidebar.selectbox("Colunas:", [1, 2, 3], index=1)

if st.sidebar.button("🧹 LIMPAR"):
    st.session_state.preview_questoes = []
    st.rerun()

# --- LOGICA ---
st.title(f"🛠️ {menu}")

if menu == "🔢 Operações":
    tipo = st.radio("Escolha:", ["Soma", "Subtração", "Multiplicação", "Divisão"], horizontal=True)
    if st.button("GERAR LISTA"):
        s = {"Soma": "+", "Subtração": "-", "Multiplicação": "x", "Divisão": "/"}[tipo]
        st.session_state.preview_questoes = [f"t. Lista de {tipo}", "Calcule:"] + \
            [f"{random.randint(10, 999)} {s} {random.randint(10, 99)} =" for _ in range(12)]

# --- PREVIEW E PDF (O CONSERTO) ---
if st.session_state.preview_questoes:
    st.divider()
    for line in st.session_state.preview_questoes: st.write(line)

    def criar_pdf_bytes():
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        larg_col = 190 / layout_cols
        l_idx = 0
        letras = "abcdefghijklmnopqrstuvwxyz"

        for line in st.session_state.preview_questoes:
            clean = line.strip().encode('latin-1', 'replace').decode('latin-1')
            if clean.startswith("t."):
                pdf.ln(5); pdf.set_font("Arial", 'B', 14)
                pdf.cell(190, 10, clean[2:].strip(), ln=True, align='C')
                pdf.set_font("Arial", size=12); l_idx = 0
            else:
                col_at = l_idx % layout_cols
                pdf.cell(larg_col, 8, f"{letras[l_idx%26]}) {clean}", ln=(col_at == layout_cols - 1))
                l_idx += 1
        
        # TRANSFORMA EM BYTESIO PARA NÃO DAR ERRO DE UNSUPPORTED
        return BytesIO(pdf.output(dest='S').encode('latin-1'))

    # GERA O OBJETO DE BUFFER
    pdf_buffer = criar_pdf_bytes()

    st.download_button(
        label="📥 BAIXAR PDF",
        data=pdf_buffer.getvalue(), # PEGA O VALOR EM BYTES PURO
        file_name="quantum_lab.pdf",
        mime="application/pdf"
    )

