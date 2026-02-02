import streamlit as st
import random
import re
import os
import math
from fpdf import FPDF

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

if 'perfil' not in st.session_state: st.session_state.perfil = ""
if 'sub_menu' not in st.session_state: st.session_state.sub_menu = ""
if 'preview_questoes' not in st.session_state: st.session_state.preview_questoes = []

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
# OPÇÃO DE CABEÇALHO AQUI
usar_cabecalho = st.sidebar.checkbox("Ativar Cabeçalho (Imagem)", value=True)
layout_cols = st.sidebar.selectbox("Colunas PDF:", [1, 2, 3], index=1)

if st.sidebar.button("🧹 Limpar Tudo"):
    st.session_state.preview_questoes = []; st.rerun()
if st.sidebar.button("🚪 Sair"):
    st.session_state.clear(); st.rerun()

# --- 4. CENTRO DE COMANDO ---
st.title("🛠️ Centro de Comando")
g1, g2, g3, g4, g5, g6 = st.columns(6)
if g1.button("🔢 Operações"): st.session_state.sub_menu = "op"
if g2.button("📐 Equações"): st.session_state.sub_menu = "eq"
if g3.button("⛓️ Sistemas"): st.session_state.sub_menu = "sis"
if g4.button("⚖️ Álgebra"): st.session_state.sub_menu = "alg"
if g5.button("🎓 Colegial"): st.session_state.sub_menu = "col"
if g6.button("📄 Manual"): st.session_state.sub_menu = "man"

st.divider()
menu = st.session_state.sub_menu

# --- 5. LÓGICAS (COLEGIAL COM SELETORES) ---
if menu == "col":
    t = st.radio("Tema:", ["Radiciação", "Potenciação", "Porcentagem"], horizontal=True)
    if t == "Radiciação":
        g = st.radio("Tipo:", ["Quadrada", "Cúbica"], horizontal=True)
        if st.button("Gerar"):
            if g == "Quadrada": qs = [f"SQRT({random.randint(2,15)**2}) =" for _ in range(10)]
            else: qs = [f"3v({random.randint(2,10)**3}) =" for _ in range(10)]
            st.session_state.preview_questoes = [".M1", f"t. Radicacao {g}", "1. Calcule:"] + qs
    elif t == "Potenciação":
        ex = st.selectbox("Expoente:", [2, 3, 4])
        if st.button("Gerar"):
            qs = [f"{random.randint(2,12)}^{ex} =" for _ in range(10)]
            st.session_state.preview_questoes = [".M1", f"t. Potenciacao (Exp {ex})", "1. Calcule:"] + qs
    elif t == "Porcentagem":
        if st.button("Gerar"):
            qs = [f"{random.randint(1,10)*5}% de {random.randint(10,100)*10} =" for _ in range(10)]
            st.session_state.preview_questoes = [".M1", "t. Porcentagem", "1. Calcule:"] + qs

elif menu == "op":
    if st.button("Gerar Operações"):
        qs = [f"{random.randint(10,99)} + {random.randint(10,99)} =" for _ in range(12)]
        st.session_state.preview_questoes = [".M1", "t. Operacoes", "1. Calcule:"] + qs

# --- 6. MOTOR PDF ---
if st.session_state.preview_questoes:
    st.subheader("👁️ Preview")
    for l in st.session_state.preview_questoes: st.write(l)

    def export_pdf():
        pdf = FPDF()
        pdf.add_page()
        
        # LÓGICA DO CABEÇALHO NO PDF
        if usar_cabecalho and os.path.exists("cabecalho.png"):
            pdf.image("cabecalho.png", 10, 10, 190)
            pdf.set_y(55) # Espaço para a imagem
        else:
            pdf.set_y(15) # Começa do topo se estiver desligado
            
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
                txt = f"{letras[l_idx%26]}) {line}".encode('latin-1', 'ignore').decode('latin-1')
                pdf.cell(larg_col, 8, txt, ln=(col == int(layout_cols)-1))
                l_idx += 1
        return bytes(pdf.output())

    st.download_button("📥 Baixar PDF", data=export_pdf(), file_name="atividade.pdf", mime="application/pdf")