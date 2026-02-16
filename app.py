import streamlit as st
import random
import os
import math
from fpdf import FPDF
from io import BytesIO

# --- 1. PERSISTÊNCIA E CONFIGURAÇÃO ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide", page_icon="🚀")

if 'autenticado' not in st.session_state: st.session_state.autenticado = False
if 'preview_questoes' not in st.session_state: st.session_state.preview_questoes = []
if 'res_calc' not in st.session_state: st.session_state.res_calc = ""

# --- 2. LOGIN (CHAVE MESTRA) ---
if not st.session_state.autenticado:
    st.title("🔐 Quantum Suite - Acesso")
    chave_mestra = str(st.secrets.get("chave_mestra", "admin")).strip().lower()
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
    ["Início", "🔢 Operações", "📐 Equações", "⛓️ Sistemas", "Bhaskara", "💰 Financeira (Take Profit)", "📄 Manual"]
)

st.sidebar.divider()
st.sidebar.success("✅ Take Profit: INFINITO ATIVO")
st.sidebar.divider()

usar_cabecalho = st.sidebar.checkbox("Usar cabeçalho.png", value=False)
layout_cols = st.sidebar.selectbox("Colunas no PDF:", [1, 2, 3], index=1)

if st.sidebar.button("🧹 LIMPAR TUDO"):
    st.session_state.preview_questoes = []
    st.session_state.res_calc = ""
    st.rerun()

# --- 4. FUNÇÃO DE GERAÇÃO DE PDF (FORMATO SOLICITADO) ---
def gerar_pdf_bytes():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=10)
    
    y_pos = 45 if usar_cabecalho else 15
    if usar_cabecalho and os.path.exists("cabecalho.png"):
        pdf.image("cabecalho.png", 10, 10, 190)
    
    pdf.set_y(y_pos)
    larg_col = 190 / layout_cols
    l_idx = 0
    letras = "abcdefghijklmnopqrstuvwxyz"

    for line in st.session_state.preview_questoes:
        original_line = line.strip()
        if not original_line: continue

        # --- SUBSTITUIÇÕES MATEMÁTICAS ---
        clean = original_line.replace('x2', 'x²').replace('v2', '√').replace('v3', '³√')
        
        try:
            clean = clean.encode('latin-1', 'replace').decode('latin-1')
        except:
            pass
        
        # --- LÓGICA DE FORMATAÇÃO ---
        if clean.startswith("t."): 
            # TÍTULO: Negrito, Centralizado, Tamanho 14 (FA4)
            pdf.ln(5)
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(190, 10, clean[2:].strip(), ln=True, align='C')
            l_idx = 0 
        
        elif clean.startswith("txt."): 
            # INSTRUÇÃO: Sem Negrito, Esquerda, Tamanho 10
            pdf.ln(2)
            pdf.set_font("Arial", size=10)
            pdf.cell(190, 7, clean[4:].strip(), ln=True, align='L')
            
        else: 
            # QUESTÕES: Sem Negrito, Com Letra, Tamanho 10
            pdf.set_font("Arial", size=10)
            col_at = l_idx % layout_cols
            txt_quest = f"{letras[l_idx % 26]}) {clean}"
            pdf.cell(larg_col, 7, txt_quest, ln=(col_at == layout_cols - 1))
            l_idx += 1
    
    pdf_output = pdf.output(dest='S')
    buffer = BytesIO()
    if isinstance(pdf_output, str):
        buffer.write(pdf_output.encode('latin-1'))
    else:
        buffer.write(pdf_output)
    buffer.seek(0)
    return buffer

# --- 5. LÓGICA DAS FERRAMENTAS ---
st.title(f"🛠️ {menu}")

if menu == "🔢 Operações":
    tipo = st.radio("Operação:", ["Soma", "Subtração", "Multiplicação", "Divisão"], horizontal=True)
    if st.button("GERAR LISTA"):
        s = {"Soma": "+", "Subtração": "-", "Multiplicação": "x", "Divisão": "/"}[tipo]
        st.session_state.preview_questoes = [f"t. Lista de {tipo}", "txt. 1. Resolva as operações abaixo:"] + \
            [f"{random.randint(10, 999)} {s} {random.randint(10, 99)} =" for _ in range(12)]

elif menu == "📐 Equações":
    grau = st.radio("Grau:", ["1º Grau", "2º Grau"], horizontal=True)
    if st.button("GERAR EQUAÇÕES"):
        if grau == "1º Grau":
            qs = [f"{random.randint(2,9)}x + {random.randint(1,20)} = {random.randint(21,99)}" for _ in range(10)]
        else:
            qs = [f"x2 - {random.randint(5,10)}x + {random.randint(1,6)} = 0" for _ in range(5)]
        st.session_state.preview_questoes = [f"t. Equações de {grau}", "txt. 1. Resolva as equações:"] + qs

elif menu == "Bhaskara":
    c1, c2, c3 = st.columns(3)
    a, b, c = c1.number_input("a", 1.0), c2.number_input("b", -5.0), c3.number_input("c", 6.0)
    if st.button("CALCULAR"):
        d = b**2 - 4*a*c
        if d >= 0:
            x1 = (-b+math.sqrt(d))/(2*a); x2 = (-b-math.sqrt(d))/(2*a)
            st.session_state.res_calc = f"Delta: {d} | x1: {x1:.2f} | x2: {x2:.2f}"
        else: st.session_state.res_calc = "Delta negativo!"

elif menu == "💰 Financeira (Take Profit)":
    entrada = st.number_input("Valor de Entrada:", value=100.0)
    alvo = st.number_input("Alvo de Lucro %:", value=10.0)
    if st.button("CALCULAR TP"):
        venda = entrada * (1 + (alvo/100))
        st.session_state.res_calc = f"Take Profit Ativo: R$ {venda:.2f} (Venda Automática Ativa)"

elif menu == "📄 Manual":
    txt = st.text_area("Digite as questões (t. título | txt. instrução):", height=200)
    if st.button("LANÇAR"): 
        st.session_state.preview_questoes = txt.split("\n")

# --- 6. PREVIEW E DOWNLOAD ---
if st.session_state.res_calc: st.info(st.session_state.res_calc)

if st.session_state.preview_questoes:
    st.divider()
    with st.expander("👁️ Ver Rascunho"):
        for line in st.session_state.preview_questoes:
            if line.strip(): st.write(line)

    try:
        pdf_buffer = gerar_pdf_bytes()
        st.download_button(label="📥 BAIXAR PDF", data=pdf_buffer, file_name="quantum_lab.pdf", mime="application/pdf")
    except Exception as e:
        st.error(f"Erro no PDF: {e}")
