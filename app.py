import streamlit as st
import random
import re
import os
import math
from fpdf import FPDF

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

# Inicialização de estados
for key in ['perfil', 'preview_questoes', 'res_calc']:
    if key not in st.session_state:
        st.session_state[key] = None if key == 'perfil' else ([] if key == 'preview_questoes' else "")

# --- 2. LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Login Quantum")
    pin = st.text_input("PIN:", type="password")
    if st.button("ACESSAR"):
        # Use o PIN que preferir aqui
        if pin == "123": 
            st.session_state.perfil = "admin"
            st.rerun()
        else:
            st.error("PIN INCORRETO!")
    st.stop()

# --- 3. SIDEBAR ---
st.sidebar.title(f"🚀 {st.session_state.perfil.upper()}")
menu = st.sidebar.selectbox("FERRAMENTA:", ["Início", "🔢 Operações", "📐 Equações", "𝑓(x) Bhaskara", "📄 Manual"])

usar_cabecalho = st.sidebar.checkbox("Usar cabeçalho.png", value=False) # Mudei para False por segurança
layout_cols = st.sidebar.selectbox("Colunas no PDF:", [1, 2, 3], index=1)

if st.sidebar.button("🧹 LIMPAR TUDO"):
    st.session_state.preview_questoes = []
    st.session_state.res_calc = ""
    st.rerun()

# --- 4. ÁREAS DE CONTEÚDO ---
st.title(f"🛠️ {menu}")

if menu == "🔢 Operações":
    tipo = st.radio("Escolha:", ["Soma", "Subtração", "Multiplicação", "Divisão"], horizontal=True)
    if st.button("GERAR LISTA"):
        s = {"Soma": "+", "Subtração": "-", "Multiplicação": "x", "Divisão": "/"}[tipo]
        st.session_state.preview_questoes = [f"t. Lista de {tipo}", "1. Calcule:"] + [f"{random.randint(10, 999)} {s} {random.randint(10, 99)} =" for _ in range(12)]

elif menu == "📐 Equações":
    if st.button("GERAR EQUAÇÕES"):
        st.session_state.preview_questoes = [f"t. Equações", "1. Resolva:"] + [f"{random.randint(2,9)}x + {random.randint(1,20)} = {random.randint(21,99)}" for _ in range(10)]

elif menu == "𝑓(x) Bhaskara":
    a = st.number_input("a", value=1.0); b = st.number_input("b", value=-5.0); c = st.number_input("c", value=6.0)
    if st.button("CALCULAR"):
        d = b**2 - 4*a*c
        if d >= 0: st.session_state.res_calc = f"Delta: {d} | x1: {(-b+math.sqrt(d))/(2*a):.2f}"
        else: st.session_state.res_calc = "Delta negativo!"

elif menu == "📄 Manual":
    txt = st.text_area("Questões:")
    if st.button("LANÇAR"): st.session_state.preview_questoes = txt.split("\n")

# --- 5. MOTOR PDF COM TRAVA DE SEGURANÇA ---
if st.session_state.res_calc: st.success(st.session_state.res_calc)

if st.session_state.preview_questoes:
    st.divider()
    st.subheader("👁️ Preview")
    for line in st.session_state.preview_questoes: st.write(line)

    # A função agora é chamada fora do botão para garantir que os dados existam
    def build_pdf():
        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.add_page()
        pdf.set_font("helvetica", size=11)
        
        y_pos = 50 if usar_cabecalho else 20
        if usar_cabecalho and os.path.exists("cabecalho.png"):
            pdf.image("cabecalho.png", x=10, y=10, w=190)
        
        pdf.set_y(y_pos)
        larg_col = 190 / layout_cols
        l_idx = 0
        
        for line in st.session_state.preview_questoes:
            # Encode seguro para evitar erro de caractere
            clean = line.strip().encode('latin-1', 'replace').decode('latin-1')
            if not clean: continue
            
            if clean.startswith("t."):
                pdf.ln(5); pdf.set_font("helvetica", style='B', size=14)
                pdf.cell(190, 10, clean[2:].strip(), ln=True, align='C')
                pdf.set_font("helvetica", size=11); l_idx = 0
            else:
                col_at = l_idx % layout_cols
                pdf.cell(larg_col, 8, f"- {clean}", ln=(col_at == layout_cols - 1))
                l_idx += 1
        return pdf.output() # fpdf2 retorna bytes

    # --- O CONSERTO ESTÁ AQUI ---
    # Geramos os bytes antes. Se der erro ou estiver vazio, o botão nem aparece.
    try:
        pdf_data = build_pdf()
        if pdf_data:
            st.download_button(
                label="📥 BAIXAR PDF A4",
                data=pdf_data,
                file_name="atividade.pdf",
                mime="application/pdf",
                key="btn_download_final"
            )
    except Exception as e:
        st.error(f"Erro ao preparar PDF: {e}")
