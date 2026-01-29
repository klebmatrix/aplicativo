import streamlit as st
import random
import re
import os
from fpdf import FPDF

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Quantum Math Cards", layout="wide")

# Inicialização de estados
if 'perfil' not in st.session_state: st.session_state.perfil = None
if 'sub_menu' not in st.session_state: st.session_state.sub_menu = None
if 'preview_questoes' not in st.session_state: st.session_state.preview_questoes = []

def clean_txt(text):
    if not text: return ""
    return str(text).encode('latin-1', 'replace').decode('latin-1')

# --- LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Acesso")
    pin = st.text_input("PIN:", type="password")
    if st.button("Entrar"):
        if pin == "123456": st.session_state.perfil = "aluno"
        elif pin.lower() == "chave_mestra": st.session_state.perfil = "admin"
        else: st.error("Incorreto")
        st.rerun()
    st.stop()

# --- MENU DE SELEÇÃO ---
st.title(" cards de Atividades")
cols = st.columns(4)
if cols[0].button("🔢 Operações"): st.session_state.sub_menu = "op"
if cols[1].button("📐 1º Grau"): st.session_state.sub_menu = "eq"
if cols[2].button("📚 Colegial"): st.session_state.sub_menu = "col"
if cols[3].button("⚖️ Álgebra"): st.session_state.sub_menu = "alg"

# --- GERAÇÃO DE CONTEÚDO (LIMPO) ---
op = st.session_state.sub_menu
if op == "op":
    st.session_state.preview_questoes = ["t. Operações Básicas"] + [f"{random.randint(10,500)} {random.choice(['+', '-', 'x'])} {random.randint(2,50)} =" for _ in range(12)]
elif op == "eq":
    st.session_state.preview_questoes = ["t. Equações Lineares"] + [f"{random.randint(2,9)}x + {random.randint(1,20)} = {random.randint(21,99)}" for _ in range(10)]
elif op == "col":
    st.session_state.preview_questoes = ["t. Frações"] + [f"{random.randint(1,9)}/{random.randint(2,5)} + {random.randint(1,9)}/{random.randint(2,5)} =" for _ in range(8)]
elif op == "alg":
    st.session_state.preview_questoes = ["t. Álgebra Linear", "1. Resolva os sistemas:"] + [f"{random.randint(1,5)}x + {random.randint(1,5)}y = {random.randint(10,30)}" for _ in range(6)]

# --- EXIBIÇÃO EM CARDS ---
if st.session_state.preview_questoes:
    st.divider()
    
    # Cabeçalho da Atividade (Imagem no topo conforme solicitado)
    if os.path.exists("cabecalho.png"):
        st.image("cabecalho.png", use_container_width=True)

    letras = "abcdefghijklmnopqrstuvwxyz"
    l_idx = 0
    
    # Renderização dos Cards
    for q in st.session_state.preview_questoes:
        line = q.strip()
        if not line: continue
        
        if line.lower().startswith("t."):
            st.markdown(f"<h2 style='text-align: center; color: #007bff; font-weight: bold;'>{line[2:].strip()}</h2>", unsafe_allow_html=True)
            l_idx = 0
        elif re.match(r'^\d+', line):
            st.subheader(line) # Linha que começa com número (ex: 1. Resolva)
            l_idx = 0
        else:
            # Criando os Cards em 2 colunas
            if l_idx % 2 == 0:
                c_card1, c_card2 = st.columns(2)
                with c_card1:
                    with st.container(border=True):
                        st.write(f"**{letras[l_idx%26]})**")
                        st.write(line)
            else:
                with c_card2:
                    with st.container(border=True):
                        st.write(f"**{letras[l_idx%26]})**")
                        st.write(line)
            l_idx += 1

    # --- BOTÃO DE EXPORTAÇÃO ---
    def export_pdf():
        pdf = FPDF()
        pdf.add_page()
        y = 20
        if os.path.exists("cabecalho.png"):
            pdf.image("cabecalho.png", x=10, y=10, w=190)
            y = 55
        
        pdf.set_font("Arial", size=10)
        l_pdf = 0
        y_base = y
        
        for q in st.session_state.preview_questoes:
            line = q.strip()
            if line.lower().startswith("t."):
                pdf.set_font("Arial", 'B', 14)
                pdf.set_y(y)
                pdf.cell(0, 10, clean_txt(line[2:]), ln=True, align='C')
                y = pdf.get_y() + 5
                pdf.set_font("Arial", size=9)
                l_pdf = 0
            elif re.match(r'^\d+', line):
                pdf.set_y(y)
                pdf.multi_cell(0, 7, clean_txt(line))
                y = pdf.get_y() + 2
                l_pdf = 0
            else:
                txt = f"{letras[l_pdf%26]}) {line}"
                if l_pdf % 2 == 0:
                    y_base = y
                    pdf.set_xy(15, y_base)
                    pdf.multi_cell(90, 10, clean_txt(txt), border=1) # Borda simula o card
                    y_temp = pdf.get_y()
                else:
                    pdf.set_xy(110, y_base)
                    pdf.multi_cell(85, 10, clean_txt(txt), border=1)
                    y = max(y_temp, pdf.get_y()) + 2
                l_pdf += 1
        return pdf.output(dest='S').encode('latin-1')

    st.sidebar.download_button("📥 Gerar PDF dos Cards", export_pdf(), "cards_matematica.pdf", use_container_width=True)