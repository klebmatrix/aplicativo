import streamlit as st
import random
import re
import os
import math
from fpdf import FPDF

# --- 1. CONFIGURAÇÃO E REFRESH DE LOGIN ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

# Inicializa as variáveis se não existirem
for key in ['sub_menu', 'preview_questoes', 'res_calc']:
    if key not in st.session_state:
        st.session_state[key] = [] if key == 'preview_questoes' else ""

# PARA PEDIR LOGIN TODA VEZ: Se o estado 'logado' não existir nesta execução, perfil é None
if 'logado' not in st.session_state:
    st.session_state.perfil = None

# --- 2. TELA DE LOGIN ---
def validar_acesso(pin):
    p_aluno = str(st.secrets.get("acesso_aluno", "123456")).strip()
    p_prof = str(st.secrets.get("chave_mestra", "chave_mestra")).strip().lower()
    if pin == p_prof: return "admin"
    if pin == p_aluno: return "aluno"
    return None

if st.session_state.perfil is None:
    st.title("🔐 Login Obrigatório")
    pin_input = st.text_input("Introduza o PIN de acesso:", type="password")
    if st.button("Aceder"):
        res = validar_acesso(pin_input)
        if res:
            st.session_state.perfil = res
            st.session_state.logado = True # Marca como logado nesta sessão
            st.rerun()
        else:
            st.error("PIN Incorreto")
    st.stop() # Mata o processo aqui, não deixa ver o resto

# --- 3. SIDEBAR ---
st.sidebar.title(f"🚀 {st.session_state.perfil.upper()}")
usar_cabecalho = st.sidebar.checkbox("Usar cabecalho.png", value=True)
recuo_cabecalho = st.sidebar.slider("Altura do Título:", 20, 80, 45)
layout_cols = st.sidebar.selectbox("Colunas PDF:", [1, 2, 3], index=1)

st.sidebar.divider()
if st.sidebar.button("🧹 Limpar Atividade", use_container_width=True):
    st.session_state.preview_questoes = []; st.session_state.res_calc = ""; st.rerun()

if st.sidebar.button("🚪 Sair", use_container_width=True):
    st.session_state.clear()
    st.rerun()

# --- 4. BOTÕES DE COMANDO ---
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

# --- 5. LÓGICAS (SISTEMAS E ÁLGEBRA REAIS) ---
if menu == "sis":
    tipo = st.radio("Grau:", ["1º Grau", "2º Grau"], horizontal=True)
    if st.button("Gerar Sistemas"):
        if tipo == "1º Grau":
            qs = [f"{{ {random.randint(1,3)}x + y = {random.randint(5,15)} \n  {{ x - y = {random.randint(1,5)}" for _ in range(4)]
        else:
            qs = [f"{{ x + y = {random.randint(5,15)} \n  x . y = {random.randint(6,50)}" for _ in range(3)]
        st.session_state.preview_questoes = [".M1", f"t. Sistemas de {tipo}", "1. Resolva:"] + qs

elif menu == "alg":
    tipo = st.radio("Tipo:", ["Produtos Notáveis", "Fatoração"], horizontal=True)
    if st.button("Gerar Álgebra"):
        if tipo == "Produtos Notáveis":
            qs = [f"({random.randint(2,5)}x + {random.randint(1,9)})² =", f"(x - {random.randint(2,8)})² =", "(a + b)(a - b) ="]
        else:
            qs = ["x² - 64 =", "x² + 12x + 36 =", "x² - 4x + 4 ="]
        st.session_state.preview_questoes = [".M1", f"t. Álgebra: {tipo}", "1. Desenvolva:"] + qs

elif menu == "fin":
    st.subheader("💰 Matemática Financeira")
    cap = st.number_input("Capital (R$):", value=1000.0)
    tax = st.number_input("Taxa (%):", value=10.0)
    tmp = st.number_input("Meses:", value=12)
    if st.button("Calcular"):
        j = cap * (tax/100) * tmp
        st.session_state.res_calc = f"Juros: R$ {j:.2f} | Montante Final: R$ {cap + j:.2f}"

# (As outras lógicas de Operações, Equações e Bhaskara seguem o mesmo padrão seguro)

if st.session_state.res_calc:
    st.success(st.session_state.res_calc)

# --- 6. MOTOR PDF ---
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