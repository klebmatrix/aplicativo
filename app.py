import streamlit as st
import random
import re
import os
import math
from fpdf import FPDF

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

# Inicialização forçada para não sumir o menu
if 'perfil' not in st.session_state: st.session_state.perfil = ""
if 'sub_menu' not in st.session_state: st.session_state.sub_menu = ""
if 'preview_questoes' not in st.session_state: st.session_state.preview_questoes = []
if 'res_calc' not in st.session_state: st.session_state.res_calc = ""

# --- 2. LOGIN ---
def validar_acesso(pin):
    p_aluno = str(st.secrets.get("acesso_aluno", "123456")).strip()
    p_prof = str(st.secrets.get("chave_mestra", "chave_mestra")).strip().lower()
    if pin == p_prof: return "admin"
    if pin == p_aluno: return "aluno"
    return None

if not st.session_state.perfil:
    st.title("🔐 Login Quantum")
    pin_input = st.text_input("PIN:", type="password")
    if st.button("Acessar"):
        res = validar_acesso(pin_input)
        if res: 
            st.session_state.perfil = res
            st.rerun()
        else: st.error("PIN Incorreto")
    st.stop()

# --- 3. SIDEBAR ---
st.sidebar.title(f"🚀 {st.session_state.perfil.upper()}")
layout_cols = st.sidebar.selectbox("Colunas PDF:", [1, 2, 3], index=1)
if st.sidebar.button("🧹 Limpar Tudo"):
    st.session_state.preview_questoes = []
    st.session_state.res_calc = ""
    st.session_state.sub_menu = ""
    st.rerun()
if st.sidebar.button("🚪 Sair"):
    st.session_state.clear()
    st.rerun()

# --- 4. CENTRO DE COMANDO ---
st.title("🛠️ Centro de Comando Quantum")
g1, g2, g3, g4, g5, g6 = st.columns(6)

if g1.button("🔢 Operações", use_container_width=True): st.session_state.sub_menu = "op"
if g2.button("📐 Equações", use_container_width=True): st.session_state.sub_menu = "eq"
if g3.button("⛓️ Sistemas", use_container_width=True): st.session_state.sub_menu = "sis"
if g4.button("⚖️ Álgebra", use_container_width=True): st.session_state.sub_menu = "alg"
if g5.button("🎓 Colegial", use_container_width=True): st.session_state.sub_menu = "col"
if g6.button("📄 Manual", use_container_width=True): st.session_state.sub_menu = "man"

st.divider()

# --- 5. LÓGICAS DOS GERADORES ---
menu = st.session_state.sub_menu

if menu == "col":
    st.subheader("🎓 Módulo Colegial")
    tipo_col = st.radio("Escolha o tema:", ["Radiciação", "Potenciação", "Porcentagem"], horizontal=True)
    
    if tipo_col == "Radiciação":
        grau = st.radio("Tipo de Raiz:", ["Quadrada", "Cúbica"], horizontal=True)
        if st.button("Gerar Atividade de Raiz"):
            if grau == "Quadrada":
                qs = [f"SQRT({random.randint(2,15)**2}) =" for _ in range(10)]
            else:
                qs = [f"Raiz Cubica de ({random.randint(2,10)**3}) =" for _ in range(10)]
            st.session_state.preview_questoes = [".M1", f"t. Radicacao {grau}", "1. Calcule:"] + qs

    elif tipo_col == "Potenciação":
        expo = st.selectbox("Escolha o expoente:", [2, 3, 4])
        if st.button("Gerar Atividade de Potência"):
            qs = [f"{random.randint(2,12)}^{expo} =" for _ in range(10)]
            st.session_state.preview_questoes = [".M1", f"t. Potenciacao (Exp {expo})", "1. Calcule:"] + qs

    elif tipo_col == "Porcentagem":
        if st.button("Gerar Atividade de Porcentagem"):
            qs = [f"{random.randint(1,15)*5}% de {random.randint(10,100)*10} =" for _ in range(10)]
            st.session_state.preview_questoes = [".M1", "t. Porcentagem", "1. Calcule:"] + qs

elif menu == "op":
    tipo_op = st.radio("Operação:", ["Soma", "Subtração", "Multiplicação", "Divisão"], horizontal=True)
    if st.button("Gerar Operações"):
        s = {"Soma": "+", "Subtração": "-", "Multiplicação": "x", "Divisão": ":"}[tipo_op]
        qs = [f"{random.randint(100,999)} {s} {random.randint(10,99)} =" for _ in range(12)]
        st.session_state.preview_questoes = [".M1", f"t. {tipo_op}", "1. Efetue as contas:"] + qs

elif menu == "man":
    txt = st.text_area("Digite as questões (uma por linha):")
    if st.button("Aplicar Manual"):
        st.session_state.preview_questoes = txt.split("\n")

# --- 6. PREVIEW E PDF ---
if st.session_state.preview_questoes:
    st.divider()
    st.subheader("👁️ Preview da Atividade")
    for l in st.session_state.preview_questoes:
        st.write(l.replace("SQRT", "√"))

    def export_pdf():
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.set_y(20)
        letras = "abcdefghijklmnopqrstuvwxyz"
        l_idx = 0
        larg_col = 190 / int(layout_cols)
        
        for line in st.session_state.preview_questoes:
            line = line.strip()
            if not line: continue
            
            if line.startswith(".M"):
                pdf.set_font("Arial", size=10); pdf.cell(190, 8, line[1:], ln=True)
            elif line.lower().startswith("t."):
                pdf.set_font("Arial", 'B', 14); pdf.cell(190, 10, line[2:].strip(), ln=True, align='C')
            elif re.match(r'^\d+\.', line):
                pdf.set_font("Arial", 'B', 12); pdf.cell(190, 10, line, ln=True); l_idx = 0
            else:
                col = l_idx % int(layout_cols)
                pdf.set_font("Arial", size=12)
                txt = f"{letras[l_idx%26]}) {line}".replace("SQRT", "V")
                pdf.cell(larg_col, 8, txt.encode('latin-1', 'ignore').decode('latin-1'), ln=(col == int(layout_cols)-1))
                l_idx += 1
        return pdf.output()

    # O segredo para o Render não dar erro de bytes:
    pdf_bytes = export_pdf()
    
    st.download_button(
        label="📥 Baixar PDF",
        data=pdf_bytes,
        file_name="atividade.pdf",
        mime="application/pdf"
    )