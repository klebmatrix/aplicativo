import streamlit as st
import random
import re
import os
import math
from fpdf import FPDF
from io import BytesIO # IMPORTANTE: Isso resolve o erro de suporte

# --- 1. PERSISTÊNCIA E CONFIGURAÇÃO ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

if 'autenticado' not in st.session_state: st.session_state.autenticado = False
if 'preview_questoes' not in st.session_state: st.session_state.preview_questoes = []
if 'res_calc' not in st.session_state: st.session_state.res_calc = ""

# --- 2. LOGIN (CHAVE MESTRA) ---
if not st.session_state.autenticado:
    st.title("🔐 Quantum Suite - Acesso")
    chave_mestra = str(st.secrets.get("chave_mestra", "")).strip().lower()
    pin = st.text_input("Chave Mestra:", type="password")
    if st.button("DESBLOQUEAR"):
        if pin.lower() == chave_mestra:
            st.session_state.autenticado = True
            st.rerun()
        else: st.error("Chave Inválida.")
    st.stop()

# --- 3. MENU LATERAL ---
st.sidebar.title("🚀 QUANTUM SUITE")
menu = st.sidebar.selectbox(
    "FERRAMENTA:",
    ["Início", "🔢 Operações", "📐 Equações", "⛓️ Sistemas", "𝑓(x) Bhaskara", "💰 Financeira (Take Profit)", "📄 Manual"]
)

st.sidebar.divider()
st.sidebar.success("✅ Take Profit: INFINITO ATIVO")
st.sidebar.divider()

usar_cabecalho = st.sidebar.checkbox("Usar cabeçalho.png", value=False)
layout_cols = st.sidebar.selectbox("Colunas no PDF:", [1, 2, 3], index=1)

if st.sidebar.button("🧹 LIMPAR TUDO"):
    st.session_state.preview_questoes = []; st.session_state.res_calc = ""; st.rerun()

# --- 4. LÓGICA DA SUÍTE ---
st.title(f"🛠️ {menu}")

if menu == "🔢 Operações":
    tipo = st.radio("Operação:", ["Soma", "Subtração", "Multiplicação", "Divisão"], horizontal=True)
    if st.button("GERAR LISTA"):
        s = {"Soma": "+", "Subtração": "-", "Multiplicação": "x", "Divisão": "/"}[tipo]
        st.session_state.preview_questoes = [f"t. Lista de {tipo}", "1. Resolva:"] + \
            [f"{random.randint(10, 999)} {s} {random.randint(10, 99)} =" for _ in range(12)]

elif menu == "📐 Equações":
    grau = st.radio("Grau:", ["1º Grau", "2º Grau"], horizontal=True)
    if st.button("GERAR EQUAÇÕES"):
        if grau == "1º Grau":
            qs = [f"{random.randint(2,9)}x + {random.randint(1,20)} = {random.randint(21,99)}" for _ in range(10)]
        else:
            qs = [f"x² - {random.randint(5,10)}x + {random.randint(1,6)} = 0" for _ in range(5)]
        st.session_state.preview_questoes = [f"t. Equações de {grau}", "1. Resolva:"] + qs

elif menu == "⛓️ Sistemas":
    if st.button("GERAR SISTEMAS"):
        st.session_state.preview_questoes = ["t. Sistemas", "1. Resolva:"] + \
            [f"{{ {random.randint(1,3)}x + y = {random.randint(5,15)} \n  {{ x - y = {random.randint(1,5)}" for _ in range(4)]

elif menu == "𝑓(x) Bhaskara":
    c1, c2, c3 = st.columns(3)
    a, b, c = c1.number_input("a", 1.0), c2.number_input("b", -5.0), c3.number_input("c", 6.0)
    if st.button("CALCULAR"):
        d = b**2 - 4*a*c
        if d >= 0:
            st.session_state.res_calc = f"Delta: {d} | x1: {(-b+math.sqrt(d))/(2*a):.2f} | x2: {(-b-math.sqrt(d))/(2*a):.2f}"
        else: st.session_state.res_calc = "Delta negativo!"

elif menu == "💰 Financeira (Take Profit)":
    entrada = st.number_input("Entrada:", value=100.0)
    alvo = st.number_input("Alvo %:", value=10.0)
    if st.button("CALCULAR TP"):
        venda = entrada * (1 + (alvo/100))
        st.session_state.res_calc = f"Take Profit em: R$ {venda:.2f} (Venda Automática Ativa)"

elif menu == "📄 Manual":
    txt = st.text_area("Questões:")
    if st.button("LANÇAR"): st.session_state.preview_questoes = txt.split("\n")

# --- 5. PREVIEW E PDF (O CONSERTO REAL) ---
if st.session_state.res_calc: st.success(st.session_state.res_calc)

if st.session_state.preview_questoes:
    st.divider()
    for line in st.session_state.preview_questoes:
        if line.strip(): st.write(line)

    def gerar_pdf_bytes():
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
        
        # TRANSFORMA EM BUFFER DE BYTES (Isso impede o erro de suporte)
        buffer = BytesIO()
        pdf_str = pdf.output(dest='S')
        if isinstance(pdf_str, str):
            buffer.write(pdf_str.encode('latin-1'))
        else:
            buffer.write(pdf_str)
        buffer.seek(0)
        return buffer

    # SÓ EXECUTA O BOTÃO SE O BUFFER FOR CRIADO
    try:
        pdf_buffer = gerar_pdf_bytes()
        st.download_button(
            label="📥 BAIXAR PDF COMPLETO",
            data=pdf_buffer, # Passa o objeto BytesIO direto
            file_name="quantum_lab.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.error(f"Erro na geração: {e}")
