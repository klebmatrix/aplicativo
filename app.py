import streamlit as st
import random
import re
import os
import math
from fpdf import FPDF

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

# Inicialização de estados
if 'perfil' not in st.session_state: st.session_state.perfil = None
if 'sub_menu' not in st.session_state: st.session_state.sub_menu = None
if 'preview_questoes' not in st.session_state: st.session_state.preview_questoes = []
if 'res_calc' not in st.session_state: st.session_state.res_calc = ""

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

if st.sidebar.button("🧹 Limpar Tudo", use_container_width=True):
    st.session_state.preview_questoes = []; st.session_state.sub_menu = None; st.session_state.res_calc = ""; st.rerun()

# --- 4. BOTÕES PRINCIPAIS ---
st.title("🛠️ Centro de Comando Quantum")
g1, g2, g3, g4, g5 = st.columns(5)
if g1.button("🔢 Operações", use_container_width=True): st.session_state.sub_menu = "op"
if g2.button("📐 Equações", use_container_width=True): st.session_state.sub_menu = "eq"
if g3.button("⛓️ Sistemas", use_container_width=True): st.session_state.sub_menu = "sis"
if g4.button("⚖️ Álgebra", use_container_width=True): st.session_state.sub_menu = "alg"
if g5.button("📄 Manual", use_container_width=True): st.session_state.sub_menu = "man"

c1, c2, c3 = st.columns(3)
if c1.button("𝑓(x) Bhaskara", use_container_width=True): st.session_state.sub_menu = "calc_f"
if c2.button("📊 PEMDAS", use_container_width=True): st.session_state.sub_menu = "pemdas"
if c3.button("💰 Financeira", use_container_width=True): st.session_state.sub_menu = "fin"

st.divider()

# --- 5. LÓGICA DE CÁLCULOS E GERAÇÃO ---
menu = st.session_state.sub_menu

if menu == "fin":
    st.subheader("💰 Calculadora Financeira")
    f_cap = st.number_input("Capital Inicial (R$):", value=1000.0)
    f_taxa = st.number_input("Taxa de Juros (%):", value=10.0)
    if st.button("Calcular Juros Simples"):
        res = f_cap * (f_taxa / 100)
        st.session_state.res_calc = f"Juros: R$ {res:.2f} | Total: R$ {f_cap + res:.2f}"

elif menu == "calc_f":
    st.subheader("𝑓(x) Bhaskara")
    fa = st.number_input("a", value=1.0); fb = st.number_input("b", value=-5.0); fc = st.number_input("c", value=6.0)
    if st.button("Calcular Raízes"):
        delta = fb**2 - 4*fa*fc
        if delta >= 0:
            x1 = (-fb + math.sqrt(delta)) / (2*fa)
            x2 = (-fb - math.sqrt(delta)) / (2*fa)
            st.session_state.res_calc = f"Delta: {delta} | x1: {x1} | x2: {x2}"
        else: st.session_state.res_calc = "Delta Negativo."

elif menu == "pemdas":
    st.subheader("📊 PEMDAS")
    exp = st.text_input("Expressão:", "10 + 5 * 2")
    if st.button("Resolver"):
        try: st.session_state.res_calc = f"Resultado: {eval(exp.replace('x','*'))}"
        except: st.error("Erro na expressão")

elif menu == "op":
    tipo = st.radio("Operação:", ["Soma", "Subtração", "Multiplicação", "Divisão"], horizontal=True)
    if st.button("Gerar Atividade"):
        simb = {"Soma": "+", "Subtração": "-", "Multiplicação": "x", "Divisão": "÷"}[tipo]
        st.session_state.preview_questoes = [".M1", f"t. Atividade de {tipo}", "1. Calcule:"] + [f"{random.randint(10,500)} {simb} {random.randint(10,100)} =" for _ in range(12)]

elif menu == "sis":
    if st.button("Gerar Sistemas"):
        st.session_state.preview_questoes = [".M1", "t. Sistemas", "1. Resolva:"] + [f"{{ x + y = {random.randint(5,15)} \n  {{ x - y = {random.randint(1,5)}" for _ in range(3)]

elif menu == "man":
    txt = st.text_area("Texto Manual:")
    if st.button("Aplicar"): st.session_state.preview_questoes = txt.split("\n")

# EXIBE O RESULTADO DO CÁLCULO SE EXISTIR
if st.session_state.res_calc:
    st.success(st.session_state.res_calc)

# --- 6. VISUALIZAÇÃO E PDF ---
if st.session_state.preview_questoes:
    st.divider()
    with st.container(border=True):
        for line in st.session_state.preview_questoes: st.write(line)

    def export_pdf():
        pdf = FPDF()
        pdf.add_page()
        y_pos = 10
        if usar_cabecalho and os.path.exists("cabecalho.png"):
            pdf.image("cabecalho.png", 10, 10, 190)
            y_pos = recuo_cabecalho 
        pdf.set_y(y_pos)
        letras, l_idx = "abcdefghijklmnopqrstuvwxyz", 0
        larg_col = 190 / int(layout_cols)
        for line in st.session_state.preview_questoes:
            line = line.strip()
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
                pdf.cell(larg_col, 8, f"{letras[l_idx%26]}) {line.lstrip('. ')}", ln=(col == int(layout_cols)-1))
                l_idx += 1
        return pdf.output(dest='S').encode('latin-1')

    st.download_button("📥 Baixar PDF", data=export_pdf(), file_name="atividade.pdf")