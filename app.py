import streamlit as st
import random
import re
import os
import math
from fpdf import FPDF

# --- 1. CONFIGURAÇÃO E ESTADO ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

for key in ['perfil', 'sub_menu', 'preview_questoes', 'res_calc']:
    if key not in st.session_state:
        st.session_state[key] = [] if key == 'preview_questoes' else None

# --- 2. LOGIN (Secrets Render) ---
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
layout_cols = st.sidebar.selectbox("Colunas PDF:", [1, 2, 3], index=1)

if st.sidebar.button("🧹 Limpar Tudo", use_container_width=True):
    st.session_state.preview_questoes = []; st.session_state.sub_menu = None; st.session_state.res_calc = None; st.rerun()

if st.sidebar.button("🚪 Sair", use_container_width=True):
    st.session_state.clear(); st.rerun()

# --- 4. INTERFACE DE BOTÕES (5 GERADORES + 3 CÁLCULOS) ---
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
menu = st.session_state.sub_menu

# --- 5. LÓGICAS DOS GERADORES ---
if menu == "op":
    tipo = st.radio("Operação:", ["Soma", "Subtração", "Multiplicação", "Divisão"], horizontal=True)
    if st.button("Gerar Operações"):
        s = {"Soma": "+", "Subtração": "-", "Multiplicação": "x", "Divisão": "÷"}[tipo]
        questoes = [f"{random.randint(10, 999)} {s} {random.randint(10, 200)} =" for _ in range(12)]
        st.session_state.preview_questoes = [".M1", f"t. {tipo.upper()}", "1. Calcule:"] + questoes

elif menu == "eq":
    tipo = st.radio("Grau:", ["1º Grau", "2º Grau"], horizontal=True)
    if st.button("Gerar Equações"):
        if tipo == "1º Grau":
            qs = [f"{random.randint(2,9)}x {'+' if random.random()>0.5 else '-'} {random.randint(1,20)} = {random.randint(21,80)}" for _ in range(8)]
        else:
            qs = [f"x² {'-' if random.random()>0.5 else '+'} {random.randint(2,10)}x + {random.randint(1,15)} = 0" for _ in range(5)]
        st.session_state.preview_questoes = [".M1", f"t. EQUAÇÕES {tipo}", "1. Resolva:"] + qs

elif menu == "sis":
    tipo = st.radio("Sistemas:", ["1º Grau", "2º Grau"], horizontal=True)
    if st.button("Gerar Sistemas"):
        if tipo == "1º Grau":
            qs = [f"{{ {random.randint(1,3)}x + {random.randint(1,3)}y = {random.randint(5,20)} \n  {random.randint(1,3)}x - {random.randint(1,3)}y = {random.randint(1,10)}" for _ in range(4)]
        else:
            qs = [f"{{ x + y = {random.randint(5,15)} \n  x . y = {random.randint(6,50)}" for _ in range(3)]
        st.session_state.preview_questoes = [".M1", f"t. SISTEMAS {tipo}", "1. Resolva os sistemas:"] + qs

elif menu == "alg":
    tipo = st.radio("Álgebra:", ["Produtos Notáveis", "Fatoração"], horizontal=True)
    if st.button("Gerar Álgebra"):
        if tipo == "Produtos Notáveis":
            qs = ["(x+5)² =", "(x-3)² =", "(2x+1)² =", "(a+b)(a-b) ="]
        else:
            qs = ["x² - 25 =", "x² + 4x + 4 =", "x² - 10x + 25 ="]
        st.session_state.preview_questoes = [".M1", f"t. {tipo.upper()}", "1. Desenvolva:"] + qs

elif menu == "man":
    txt = st.text_area("Texto Manual (.M1 = Margem, t. = Título, 1. = Questão):")
    if st.button("Aplicar"): st.session_state.preview_questoes = txt.split("\n")

# --- 6. LÓGICAS DOS CÁLCULOS ---
elif menu == "calc_f":
    a = st.number_input("a", value=1.0); b = st.number_input("b", value=-5.0); c = st.number_input("c", value=6.0)
    if st.button("Calcular"):
        d = b**2 - 4*a*c
        if d >= 0: st.session_state.res_calc = f"Delta: {d} | x1: {(-b+math.sqrt(d))/(2*a)} | x2: {(-b-math.sqrt(d))/(2*a)}"
        else: st.session_state.res_calc = "Delta negativo, sem raízes reais."

elif menu == "pemdas":
    exp = st.text_input("Expressão:", "10 + (2 * 5)")
    if st.button("Resolver"):
        try: st.session_state.res_calc = f"Resultado: {eval(exp.replace('x','*'))}"
        except: st.error("Erro na expressão.")

elif menu == "fin":
    p = st.number_input("Capital", value=1000.0); i = st.number_input("Taxa %", value=2.0); t = st.number_input("Meses", value=12)
    if st.button("Calcular Juros Simples"):
        st.session_state.res_calc = f"Juros: R$ {p*(i/100)*t:.2f} | Total: R$ {p+(p*(i/100)*t):.2f}"

if st.session_state.res_calc:
    st.success(st.session_state.res_calc)

# --- 7. VISUALIZAÇÃO E PDF ---
if st.session_state.preview_questoes:
    st.subheader("👁️ Visualização")
    with st.container(border=True):
        for line in st.session_state.preview_questoes: st.write(line)

    def export_pdf():
        pdf = FPDF()
        pdf.add_page()
        y_pos = 10
        if usar_cabecalho and os.path.exists("cabecalho.png"):
            pdf.image("cabecalho.png", 10, 10, 190)
            y_pos = 65 
        pdf.set_y(y_pos)
        letras, l_idx = "abcdefghijklmnopqrstuvwxyz", 0
        n_cols = int(layout_cols)
        larg_col = 190 / n_cols
        for line in st.session_state.preview_questoes:
            line = line.strip()
            if not line: continue
            if line.startswith(".M"):
                pdf.set_font("Helvetica", 'B', 12); pdf.cell(190, 10, line[1:], ln=True)
            elif line.lower().startswith("t."):
                pdf.set_font("Helvetica", 'B', 14); pdf.cell(190, 10, line[2:].strip().upper(), ln=True, align='C')
            elif re.match(r'^\d+\.', line):
                pdf.set_font("Helvetica", 'B', 12); pdf.cell(190, 10, line, ln=True); l_idx = 0
            else:
                pdf.set_font("Helvetica", size=12)
                col = l_idx % n_cols
                pdf.cell(larg_col, 8, f"{letras[l_idx%26]}) {line.lstrip('. ')}", ln=(col == n_cols-1))
                l_idx += 1
        return pdf.output(dest='S').encode('latin-1')

    st.download_button("📥 Baixar PDF", data=export_pdf(), file_name="atividade_completa.pdf")