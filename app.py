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

# --- SIDEBAR ---
st.sidebar.title("🚀 QUANTUM SUITE")
menu = st.sidebar.selectbox("FERRAMENTA:", [
    "🔢 Operações", "📐 Equações", "🎓 Colegial (Rad/Pot/%)", 
    "🧪 Bhaskara", "💰 Financeira (Take Profit)", "📄 Manual"
])

st.sidebar.divider()
st.sidebar.success("✅ Take Profit: INFINITO ATIVO")
st.sidebar.divider()

# OPÇÕES DO PDF
usar_img_cabecalho = st.sidebar.checkbox("Usar imagem 'cabeçalho' da pasta", value=True)
layout_cols = st.sidebar.selectbox("Colunas no PDF:", [1, 2, 3], index=1)

if st.sidebar.button("🧹 LIMPAR TUDO"):
    st.session_state.preview_questoes = []
    st.session_state.res_calc = ""
    st.rerun()

# --- PDF ENGINE COM IMAGEM ---
def gerar_pdf_bytes():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=10)
    
    # Tenta carregar a imagem da pasta
    if usar_img_cabecalho:
        img_path = None
        # Procura por extensões comuns
        for ext in [".png", ".jpg", ".jpeg"]:
            if os.path.exists(f"cabeçalho{ext}"):
                img_path = f"cabeçalho{ext}"
                break
        
        if img_path:
            # Insere a imagem (ajustada para a largura da página)
            pdf.image(img_path, x=10, y=8, w=190)
            pdf.ln(45) # Espaço para não escrever em cima da imagem
        else:
            st.sidebar.error("⚠️ Arquivo 'cabeçalho' não achado na pasta!")
            pdf.set_y(15)
    else:
        pdf.set_y(15)

    larg_col = 190 / layout_cols
    l_idx = 0
    letras = "abcdefghijklmnopqrstuvwxyz"
    
    for line in st.session_state.preview_questoes:
        clean = line.strip().replace('x2', 'x²').replace('v2', '√')
        try: clean = clean.encode('latin-1', 'replace').decode('latin-1')
        except: pass
        
        if clean.startswith("t."):
            pdf.ln(5)
            pdf.set_font("Arial", 'B', 14) # TITULO NEGRITO 14 CENTRALIZADO
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

# (Aqui seguem as ferramentas de Operações, Equações, etc., igual ao anterior)
if menu == "🎓 Colegial (Rad/Pot/%)":
    sub = st.radio("Tema:", ["Potenciação", "Radiciação", "Porcentagem"], horizontal=True)
    if st.button("GERAR"):
        if sub == "Potenciação":
            st.session_state.preview_questoes = ["t. Potenciação", "txt. Calcule:"] + [f"{random.randint(2,12)}² =" for _ in range(12)]
        elif sub == "Radiciação":
            st.session_state.preview_questoes = ["t. Radiciação", "txt. Calcule:"] + [f"√{random.randint(4,144)} =" for _ in range(12)]
        else:
            st.session_state.preview_questoes = ["t. Porcentagem", "txt. Calcule:"] + [f"{random.randint(5,50)}% de {random.randint(100,1000)} =" for _ in range(12)]

elif menu == "🔢 Operações":
    tipo = st.radio("Operação:", ["Soma", "Subtração", "Multiplicação", "Divisão"], horizontal=True)
    if st.button("GERAR"):
        s = {"Soma": "+", "Subtração": "-", "Multiplicação": "x", "Divisão": "/"}[tipo]
        st.session_state.preview_questoes = [f"t. Lista de {tipo}", "txt. Resolva:"] + [f"{random.randint(10,999)} {s} {random.randint(10,99)} =" for _ in range(12)]

# --- VISUALIZAÇÃO ---
st.divider()
if st.session_state.preview_questoes:
    st.subheader("👀 Visualização do Conteúdo")
    with st.container(border=True):
        for q in st.session_state.preview_questoes:
            st.text(q)
    
    try:
        buf = gerar_pdf_bytes()
        st.download_button("📥 BAIXAR PDF", buf, "quantum.pdf", "application/pdf")
    except Exception as e:
        st.error(f"Erro: {e}")
