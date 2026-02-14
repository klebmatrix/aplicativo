import streamlit as st
import random
import re
import os
import math
from fpdf import FPDF

# --- 1. CONFIGURAÇÃO E PERSISTÊNCIA ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

# Inicialização forçada para não perder dados no refresh
for key in ['perfil', 'sub_menu', 'preview_questoes', 'res_calc']:
    if key not in st.session_state:
        st.session_state[key] = [] if key == 'preview_questoes' else ""

# --- FUNÇÃO DE ESTABILIZAÇÃO (O QUE FALTAVA) ---
def mudar_aba(nome_aba):
    st.session_state.sub_menu = nome_aba
    st.session_state.res_calc = ""

# --- 2. LOGIN ---
def validar_acesso(pin):
    p_aluno = str(st.secrets.get("acesso_aluno", "123456")).strip()
    p_prof = str(st.secrets.get("chave_mestra", "chave_mestra")).strip().lower()
    return "admin" if pin == p_prof else "aluno" if pin == p_aluno else None

if st.session_state.perfil is None:
    st.title("🔐 Login")
    pin_input = st.text_input("PIN:", type="password")
    if st.button("Acessar", key="login_main"):
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
if st.sidebar.button("🧹 Limpar Atividade", key="clear_btn"):
    st.session_state.preview_questoes = []; st.session_state.res_calc = ""; st.rerun()

if st.sidebar.button("🚪 Sair / Logout", key="logout_btn"):
    st.session_state.clear()
    st.rerun()

# --- 4. CENTRO DE COMANDO (AGORA ESTABILIZADO COM CALLBACKS) ---
st.title("🛠️ Centro de Comando Quantum")

# Fileira 1
g1, g2, g3, g4, g5 = st.columns(5)
# Usamos on_click para garantir que o Streamlit salve a mudança
g1.button("🔢 Operações", on_click=mudar_aba, args=("op",), key="c_op", use_container_width=True)
g2.button("📐 Equações", on_click=mudar_aba, args=("eq",), key="c_eq", use_container_width=True)
g3.button("⛓️ Sistemas", on_click=mudar_aba, args=("sis",), key="c_si", use_container_width=True)
g4.button("⚖️ Álgebra", on_click=mudar_aba, args=("alg",), key="c_al", use_container_width=True)
g5.button("📄 Manual", on_click=mudar_aba, args=("man",), key="c_ma", use_container_width=True)

# Fileira 2
c1, c2, c3 = st.columns(3)
c1.button("𝑓(x) Bhaskara", on_click=mudar_aba, args=("calc_f",), key="c_bh", use_container_width=True)
c2.button("📊 PEMDAS", on_click=mudar_aba, args=("pemdas",), key="c_pe", use_container_width=True)
c3.button("💰 Financeira", on_click=mudar_aba, args=("fin",), key="c_fi", use_container_width=True)

st.divider()
menu = st.session_state.sub_menu

# --- 5. LÓGICAS (O RESTO DO SEU CÓDIGO) ---
if menu == "op":
    st.subheader("Gerador de Operações")
    tipo = st.radio("Escolha:", ["Soma", "Subtração", "Multiplicação", "Divisão"], horizontal=True)
    if st.button("Gerar Atividade", key="gen_op"):
        s = {"Soma": "+", "Subtração": "-", "Multiplicação": "x", "Divisão": "÷"}[tipo]
        qs = [f"{random.randint(10, 999)} {s} {random.randint(10, 99)} =" for _ in range(12)]
        st.session_state.preview_questoes = [".M1", f"t. Atividade de {tipo}", "1. Calcule:"] + qs

elif menu == "calc_f":
    st.subheader("Calculadora Bhaskara")
    ca1, ca2, ca3 = st.columns(3)
    a = ca1.number_input("a", value=1.0)
    b = ca2.number_input("b", value=-5.0)
    c = ca3.number_input("c", value=6.0)
    if st.button("Calcular", key="run_bh"):
        d = b**2 - 4*a*c
        if d >= 0: 
            r1 = (-b+math.sqrt(d))/(2*a)
            r2 = (-b-math.sqrt(d))/(2*a)
            st.session_state.res_calc = f"Delta: {d} | x1: {r1:.2f} | x2: {r2:.2f}"
        else: st.session_state.res_calc = "Delta negativo."

# (Mantenha as outras lógicas de eq, sis, alg, man, pemdas e fin aqui conforme seu original...)

if st.session_state.res_calc: st.success(st.session_state.res_calc)

# --- 7. MOTOR PDF ---
if st.session_state.preview_questoes:
    st.subheader("👁️ Preview")
    with st.container(border=True):
        for line in st.session_state.preview_questoes: st.write(line)

    def export_pdf():
        pdf = FPDF(orientation='P', unit='mm', format='A4')
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
                pdf.set_font("Helvetica", size=11)
                col = l_idx % int(layout_cols)
                pdf.cell(larg_col, 8, f"{letras[l_idx%26]}) {line}", ln=(col == int(layout_cols)-1))
                l_idx += 1
        return pdf.output(dest='S').encode('latin-1')

    st.download_button("📥 Baixar PDF", data=export_pdf(), file_name="atividade.pdf", key="down_btn")
