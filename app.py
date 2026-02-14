import streamlit as st
import random
import re
import os
import math
from fpdf import FPDF

# --- 1. CONFIGURAÇÃO E PERSISTÊNCIA ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

# Inicialização de estados
for key in ['perfil', 'sub_menu', 'preview_questoes', 'res_calc']:
    if key not in st.session_state:
        st.session_state[key] = [] if key == 'preview_questoes' else ""

# FUNÇÃO DE NAVEGAÇÃO (ESTABILIZADORA)
def mudar_aba(aba):
    st.session_state.sub_menu = aba
    st.session_state.res_calc = ""

# --- 2. LOGIN ---
def validar_acesso(pin):
    p_aluno = str(st.secrets.get("acesso_aluno", "123456")).strip()
    p_prof = str(st.secrets.get("chave_mestra", "chave_mestra")).strip().lower()
    return "admin" if pin == p_prof else "aluno" if pin == p_aluno else None

if st.session_state.perfil is None:
    st.title("🔐 Login")
    pin_input = st.text_input("PIN:", type="password")
    if st.button("Acessar"):
        res = validar_acesso(pin_input)
        if res: st.session_state.perfil = res; st.rerun()
        else: st.error("PIN Incorreto")
    st.stop()

# --- 3. SIDEBAR ---
st.sidebar.title(f"🚀 {st.session_state.perfil.upper()}")
usar_cabecalho = st.sidebar.checkbox("Usar cabecalho.png", value=True)
recuo_cabecalho = st.sidebar.slider("Altura do Título:", 20, 80, 45)
layout_cols = st.sidebar.selectbox("Colunas PDF:", [1, 2, 3], index=1)

st.sidebar.divider()
if st.sidebar.button("🧹 Limpar Atividade", use_container_width=True):
    st.session_state.preview_questoes = []; st.session_state.res_calc = ""; st.rerun()

if st.sidebar.button("🚪 Sair / Logout", use_container_width=True):
    st.session_state.clear()
    st.rerun()

# --- 4. CENTRO DE COMANDO (8 BOTÕES ESTABILIZADOS) ---
st.title("🛠️ Centro de Comando Quantum")
g1, g2, g3, g4, g5 = st.columns(5)
# Aqui usamos on_click para o estado não morrer no refresh
g1.button("🔢 Operações", on_click=mudar_aba, args=("op",), key="btn_op", use_container_width=True)
g2.button("📐 Equações", on_click=mudar_aba, args=("eq",), key="btn_eq", use_container_width=True)
g3.button("⛓️ Sistemas", on_click=mudar_aba, args=("sis",), key="btn_si", use_container_width=True)
g4.button("⚖️ Álgebra", on_click=mudar_aba, args=("alg",), key="btn_al", use_container_width=True)
g5.button("📄 Manual", on_click=mudar_aba, args=("man",), key="btn_ma", use_container_width=True)

c1, c2, c3 = st.columns(3)
c1.button("𝑓(x) Bhaskara", on_click=mudar_aba, args=("calc_f",), key="btn_bh", use_container_width=True)
c2.button("📊 PEMDAS", on_click=mudar_aba, args=("pemdas",), key="btn_pe", use_container_width=True)
c3.button("💰 Financeira", on_click=mudar_aba, args=("fin",), key="btn_fi", use_container_width=True)

st.divider()
menu = st.session_state.sub_menu

# --- 5. LÓGICAS (CONTEÚDO) ---
if menu == "op":
    tipo = st.radio("Escolha:", ["Soma", "Subtração", "Multiplicação", "Divisão"], horizontal=True)
    if st.button("Gerar Atividade"):
        s = {"Soma": "+", "Subtração": "-", "Multiplicação": "x", "Divisão": "÷"}[tipo]
        qs = [f"{random.randint(10, 999)} {s} {random.randint(10, 99)} =" for _ in range(12)]
        st.session_state.preview_questoes = [".M1", f"t. Atividade de {tipo}", "1. Calcule:"] + qs

elif menu == "calc_f":
    a = st.number_input("a", value=1.0); b = st.number_input("b", value=-5.0); c = st.number_input("c", value=6.0)
    if st.button("Calcular"):
        d = b**2 - 4*a*c
        if d >= 0:
            x1 = (-b+math.sqrt(d))/(2*a)
            x2 = (-b-math.sqrt(d))/(2*a)
            st.session_state.res_calc = f"Delta: {d} | x1: {x1:.2f} | x2: {x2:.2f}"
        else: st.session_state.res_calc = "Delta negativo."

# Adicione as lógicas de eq, sis, alg, man conforme seu código original aqui...

if st.session_state.res_calc: st.success(st.session_state.res_calc)

# --- 7. MOTOR PDF ---
if st.session_state.preview_questoes:
    st.subheader("👁️ Preview")
    with st.container(border=True):
        for line in st.session_state.preview_questoes: st.write(line)

    def export_pdf():
        pdf = FPDF()
        pdf.add_page()
        y_ini = 10
        if usar_cabecalho and os.path.exists("cabecalho.png"):
            pdf.image("cabecalho.png", 10, 10, 190)
            y_ini = recuo_cabecalho 
        pdf.set_y(y_ini)
        letras, l_idx = "abcdefghijklmnopqrstuvwxyz", 0
        larg_col = 190 / int(layout_cols)
        for line in st.session_state.preview_questoes:
            line = line.strip().encode('latin-1', 'replace').decode('latin-1')
            if not line: continue
            if line.startswith(".M"):
                pdf.set_font("Helvetica", size=12); pdf.cell(190, 10, line[1:], ln=True)
            elif line.lower().startswith("t."):
                pdf.set_font("Helvetica", 'B', 14); pdf.cell(190, 10, line[2:].strip(), ln=True, align='C')
            elif re.match(r'^\d+\.', line):
                pdf.set_font("Helvetica", size=12); pdf.cell(190, 10, line, ln=True); l_idx = 0
            else:
                pdf.set_font("Helvetica", size=12)
                col = l_idx % int(layout_cols)
                pdf.cell(larg_col, 8, f"{letras[l_idx%26]}) {line}", ln=(col == int(layout_cols)-1))
                l_idx += 1
        return pdf.output(dest='S')

    st.download_button("📥 Baixar PDF", data=export_pdf(), file_name="atividade.pdf")
