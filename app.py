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
        st.session_state[key] = [] if key == 'preview_questoes' else None

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

# --- 3. SIDEBAR (ALTURA DE VOLTA AQUI) ---
st.sidebar.title(f"🚀 {st.session_state.perfil.upper()}")
usar_cabecalho = st.sidebar.checkbox("Usar cabecalho.png", value=True)
# CONTROLE DE ALTURA QUE VOCÊ PEDIU
recuo_cabecalho = st.sidebar.slider("Altura do Título (Distância do Topo):", 20, 80, 45)
layout_cols = st.sidebar.selectbox("Colunas PDF:", [1, 2, 3], index=1)

if st.sidebar.button("🧹 Limpar Tudo", use_container_width=True):
    st.session_state.preview_questoes = []; st.session_state.sub_menu = None; st.session_state.res_calc = None; st.rerun()

# --- 4. BOTÕES (5 GERADORES + 3 CÁLCULOS) ---
st.title("🛠️ Centro de Comando Quantum")
g1, g2, g3, g4, g5 = st.columns(5)
if g1.button("🔢 Operações"): st.session_state.sub_menu = "op"
if g2.button("📐 Equações"): st.session_state.sub_menu = "eq"
if g3.button("⛓️ Sistemas"): st.session_state.sub_menu = "sis"
if g4.button("⚖️ Álgebra"): st.session_state.sub_menu = "alg"
if g5.button("📄 Manual"): st.session_state.sub_menu = "man"

c1, c2, c3 = st.columns(3)
if c1.button("𝑓(x) Bhaskara"): st.session_state.sub_menu = "calc_f"
if c2.button("📊 PEMDAS"): st.session_state.sub_menu = "pemdas"
if c3.button("💰 Financeira"): st.session_state.sub_menu = "fin"

st.divider()
menu = st.session_state.sub_menu

# --- 5. LÓGICAS DE GERAÇÃO ---
if menu == "op":
    tipo = st.radio("Operação:", ["Soma", "Subtração", "Multiplicação", "Divisão"], horizontal=True)
    if st.button("Gerar"):
        s = {"Soma": "+", "Subtração": "-", "Multiplicação": "x", "Divisão": "÷"}[tipo]
        st.session_state.preview_questoes = [".M1", f"t. Atividade de {tipo}", "1. Resolva:"] + [f"{random.randint(10, 999)} {s} {random.randint(10, 200)} =" for _ in range(12)]

elif menu == "eq":
    tipo = st.radio("Grau:", ["1º Grau", "2º Grau"], horizontal=True)
    if st.button("Gerar Equações"):
        if tipo == "1º Grau":
            qs = [f"{random.randint(2,9)}x = {random.randint(10,90)}" for _ in range(8)]
        else:
            qs = [f"x² - {random.randint(2,10)}x + {random.randint(1,9)} = 0" for _ in range(5)]
        st.session_state.preview_questoes = [".M1", f"t. Equações de {tipo}", "1. Resolva:"] + qs

elif menu == "sis":
    tipo = st.radio("Sistemas:", ["1º Grau", "2º Grau"], horizontal=True)
    if st.button("Gerar Sistemas"):
        if tipo == "1º Grau":
            qs = [f"{{ {random.randint(1,3)}x + y = {random.randint(5,15)} \n  {{ x - y = {random.randint(1,5)}" for _ in range(3)]
        else:
            qs = [f"{{ x + y = {random.randint(5,15)} \n  x . y = {random.randint(6,50)}" for _ in range(2)]
        st.session_state.preview_questoes = [".M1", f"t. Sistemas de {tipo}", "1. Resolva:"] + qs

elif menu == "alg":
    if st.button("Gerar Álgebra"):
        st.session_state.preview_questoes = [".M1", "t. Exercícios de Álgebra", "1. Desenvolva:"] + ["(x+4)² =", "x² - 16 =", "(a+b)(a-b) ="]

elif menu == "man":
    txt = st.text_area("Texto Manual:")
    if st.button("Aplicar"): st.session_state.preview_questoes = txt.split("\n")

# --- 6. CÁLCULOS ---
elif menu == "calc_f":
    a = st.number_input("a", value=1.0); b = st.number_input("b", value=-5.0); c = st.number_input("c", value=6.0)
    if st.button("Calcular"):
        d = b**2 - 4*a*c
        st.session_state.res_calc = f"x1: {(-b+math.sqrt(d))/(2*a)} | x2: {(-b-math.sqrt(d))/(2*a)}" if d >= 0 else "Sem raízes reais."

if st.session_state.res_calc: st.success(st.session_state.res_calc)

# --- 7. MOTOR PDF ---
if st.session_state.preview_questoes:
    st.subheader("👁️ Visualização")
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
            line = line.strip()
            if not line: continue
            
            if line.startswith(".M"):
                pdf.set_font("Helvetica", size=12); pdf.cell(190, 10, line[1:], ln=True)
            elif line.lower().startswith("t."):
                # TÍTULO EM NEGRITO ('B')
                pdf.set_font("Helvetica", 'B', 14)
                pdf.cell(190, 10, line[2:].strip(), ln=True, align='C')
            elif re.match(r'^\d+\.', line):
                # QUESTÃO NORMAL
                pdf.set_font("Helvetica", size=12); pdf.cell(190, 10, line, ln=True); l_idx = 0
            else:
                # ITENS NORMAL
                pdf.set_font("Helvetica", size=12)
                col = l_idx % int(layout_cols)
                pdf.cell(larg_col, 8, f"{letras[l_idx%26]}) {line.lstrip('. ')}", ln=(col == int(layout_cols)-1))
                l_idx += 1
        return pdf.output(dest='S').encode('latin-1')

    st.download_button("📥 Baixar PDF", data=export_pdf(), file_name="atividade.pdf")