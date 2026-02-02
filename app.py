import streamlit as st
import random
import re
import os
import math
from fpdf import FPDF

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

for key in ['perfil', 'sub_menu', 'preview_questoes', 'res_calc']:
    if key not in st.session_state:
        st.session_state[key] = [] if key == 'preview_questoes' else ""

# --- 2. LOGIN ---
def validar_acesso(pin):
    p_aluno = str(st.secrets.get("acesso_aluno", "123456")).strip()
    p_prof = str(st.secrets.get("chave_mestra", "chave_mestra")).strip().lower()
    return "admin" if pin == p_prof else "aluno" if pin == p_aluno else None

if not st.session_state.perfil:
    st.title("🔐 Login Quantum")
    pin_input = st.text_input("PIN:", type="password")
    if st.button("Acessar"):
        res = validar_acesso(pin_input)
        if res: st.session_state.perfil = res; st.rerun()
        else: st.error("PIN Incorreto")
    st.stop()

# --- 3. SIDEBAR ---
st.sidebar.title(f"🚀 {st.session_state.perfil.upper()}")
layout_cols = st.sidebar.selectbox("Colunas PDF:", [1, 2, 3], index=1)
if st.sidebar.button("🧹 Limpar Tudo"):
    st.session_state.preview_questoes = []; st.session_state.res_calc = ""; st.rerun()
if st.sidebar.button("🚪 Sair"):
    st.session_state.clear(); st.rerun()

# --- 4. CENTRO DE COMANDO ---
st.title("🛠️ Centro de Comando Quantum")
g1, g2, g3, g4, g5, g6 = st.columns(6)
if g1.button("🔢 Operações"): st.session_state.sub_menu = "op"
if g2.button("📐 Equações"): st.session_state.sub_menu = "eq"
if g3.button("⛓️ Sistemas"): st.session_state.sub_menu = "sis"
if g4.button("⚖️ Álgebra"): st.session_state.sub_menu = "alg"
if g5.button("🎓 Colegial"): st.session_state.sub_menu = "col"
if g6.button("📄 Manual"): st.session_state.sub_menu = "man"

st.divider()
menu = st.session_state.sub_menu

# --- 5. LÓGICAS (COLEGIAL AJUSTADO) ---
if menu == "col":
    tipo = st.radio("Tema:", ["Radiciação", "Potenciação", "Porcentagem"], horizontal=True)
    if tipo == "Radiciação":
        grau = st.radio("Raiz:", ["Quadrada", "Cúbica"], horizontal=True)
        if st.button("Gerar Radiciação"):
            if grau == "Quadrada": qs = [f"SQRT({random.randint(2,15)**2}) =" for _ in range(10)]
            else: qs = [f"3v({random.randint(2,10)**3}) =" for _ in range(10)]
            st.session_state.preview_questoes = [".M1", f"t. Radicacao {grau}", "1. Calcule:"] + qs
    elif tipo == "Potenciação":
        exp = st.selectbox("Expoente:", [2, 3, 4])
        if st.button("Gerar Potenciação"):
            qs = [f"{random.randint(2,12)}^{exp} =" for _ in range(10)]
            st.session_state.preview_questoes = [".M1", f"t. Potenciacao (Exp {exp})", "1. Calcule:"] + qs
    elif tipo == "Porcentagem":
        if st.button("Gerar Porcentagem"):
            qs = [f"{random.randint(1,10)*5}% de {random.randint(10,100)*10} =" for _ in range(10)]
            st.session_state.preview_questoes = [".M1", "t. Porcentagem", "1. Calcule:"] + qs

elif menu == "op":
    if st.button("Gerar Operações"):
        qs = [f"{random.randint(100,999)} + {random.randint(10,99)} =" for _ in range(12)]
        st.session_state.preview_questoes = [".M1", "t. Operacoes", "1. Calcule:"] + qs

elif menu == "man":
    txt = st.text_area("Texto Manual:")
    if st.button("Aplicar"): st.session_state.preview_questoes = txt.split("\n")

# --- 6. MOTOR PDF (RESOLUÇÃO DEFINITIVA) ---
if st.session_state.preview_questoes:
    st.subheader("👁️ Preview")
    for l in st.session_state.preview_questoes: st.write(l)

    def gerar_pdf_bytes():
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.set_y(20)
        letras, l_idx = "abcdefghijklmnopqrstuvwxyz", 0
        larg_col = 190 / int(layout_cols)
        
        for line in st.session_state.preview_questoes:
            line = line.strip()
            if not line: continue
            
            if line.startswith(".M"):
                pdf.set_font("Arial", size=11); pdf.cell(190, 8, line[1:], ln=True)
            elif line.lower().startswith("t."):
                pdf.set_font("Arial", 'B', 14); pdf.cell(190, 10, line[2:].strip(), ln=True, align='C')
            elif re.match(r'^\d+\.', line):
                pdf.set_font("Arial", 'B', 12); pdf.cell(190, 10, line, ln=True); l_idx = 0
            else:
                col = l_idx % int(layout_cols)
                pdf.set_font("Arial", size=12)
                # Formatação simples para evitar erro de caractere
                texto_item = f"{letras[l_idx%26]}) {line}".replace("SQRT", "V")
                pdf.cell(larg_col, 8, texto_item.encode('latin-1', 'ignore').decode('latin-1'), ln=(col == int(layout_cols)-1))
                l_idx += 1
        
        # O pulo do gato: output('S') retorna a string de bytes no fpdf2
        return pdf.output()

    # Convertemos o output explicitamente para bytes para o Streamlit não reclamar
    pdf_data = gerar_pdf_bytes()
    if isinstance(pdf_data, str):
        pdf_data = pdf_data.encode('latin-1')

    st.download_button(
        label="📥 Baixar PDF",
        data=pdf_data,
        file_name="atividade.pdf",
        mime="application/pdf"
    )