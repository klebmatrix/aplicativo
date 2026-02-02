import streamlit as st
import random
import re
import os
import math
from fpdf import FPDF

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

for key in ['perfil', 'sub_menu', 'preview_questoes', 'res_calc']:
    if key not in st.session_state:
        st.session_state[key] = [] if key == 'preview_questoes' else ""

# --- LOGIN ---
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

# --- SIDEBAR ---
st.sidebar.title(f"🚀 {st.session_state.perfil.upper()}")
usar_cabecalho = st.sidebar.checkbox("Ativar cabeçalho", value=True)
layout_cols = st.sidebar.selectbox("Colunas PDF:", [1, 2, 3], index=1)
if st.sidebar.button("🧹 Limpar"):
    st.session_state.preview_questoes = []; st.session_state.res_calc = ""; st.rerun()
if st.sidebar.button("🚪 Sair"):
    st.session_state.clear(); st.rerun()

# --- CENTRO DE COMANDO ---
st.title("🛠️ Centro de Comando")
g1, g2, g3, g4, g5, g6 = st.columns(6)
if g1.button("🔢 Operações"): st.session_state.sub_menu = "op"
if g2.button("📐 Equações"): st.session_state.sub_menu = "eq"
if g3.button("⛓️ Sistemas"): st.session_state.sub_menu = "sis"
if g4.button("⚖️ Álgebra"): st.session_state.sub_menu = "alg"
if g5.button("🎓 Colegial"): st.session_state.sub_menu = "col"
if g6.button("📄 Manual"): st.session_state.sub_menu = "man"

st.divider()
c1, c2, c3 = st.columns(3)
if c1.button("𝑓(x) Bhaskara"): st.session_state.sub_menu = "calc_f"
if c2.button("📊 Exp. Numéricas"): st.session_state.sub_menu = "exp_num"
if c3.button("💰 Financeira"): st.session_state.sub_menu = "fin"

menu = st.session_state.sub_menu

# --- LÓGICAS DE GERAÇÃO ---

if menu == "eq":
    tipo = st.radio("Grau:", ["1º Grau", "2º Grau"], horizontal=True)
    if st.button("Gerar Equações"):
        if tipo == "1º Grau":
            qs = [f"{random.randint(2,9)}x {'+' if random.random()>0.5 else '-'} {random.randint(1,20)} = {random.randint(21,99)}" for _ in range(10)]
        else:
            qs = [f"x² {'-' if random.random()>0.5 else '+'} {random.randint(2,10)}x + {random.randint(1,16)} = 0" for _ in range(6)]
        st.session_state.preview_questoes = [".M1", f"t. Equações de {tipo}", "1. Resolva:"] + qs

elif menu == "sis":
    tipo = st.radio("Grau:", ["1º Grau", "2º Grau"], horizontal=True)
    if st.button("Gerar Sistemas"):
        qs = []
        for _ in range(4):
            x, y = random.randint(1,10), random.randint(1,5)
            if tipo == "1º Grau": qs.append(f"{{ x + y = {x+y} \n  x - y = {x-y}")
            else: qs.append(f"{{ x + y = {x+y} \n  x . y = {x*y}")
        st.session_state.preview_questoes = [".M1", f"t. Sistemas de {tipo}", "1. Resolva:"] + qs

elif menu == "alg":
    tipo = st.radio("Tipo:", ["Produtos Notáveis", "Fatoração"], horizontal=True)
    if st.button("Gerar Álgebra"):
        if tipo == "Produtos Notáveis":
            qs = [f"({random.randint(2,5)}x + {random.randint(1,9)})² =" for _ in range(6)]
        else:
            qs = ["x² - 25 =", "x² + 10x + 25 =", "x² - 81 =", "a² - 2ab + b² ="]
        st.session_state.preview_questoes = [".M1", f"t. Expressões Algébricas", "1. Desenvolva:"] + qs

elif menu == "col":
    tipo = st.radio("Tema:", ["Radiciação", "Potenciação"], horizontal=True)
    if tipo == "Radiciação":
        m = st.selectbox("Raiz:", ["Quadrada", "Cúbica", "Misturada"])
        if st.button("Gerar"):
            qs = []
            for _ in range(12):
                sel = m if m != "Misturada" else random.choice(["Quadrada", "Cúbica"])
                if sel == "Quadrada": qs.append(f"SQRT({random.randint(2,12)**2}) =")
                else: qs.append(f"CBRT({random.randint(2,5)**3}) =")
            st.session_state.preview_questoes = [".M1", "t. Radiciação", "1. Calcule:"] + qs

elif menu == "exp_num":
    if st.button("Gerar Expressões Numéricas"):
        qs = [f"{random.randint(10,50)} + {random.randint(2,10)} x ({random.randint(5,15)} - {random.randint(1,4)}) =" for _ in range(8)]
        st.session_state.preview_questoes = [".M1", "t. Expressões Numéricas", "1. Calcule o valor:"] + qs

# --- MOTOR PDF ---
if st.session_state.preview_questoes:
    st.subheader("Preview")
    for l in st.session_state.preview_questoes: st.write(l.replace("SQRT","√").replace("CBRT","∛"))

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
                pdf.set_font("Helvetica", 'B', 14); pdf.cell(190, 10, line[2:], ln=True, align='C')
            elif re.match(r'^\d+\.', line):
                pdf.set_font("Helvetica", 'B', 12); pdf.cell(190, 10, line, ln=True); l_idx = 0
            else:
                col = l_idx % int(layout_cols)
                pdf.set_font("Helvetica", size=12); pdf.write(8, f"{letras[l_idx%26]}) ")
                if "SQRT" in line:
                    pdf.set_font("Symbol", size=12); pdf.write(8, chr(214))
                    pdf.set_font("Helvetica", size=12); pdf.write(8, line.replace("SQRT(","").replace(")",""))
                elif "CBRT" in line:
                    pdf.set_font("Helvetica", size=8); pdf.write(8, "3")
                    pdf.set_font("Symbol", size=12); pdf.write(8, chr(214))
                    pdf.set_font("Helvetica", size=12); pdf.write(8, line.replace("CBRT(","").replace(")",""))
                else: pdf.write(8, line)
                l_idx += 1
                if col == int(layout_cols)-1: pdf.ln(12)
                else: pdf.set_x(pdf.get_x() + (larg_col - 40))
        return bytes(pdf.output())

    st.download_button("📥 Baixar PDF", data=export_pdf(), file_name="atividade.pdf")