import streamlit as st
import random
import re
import os
import math
from fpdf import FPDF

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

# Inicializa as chaves para não dar erro de "KeyError"
for key in ['perfil', 'sub_menu', 'preview_questoes', 'res_calc']:
    if key not in st.session_state:
        st.session_state[key] = [] if key == 'preview_questoes' else ""

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
        if res: 
            st.session_state.perfil = res
            st.rerun()
        else: st.error("PIN Incorreto")
    st.stop()

# --- 3. SIDEBAR ---
st.sidebar.title(f"🚀 {st.session_state.perfil.upper()}")
usar_cabecalho = st.sidebar.checkbox("Ativar cabeçalho", value=True)
layout_cols = st.sidebar.selectbox("Colunas PDF:", [1, 2, 3], index=1)
if st.sidebar.button("🧹 Limpar Tudo"):
    st.session_state.preview_questoes = []; st.session_state.res_calc = ""; st.rerun()
if st.sidebar.button("🚪 Sair"):
    st.session_state.clear(); st.rerun()

# --- 4. CENTRO DE COMANDO (6 GERADORES + 3 CALCULADORES) ---
st.title("🛠️ Centro de Comando Quantum")
g1, g2, g3, g4, g5, g6 = st.columns(6)
if g1.button("🔢 Operações", use_container_width=True): st.session_state.sub_menu = "op"
if g2.button("📐 Equações", use_container_width=True): st.session_state.sub_menu = "eq"
if g3.button("⛓️ Sistemas", use_container_width=True): st.session_state.sub_menu = "sis"
if g4.button("⚖️ Álgebra", use_container_width=True): st.session_state.sub_menu = "alg"
if g5.button("🎓 Colegial", use_container_width=True): st.session_state.sub_menu = "col"
if g6.button("📄 Manual", use_container_width=True): st.session_state.sub_menu = "man"

st.divider()
c1, c2, c3 = st.columns(3)
if c1.button("𝑓(x) Bhaskara", use_container_width=True): st.session_state.sub_menu = "calc_f"
if c2.button("📊 Exp. Numéricas", use_container_width=True): st.session_state.sub_menu = "exp_num"
if c3.button("💰 Financeira", use_container_width=True): st.session_state.sub_menu = "fin"

menu = st.session_state.sub_menu

# --- 5. LÓGICAS DOS GERADORES ---

if menu == "man":
    st.subheader("✍️ Entrada Manual")
    txt_input = st.text_area("Digite as questões (uma por linha):", height=200)
    if st.button("Aplicar Texto Manual"):
        if txt_input:
            st.session_state.preview_questoes = txt_input.split("\n")
            st.success("Texto carregado!")

elif menu == "col":
    t_col = st.radio("Tema:", ["Radiciação", "Potenciação", "Porcentagem"], horizontal=True)
    if st.button("Gerar Atividade Colegial"):
        qs = []
        if t_col == "Radiciação":
            for _ in range(12): qs.append(f"SQRT({random.randint(2,12)**2}) =")
            st.session_state.preview_questoes = [".M1", "t. Radiciação", "1. Calcule:"] + qs
        elif t_col == "Porcentagem":
            for _ in range(10): qs.append(f"{random.randint(1,10)*5}% de {random.randint(10,100)*10} =")
            st.session_state.preview_questoes = [".M1", "t. Porcentagem", "1. Calcule:"] + qs
        else:
            for _ in range(12): qs.append(f"{random.randint(2,15)}² =")
            st.session_state.preview_questoes = [".M1", "t. Potenciação", "1. Calcule:"] + qs

# --- 6. CALCULADORES ---
if menu == "calc_f":
    st.subheader("🧮 Calculadora de Bhaskara")
    col1, col2, col3 = st.columns(3)
    va = col1.number_input("a", value=1.0)
    vb = col2.number_input("b", value=-5.0)
    vc = col3.number_input("c", value=6.0)
    if st.button("Executar Cálculo"):
        delta = (vb**2) - (4 * va * vc)
        if delta < 0:
            st.session_state.res_calc = f"Delta = {delta} (Não existem raízes reais)"
        else:
            x1 = (-vb + math.sqrt(delta)) / (2 * va)
            x2 = (-vb - math.sqrt(delta)) / (2 * va)
            st.session_state.res_calc = f"Delta = {delta} | x1 = {x1:.2f} | x2 = {x2:.2f}"

if st.session_state.res_calc:
    st.info(st.session_state.res_calc)

# --- 7. MOTOR PDF ---
if st.session_state.preview_questoes:
    st.subheader("👁️ Preview")
    for l in st.session_state.preview_questoes:
        st.write(l.replace("SQRT","√").replace("CBRT","∛"))

    def export_pdf():
        pdf = FPDF()
        pdf.add_page()
        pdf.set_y(40)
        letras, l_idx = "abcdefghijklmnopqrstuvwxyz", 0
        larg_col = 190 / int(layout_cols)
        for line in st.session_state.preview_questoes:
            line = line.strip()
            if not line: continue
            if line.startswith(".M"):
                pdf.set_font("Helvetica", size=10); pdf.cell(190, 8, line[1:], ln=True)
            elif line.startswith("t."):
                pdf.set_font("Helvetica", 'B', 14); pdf.cell(190, 10, line[2:].strip(), ln=True, align='C')
            elif re.match(r'^\d+\.', line):
                pdf.set_font("Helvetica", 'B', 12); pdf.cell(190, 10, line, ln=True); l_idx = 0
            else:
                col = l_idx % int(layout_cols)
                pdf.set_font("Helvetica", size=12); pdf.write(8, f"{letras[l_idx%26]}) ")
                if "SQRT" in line:
                    pdf.set_font("Symbol", size=12); pdf.write(8, chr(214))
                    pdf.set_font("Helvetica", size=12); pdf.write(8, line.replace("SQRT(","").replace(")",""))
                else: pdf.write(8, line)
                l_idx += 1
                if col == int(layout_cols)-1: pdf.ln(12)
                else: pdf.set_x(pdf.get_x() + (larg_col - 40))
        return bytes(pdf.output())

    st.download_button("📥 Baixar PDF", data=export_pdf(), file_name="atividade.pdf")