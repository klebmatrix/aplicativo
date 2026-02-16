import streamlit as st
import random
import os
import math
from fpdf import FPDF
from io import BytesIO

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
if 'preview_questoes' not in st.session_state:
    st.session_state.preview_questoes = []
if 'res_calc' not in st.session_state:
    st.session_state.res_calc = ""

# --- LOGIN ---
if not st.session_state.autenticado:
    st.title("🔐 Quantum Suite - Acesso")
    chave = str(st.secrets.get("chave_mestra", "admin")).strip().lower()
    pin = st.text_input("Chave Mestra:", type="password")
    if st.button("DESBLOQUEAR"):
        if pin.lower() == chave:
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("Chave Inválida.")
    st.stop()

# --- SIDEBAR (6 CARDS) ---
st.sidebar.title("🚀 QUANTUM SUITE")
menu = st.sidebar.selectbox("FERRAMENTA:", [
    "🔢 Operações", "📐 Equações", "🎓 Colegial (Rad/Pot/%)", 
    "🧪 Bhaskara", "💰 Financeira (Take Profit)", "📄 Manual"
])

st.sidebar.divider()
st.sidebar.success("✅ Take Profit: INFINITO ATIVO")
st.sidebar.divider()

layout_cols = st.sidebar.selectbox("Colunas no PDF:", [1, 2, 3], index=1)

if st.sidebar.button("🧹 LIMPAR TUDO"):
    st.session_state.preview_questoes = []
    st.session_state.res_calc = ""
    st.rerun()

# --- ENGINE PDF (TITULO 14 NEGRITO CENTRALIZADO) ---
def gerar_pdf_bytes():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.set_y(15)
    larg_col = 190 / layout_cols
    l_idx = 0
    letras = "abcdefghijklmnopqrstuvwxyz"
    for line in st.session_state.preview_questoes:
        clean = line.strip().replace('x2', 'x²').replace('v2', '√')
        try:
            clean = clean.encode('latin-1', 'replace').decode('latin-1')
        except:
            pass
        if clean.startswith("t."):
            pdf.ln(5)
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(190, 10, clean[2:].strip(), ln=True, align='C')
            l_idx = 0 
        elif clean.startswith("txt."):
            pdf.ln(2)
            pdf.set_font("Arial", size=10)
            pdf.cell(190, 7, clean[4:].strip(), ln=True, align='L')
        else:
            pdf.set_font("Arial", size=10)
            col_at = l_idx % layout_cols
            txt_quest = f"{letras[l_idx % 26]}) {clean}"
            pdf.cell(larg_col, 7, txt_quest, ln=(col_at == layout_cols - 1))
            l_idx += 1
    out = pdf.output(dest='S')
    buf = BytesIO()
    buf.write(out.encode('latin-1') if isinstance(out, str) else out)
    buf.seek(0)
    return buf

# --- INTERFACE ---
st.title(f"🛠️ {menu}")

if menu == "🎓 Colegial (Rad/Pot/%)":
    sub = st.radio("Tema:", ["Potenciação", "Radiciação", "Porcentagem"], horizontal=True)
    if st.button("GERAR"):
        if sub == "Potenciação":
            st.session_state.preview_questoes = ["t. Exercícios de Potenciação", "txt. Resolva:"] + [f"{random.randint(2,12)}² =" for _ in range(12)]
        elif sub == "Radiciação":
            st.session_state.preview_questoes = ["t. Exercícios de Radiciação", "txt. Resolva:"] + [f"√{random.randint(4,144)} =" for _ in range(12)]
        else:
            st.session_state.preview_questoes = ["t. Porcentagem", "txt. Calcule:"] + [f"{random.randint(5,50)}% de {random.randint(100,1000)} =" for _ in range(12)]

elif menu == "💰 Financeira (Take Profit)":
    v1 = st.number_input("Entrada:", value=100.0)
    p = st.number_input("Alvo %:", value=10.0)
    if st.button("CALCULAR"):
        st.session_state.res_calc = f"Take Profit Ativo: R$ {v1*(1+p/100):.2f}"

elif menu == "🧪 Bhaskara":
    c1, c2, c3 = st.columns(3)
    a = c1.number_input("a", 1.0)
    b = c2.number_input("b", -5.0)
    c = c3.number_input("c", 6.0)
    if st.button("CALCULAR"):
        delta = b**2 - 4*a*c
        if delta >= 0:
            x1 = (-b + math.sqrt(delta)) / (2*a)
            st.session_state.res_calc = f"Delta: {delta} | x1: {x1:.2f}"
        else:
            st.session_state.res_calc = "Sem raízes reais."

# --- VISUALIZAÇÃO E DOWNLOAD ---
if st.session_state.res_calc:
    st.info(st.session_state.res_calc)

if st.session_state.preview_questoes:
    st.subheader("👀 Visualização das Questões")
    for q in st.session_state.preview_questoes:
        st.text(q)
    
    st.divider()
    try:
        buf = gerar_pdf_bytes()
        st.download_button("📥 BAIXAR PDF", buf, "quantum.pdf", "application/pdf")
    except Exception as e:
        st.error(f"Erro: {e}")
