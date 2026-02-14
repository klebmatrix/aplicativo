import streamlit as st
import random
import re
import os
from fpdf import FPDF

# --- 1. MEMÓRIA DO APP (O que impede de reduzir/sumir) ---
if 'autenticado' not in st.session_state: st.session_state.autenticado = False
if 'questoes' not in st.session_state: st.session_state.questoes = []
if 'titulo' not in st.session_state: st.session_state.titulo = "Atividade Quantum"

# --- 2. LOGIN COM CHAVE MESTRA ---
if not st.session_state.autenticado:
    st.title("🔐 Quantum Lab - Bloqueado")
    chave = str(st.secrets.get("chave_mestra", ""))
    pin = st.text_input("Chave Mestra:", type="password")
    if st.button("DESBLOQUEAR"):
        if pin == chave:
            st.session_state.autenticado = True
            st.rerun()
        else: st.error("Chave incorreta!")
    st.stop()

# --- 3. MENU LATERAL ---
st.sidebar.title("🚀 CONFIGURAÇÕES")
menu = st.sidebar.selectbox("FERRAMENTA:", ["Soma", "Subtração", "Multiplicação", "Manual"])
cols = st.sidebar.selectbox("Colunas no PDF:", [1, 2, 3], index=1)

if st.sidebar.button("🧹 LIMPAR TUDO"):
    st.session_state.questoes = []
    st.rerun()

# --- 4. LÓGICA DE GERAÇÃO ---
st.title(f"🛠️ Gerador: {menu}")

if menu != "Manual":
    if st.button(f"GERAR NOVAS QUESTÕES DE {menu.upper()}"):
        sinal = {"Soma": "+", "Subtração": "-", "Multiplicação": "x"}[menu]
        # Salva na memória para não sumir depois
        st.session_state.questoes = [f"{random.randint(10, 999)} {sinal} {random.randint(10, 99)} =" for _ in range(12)]
        st.session_state.titulo = f"Lista de {menu}"

elif menu == "Manual":
    txt = st.text_area("Cole suas questões aqui:")
    if st.button("SALVAR QUESTÕES"):
        st.session_state.questoes = txt.split("\n")
        st.session_state.titulo = "Atividade Manual"

# --- 5. EXIBIÇÃO E PDF (SÓ APARECE SE TIVER DADOS) ---
if st.session_state.questoes:
    st.divider()
    st.subheader(f"👁️ Preview: {st.session_state.titulo}")
    
    # Exibe as questões que estão na memória
    for q in st.session_state.questoes:
        if q.strip(): st.write(q)

    def criar_pdf():
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(190, 10, st.session_state.titulo, ln=True, align='C')
        pdf.ln(10)
        pdf.set_font("Arial", size=12)
        
        larg_col = 190 / cols
        for i, q in enumerate(st.session_state.questoes):
            clean = q.strip().encode('latin-1', 'replace').decode('latin-1')
            proxima_linha = (i + 1) % cols == 0
            pdf.cell(larg_col, 10, f"{i+1}) {clean}", ln=proxima_linha)
        
        # O output direto resolve o erro de AttributeError se usar fpdf2
        return pdf.output()

    # TRAVA DE SEGURANÇA PARA O DOWNLOAD_BUTTON
    try:
        pdf_bytes = criar_pdf()
        st.download_button(
            label="📥 BAIXAR PDF AGORA",
            data=pdf_bytes,
            file_name="quantum_lab.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.error(f"Erro ao gerar: {e}")
