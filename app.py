import streamlit as st
import random
import re
import os
import math
from fpdf import FPDF

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

# Inicialização de estados
if 'perfil' not in st.session_state: st.session_state.perfil = None
if 'preview_questoes' not in st.session_state: st.session_state.preview_questoes = []
if 'res_calc' not in st.session_state: st.session_state.res_calc = ""

# --- 2. LOGIN RESTRITO ---
def validar_acesso(pin):
    try:
        p_aluno = str(st.secrets.get("acesso_aluno", "")).strip()
        p_prof = str(st.secrets.get("chave_mestra", "")).strip().lower()
        if pin == p_prof: return "admin"
        if pin == p_aluno: return "aluno"
    except: return None
    return None

if st.session_state.perfil is None:
    st.title("🔐 Login Quantum")
    pin_input = st.text_input("PIN:", type="password")
    if st.button("ACESSAR"):
        res = validar_acesso(pin_input)
        if res:
            st.session_state.perfil = res
            st.rerun()
        else: st.error("PIN INCORRETO!")
    st.stop()

# --- 3. BARRA LATERAL (MENU DE ESTRUTURA) ---
st.sidebar.title(f"🚀 {st.session_state.perfil.upper()}")

# SUBSTITUIÇÃO DOS CARDS POR SELECTBOX (NÃO FALHA)
menu = st.sidebar.selectbox(
    "SELECIONE A FERRAMENTA:",
    [
        "Início", 
        "🔢 Operações", 
        "📐 Equações", 
        "⛓️ Sistemas", 
        "⚖️ Álgebra", 
        "📄 Manual",
        "𝑓(x) Bhaskara", 
        "📊 PEMDAS", 
        "💰 Financeira"
    ]
)

st.sidebar.divider()
st.sidebar.subheader("⚙️ Configurações PDF")
usar_cabecalho = st.sidebar.checkbox("Usar cabeçalho.png", value=True)
recuo_cabecalho = st.sidebar.slider("Altura do Título (mm):", 20, 100, 45)
layout_cols = st.sidebar.selectbox("Colunas:", [1, 2, 3], index=1)

if st.sidebar.button("🧹 Limpar Tudo", use_container_width=True):
    st.session_state.preview_questoes = []
    st.session_state.res_calc = ""
    st.rerun()

if st.sidebar.button("🚪 Sair", use_container_width=True):
    st.session_state.clear()
    st.rerun()

# --- 4. ÁREAS DE TRABALHO ---
st.title(f"🛠️ {menu}")

if menu == "Início":
    st.write("Selecione uma ferramenta na barra lateral para começar.")

elif menu == "🔢 Operações":
    tipo = st.radio("Operação:", ["Soma", "Subtração", "Multiplicação", "Divisão"], horizontal=True)
    if st.button("Gerar Atividade"):
        s = {"Soma": "+", "Subtração": "-", "Multiplicação": "x", "Divisão": "÷"}[tipo]
        qs = [f"{random.randint(10, 999)} {s} {random.randint(10, 99)} =" for _ in range(12)]
        st.session_state.preview_questoes = [f"t. Atividade de {tipo}", "1. Resolva os cálculos:"] + qs

elif menu == "𝑓(x) Bhaskara":
    v1, v2, v3 = st.columns(3)
    a = v1.number_input("a", value=1.0)
    b = v2.number_input("b", value=-5.0)
    c = v3.number_input("c", value=6.0)
    if st.button("Calcular"):
        d = b**2 - 4*a*c
        if d >= 0:
            x1 = (-b + math.sqrt(d))/(2*a)
            x2 = (-b - math.sqrt(d))/(2*a)
            st.session_state.res_calc = f"Delta: {d} | x1: {x1:.2f} | x2: {x2:.2f}"
        else: st.session_state.res_calc = "Delta negativo."

# (AQUI VOCÊ PODE REPETIR A LÓGICA PARA EQ, SIS, ALG, MAN CONFORME O SEU CÓDIGO)

# --- 5. RESULTADOS E PDF ---
if st.session_state.res_calc:
    st.success(st.session_state.res_calc)

if st.session_state.preview_questoes:
    st.subheader("👁️ Preview A4")
    with st.container(border=True):
        for line in st.session_state.preview_questoes:
            st.write(line)

    def export_pdf():
        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.add_page()
        y_pos = 10
        if usar_cabecalho and os.path.exists("cabecalho.png"):
            pdf.image("cabecalho.png", 10, 10, 190)
            y_pos = recuo_cabecalho
        pdf.set_y(y_pos)
        
        larg_col = 190 / layout_cols
        l_idx = 0
        letras = "abcdefghijklmnopqrstuvwxyz"
        
        for line in st.session_state.preview_questoes:
            clean = line.strip().encode('latin-1', 'replace').decode('latin-1')
            if clean.startswith("t."):
                pdf.ln(5); pdf.set_font("Helvetica", 'B', 14)
                pdf.cell(190, 10, clean[2:].strip(), ln=True, align='C')
                pdf.set_font("Helvetica", size=11); l_idx = 0
            elif re.match(r'^\d+\.', clean):
                pdf.ln(5); pdf.set_font("Helvetica", 'B', 12)
                pdf.cell(190, 10, clean, ln=True); pdf.set_font("Helvetica", size=11); l_idx = 0
            else:
                col_at = l_idx % layout_cols
                pdf.cell(larg_col, 8, f"{letras[l_idx%26]}) {clean}", ln=(col_at == layout_cols - 1))
                l_idx += 1
        return pdf.output(dest='S').encode('latin-1')

    st.download_button("📥 Baixar PDF A4", data=export_pdf(), file_name="atividade.pdf", mime="application/pdf")
