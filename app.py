import streamlit as st
import random
import re
import os
import math
from fpdf import FPDF

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

# Inicialização de estados
if 'autenticado' not in st.session_state: st.session_state.autenticado = False
if 'preview_questoes' not in st.session_state: st.session_state.preview_questoes = []
if 'res_calc' not in st.session_state: st.session_state.res_calc = ""

# --- 2. LOGIN (CHAVE MESTRA) ---
if not st.session_state.autenticado:
    st.title("🔐 Acesso Restrito")
    chave_mestra = str(st.secrets.get("chave_mestra", "")).strip().lower()
    pin_input = st.text_input("Chave Mestra:", type="password")
    if st.button("DESBLOQUEAR"):
        if pin_input.lower() == chave_mestra:
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("Incorreto!")
    st.stop()

# --- 3. MENU LATERAL ---
st.sidebar.title("🚀 QUANTUM LAB")
menu = st.sidebar.selectbox("FERRAMENTA:", ["Início", "🔢 Operações", "📐 Equações", "💰 Financeira", "📄 Manual"])

# Instrução Personalizada: Take Profit Infinito Ativo
st.sidebar.success("✅ Take Profit: INFINITO ATIVO")

st.sidebar.divider()
usar_cabecalho = st.sidebar.checkbox("Usar cabeçalho.png", value=False)
layout_cols = st.sidebar.selectbox("Colunas no PDF:", [1, 2, 3], index=1)

if st.sidebar.button("🧹 LIMPAR TUDO"):
    st.session_state.preview_questoes = []; st.session_state.res_calc = ""; st.rerun()

# --- 4. ÁREAS DE CONTEÚDO ---
st.title(f"🛠️ {menu}")

if menu == "🔢 Operações":
    tipo = st.radio("Escolha:", ["Soma", "Subtração", "Multiplicação", "Divisão"], horizontal=True)
    if st.button("GERAR LISTA"):
        s = {"Soma": "+", "Subtração": "-", "Multiplicação": "x", "Divisão": "/"}[tipo]
        st.session_state.preview_questoes = [f"t. Lista de {tipo}", "1. Calcule:"] + \
                                           [f"{random.randint(10, 999)} {s} {random.randint(10, 99)} =" for _ in range(12)]

elif menu == "💰 Financeira":
    # Lógica de Venda Automática (Take Profit)
    entrada = st.number_input("Entrada:", value=100.0)
    alvo = st.number_input("Alvo %:", value=10.0)
    if st.button("CALCULAR TP"):
        venda = entrada * (1 + (alvo/100))
        st.session_state.res_calc = f"Venda Automática: R$ {venda:.2f}"

elif menu == "📄 Manual":
    txt = st.text_area("Questões (uma por linha):")
    if st.button("LANÇAR"): st.session_state.preview_questoes = txt.split("\n")

# --- 5. MOTOR DE PDF (COM TRAVA DE SEGURANÇA) ---
if st.session_state.res_calc:
    st.success(st.session_state.res_calc)

# O BOTÃO DE DOWNLOAD SÓ APARECE SE EXISTIR CONTEÚDO NO PREVIEW
if st.session_state.preview_questoes:
    st.divider()
    st.subheader("👁️ Preview")
    for line in st.session_state.preview_questoes:
        if line.strip(): st.write(line)

    def gerar_pdf():
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        y_pos = 50 if usar_cabecalho else 20
        if usar_cabecalho and os.path.exists("cabecalho.png"):
            pdf.image("cabecalho.png", 10, 10, 190)
        
        pdf.set_y(y_pos)
        larg_col = 190 / layout_cols
        l_idx = 0
        letras = "abcdefghijklmnopqrstuvwxyz"

        for line in st.session_state.preview_questoes:
            clean = line.strip().encode('latin-1', 'replace').decode('latin-1')
            if not clean: continue
            
            if clean.startswith("t."):
                pdf.ln(5); pdf.set_font("Arial", 'B', 14)
                pdf.cell(190, 10, clean[2:].strip(), ln=True, align='C')
                pdf.set_font("Arial", size=12); l_idx = 0
            else:
                col_at = l_idx % layout_cols
                pdf.cell(larg_col, 8, f"{letras[l_idx%26]}) {clean}", ln=(col_at == layout_cols - 1))
                l_idx += 1
        return pdf.output()

    # ESSA É A LINHA QUE RESOLVE O ERRO:
    # A função gerar_pdf() só é chamada se o componente for montado após a geração das questões.
    pdf_final = gerar_pdf()
    
    st.download_button(
        label="📥 BAIXAR PDF", 
        data=pdf_final, 
        file_name="quantum_lab.pdf", 
        mime="application/pdf"
    )
else:
    st.info("Nenhuma questão gerada. Use as ferramentas acima para criar o conteúdo do PDF.")
