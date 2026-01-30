import streamlit as st
import random
import re
import os
import math
from fpdf import FPDF

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

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

# --- 4. BOTÕES ---
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

# --- 5. LÓGICAS DE GERAÇÃO (SISTEMAS E ÁLGEBRA LEGAIS) ---
if menu == "sis":
    st.subheader("⛓️ Sistemas de Equações")
    tipo_sis = st.radio("Escolha o Grau:", ["1º Grau", "2º Grau"], horizontal=True)
    if st.button("Gerar Atividade de Sistemas"):
        questoes = []
        if tipo_sis == "1º Grau":
            for _ in range(4):
                x, y = random.randint(1, 10), random.randint(1, 10)
                a1, b1 = random.randint(1, 3), random.randint(1, 3)
                a2, b2 = random.randint(1, 3), 1 # simplificado para garantir solução
                r1, r2 = (a1*x + b1*y), (a2*x - b2*y)
                questoes.append(f"{{ {a1}x + {b1}y = {r1} \n  {a2}x - {y} = {r2}")
        else:
            for _ in range(3):
                s, p = random.randint(5, 12), random.randint(6, 30)
                questoes.append(f"{{ x + y = {s} \n  x . y = {p}")
        st.session_state.preview_questoes = [".M1", f"t. Sistemas de {tipo_sis}", "1. Resolva os sistemas abaixo:"] + questoes

elif menu == "alg":
    st.subheader("⚖️ Álgebra (Produtos e Fatoração)")
    tipo_alg = st.radio("Tipo:", ["Produtos Notáveis", "Fatoração"], horizontal=True)
    if st.button("Gerar Atividade de Álgebra"):
        if tipo_alg == "Produtos Notáveis":
            qs = [f"({random.randint(2,5)}x + {random.randint(1,9)})² =", f"(x - {random.randint(2,10)})² =", "(a + b)(a - b) ="]
        else:
            qs = ["x² - 49 =", "x² + 10x + 25 =", "x² - 8x + 16 ="]
        st.session_state.preview_questoes = [".M1", f"t. Álgebra: {tipo_alg}", "1. Desenvolva os exercícios:"] + qs

# --- CÁLCULOS (GARANTINDO QUE FUNCIONEM) ---
elif menu == "fin":
    st.subheader("💰 Calculadora Financeira")
    f_cap = st.number_input("Capital (R$):", value=1000.0)
    f_taxa = st.number_input("Taxa (%):", value=5.0)
    f_tempo = st.number_input("Tempo (meses):", value=12)
    if st.button("Calcular"):
        j = f_cap * (f_taxa/100) * f_tempo
        st.session_state.res_calc = f"Juros: R$ {j:.2f} | Total: R$ {f_cap + j:.2f}"

# (Bhaskara e PEMDAS seguem a mesma lógica de salvar no res_calc)

if st.session_state.res_calc:
    st.success(st.session_state.res_calc)

# --- 6. MOTOR PDF ---
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