import streamlit as st
import random
import re
import os
import math
from fpdf import FPDF

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

# Inicialização de estados
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

# --- 4. PAINEL DE COMANDO (8 BOTÕES) ---
st.title("🛠️ Centro de Comando")
g1, g2, g3, g4, g5 = st.columns(5)
if g1.button("🔢 Operações", use_container_width=True): st.session_state.sub_menu = "op"
if g2.button("📐 Equações", use_container_width=True): st.session_state.sub_menu = "eq"
if g3.button("📚 Colegial", use_container_width=True): st.session_state.sub_menu = "col"
if g4.button("⚖️ Álgebra", use_container_width=True): st.session_state.sub_menu = "alg"
if g5.button("📄 Manual", use_container_width=True): st.session_state.sub_menu = "man"

c1, c2, c3 = st.columns(3)
if c1.button("𝑓(x) Funções", use_container_width=True): st.session_state.sub_menu = "calc_f"
if c2.button("📊 PEMDAS", use_container_width=True): st.session_state.sub_menu = "pemdas"
if c3.button("💰 Financeira", use_container_width=True): st.session_state.sub_menu = "fin"

st.divider()
menu = st.session_state.sub_menu

# --- 5. LÓGICAS FUNCIONAIS ---
if menu == "op":
    n_ini = st.number_input("Nº Inicial:", value=6)
    if st.button("Gerar 15 Contas"):
        ops = [f"{random.randint(10,999)} + {random.randint(10,999)} =" for _ in range(15)]
        st.session_state.preview_questoes = [".M1", "t. OPERAÇÕES FUNDAMENTAIS", f"{n_ini}. Calcule as somas:"] + ops

elif menu == "eq":
    n_ini = st.number_input("Nº Inicial:", value=1)
    if st.button("Gerar 10 Equações"):
        eqs = [f"{random.randint(2,10)}x {'+' if random.random()>0.5 else '-'} {random.randint(1,30)} = {random.randint(31,100)}" for _ in range(10)]
        st.session_state.preview_questoes = [".M1", "t. EQUAÇÕES DE 1º GRAU", f"{n_ini}. Determine o x:"] + eqs

elif menu == "col":
    if st.button("Gerar Radiciação"):
        rads = [f"√{i**2} =" for i in range(2, 14)]
        st.session_state.preview_questoes = [".M1", "t. RAÍZES QUADRADAS", "1. Calcule:"] + rads

elif menu == "alg":
    if st.button("Gerar Fatoração"):
        st.session_state.preview_questoes = [".M1", "t. ÁLGEBRA", "1. Fatore:"] + ["x² - 4 =", "x² - 9 =", "x² + 2x + 1 ="]

elif menu == "man":
    txt = st.text_area("Texto Manual:")
    if st.button("Aplicar"): st.session_state.preview_questoes = txt.split("\n")

elif menu == "calc_f":
    st.subheader("𝑓(x) - Fórmula de Bhaskara")
    col1, col2, col3 = st.columns(3)
    a = col1.number_input("a", value=1.0)
    b = col2.number_input("b", value=-5.0)
    c = col3.number_input("c", value=6.0)
    if st.button("Calcular"):
        delta = b**2 - 4*a*c
        if delta < 0: st.error("Sem raízes reais.")
        else:
            x1 = (-b + math.sqrt(delta))/(2*a)
            x2 = (-b - math.sqrt(delta))/(2*a)
            st.session_state.res_calc = f"Delta: {delta} | x' = {x1} | x'' = {x2}"

elif menu == "pemdas":
    exp = st.text_input("Expressão (Ex: 2+3*4):", "20 / (2+3) * 4")
    if st.button("Resolver"):
        try: st.session_state.res_calc = f"Resultado: {eval(exp)}"
        except: st.error("Expressão inválida")

elif menu == "fin":
    p = st.number_input("Capital (R$):", value=1000.0)
    i = st.number_input("Taxa (% ao mês):", value=5.0)
    t = st.number_input("Tempo (meses):", value=12)
    if st.button("Juros Simples"):
        j = p * (i/100) * t
        st.session_state.res_calc = f"Juros: R$ {j:.2f} | Total: R$ {p+j:.2f}"

# Exibe resultado do cálculo se houver
if st.session_state.res_calc:
    st.success(st.session_state.res_calc)

# --- 6. VISUALIZAÇÃO E PDF ---
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

    st.download_button("📥 Baixar PDF", data=export_pdf(), file_name="atividade_quantum.pdf")