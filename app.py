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
        if res: st.session_state.perfil = res; st.rerun()
        else: st.error("PIN Incorreto")
    st.stop()

# --- 3. SIDEBAR (PROFESSOR) ---
st.sidebar.title(f"🚀 {st.session_state.perfil.upper()}")
usar_cabecalho = st.sidebar.checkbox("Ativar cabeçalho", value=True)
layout_cols = st.sidebar.selectbox("Colunas PDF:", [1, 2, 3], index=1)
if st.sidebar.button("🧹 Limpar Atividade"):
    st.session_state.preview_questoes = []; st.session_state.res_calc = ""; st.rerun()
if st.sidebar.button("🚪 Sair"):
    st.session_state.clear(); st.rerun()

# --- 4. CENTRO DE COMANDO (6 GERADORES) ---
st.title("🛠️ Centro de Comando Quantum")
g1, g2, g3, g4, g5, g6 = st.columns(6)
if g1.button("🔢 Operações", use_container_width=True): st.session_state.sub_menu = "op"
if g2.button("📐 Equações", use_container_width=True): st.session_state.sub_menu = "eq"
if g3.button("⛓️ Sistemas", use_container_width=True): st.session_state.sub_menu = "sis"
if g4.button("⚖️ Álgebra", use_container_width=True): st.session_state.sub_menu = "alg"
if g5.button("🎓 Colegial", use_container_width=True): st.session_state.sub_menu = "col"
if g6.button("📄 Manual", use_container_width=True): st.session_state.sub_menu = "man"

st.divider()

# (3 CALCULADORES)
c1, c2, c3 = st.columns(3)
if c1.button("𝑓(x) Bhaskara", use_container_width=True): st.session_state.sub_menu = "calc_f"
if c2.button("📊 Exp. Numéricas", use_container_width=True): st.session_state.sub_menu = "exp_num"
if c3.button("💰 Financeira", use_container_width=True): st.session_state.sub_menu = "fin"

menu = st.session_state.sub_menu

# --- 5. LÓGICAS DOS GERADORES ---

if menu == "op":
    tipo_op = st.radio("Escolha a Operação:", ["Soma", "Subtração", "Multiplicação", "Divisão"], horizontal=True)
    if st.button("Gerar Operações"):
        s = {"Soma":"+", "Subtração":"-", "Multiplicação":"x", "Divisão":"÷"}[tipo_op]
        qs = [f"{random.randint(10,999)} {s} {random.randint(10,99)} =" for _ in range(12)]
        st.session_state.preview_questoes = [".M1", f"t. Atividade de {tipo_op}", "1. Efetue os cálculos:"] + qs

elif menu == "eq":
    grau = st.radio("Grau:", ["1º Grau", "2º Grau"], horizontal=True)
    if st.button("Gerar Equações"):
        if grau == "1º Grau":
            qs = [f"{random.randint(2,10)}x {'+' if random.random()>0.5 else '-'} {random.randint(1,20)} = {random.randint(21,99)}" for _ in range(10)]
        else:
            qs = [f"x² {'-' if random.random()>0.5 else '+'} {random.randint(2,10)}x + {random.randint(1,16)} = 0" for _ in range(6)]
        st.session_state.preview_questoes = [".M1", f"t. Equações de {grau}", "1. Resolva as equações:"] + qs

elif menu == "sis":
    tipo_s = st.radio("Tipo:", ["Linear (1º Grau)", "Não Linear (2º Grau)"], horizontal=True)
    if st.button("Gerar Sistemas"):
        qs = []
        for _ in range(4):
            x, y = random.randint(1,10), random.randint(1,5)
            if "1º" in tipo_s: qs.append(f"{{ x + y = {x+y} \n  x - y = {x-y}")
            else: qs.append(f"{{ x + y = {x+y} \n  x . y = {x*y}")
        st.session_state.preview_questoes = [".M1", f"t. Sistemas", "1. Determine x e y:"] + qs

elif menu == "alg":
    tipo_a = st.radio("Álgebra:", ["Produtos Notáveis", "Fatoração"], horizontal=True)
    if st.button("Gerar Álgebra"):
        if "Produtos" in tipo_a:
            qs = [f"({random.randint(2,5)}x + {random.randint(1,9)})² =" for _ in range(6)]
        else:
            qs = ["x² - 36 =", "x² + 6x + 9 =", "4x² - 16 =", "(a + b)² ="]
        st.session_state.preview_questoes = [".M1", "t. Expressões Algébricas", "1. Desenvolva ou fatore:"] + qs

elif menu == "col":
    t_col = st.radio("Tema:", ["Radiciação", "Potenciação"], horizontal=True)
    if t_col == "Radiciação":
        m_r = st.selectbox("Raiz:", ["Quadrada", "Cúbica", "Misturada"])
        if st.button("Gerar Radiciação"):
            qs = []
            for _ in range(12):
                sel = m_r if m_r != "Misturada" else random.choice(["Quadrada", "Cúbica"])
                if sel == "Quadrada": qs.append(f"SQRT({random.randint(2,12)**2}) =")
                else: qs.append(f"CBRT({random.randint(2,5)**3}) =")
            st.session_state.preview_questoes = [".M1", "t. Radiciação", "1. Calcule:"] + qs

elif menu == "exp_num":
    if st.button("Gerar Expressões"):
        qs = [f"{random.randint(10,50)} + {random.randint(2,8)} x ({random.randint(10,20)} - {random.randint(1,5)}) =" for _ in range(8)]
        st.session_state.preview_questoes = [".M1", "t. Expressões Numéricas", "1. Calcule o valor:"] + qs

# --- 6. CALCULADORES ---
if menu == "calc_f":
    va = st.number_input("a", value=1.0); vb = st.number_input("b", value=-5.0); vc = st.number_input("c", value=6.0)
    if st.button("Calcular Bhaskara"):
        d = vb**2 - 4*va*vc
        if d >= 0: st.session_state.res_calc = f"Delta: {d} | x1: {(-vb+math.sqrt(d))/(2*va)} | x2: {(-vb-math.sqrt(d))/(2*va)}"
        else: st.session_state.res_calc = "Delta negativo."
    if st.session_state.res_calc: st.info(st.session_state.res_calc)

# --- 7. MOTOR PDF ---
if st.session_state.preview_questoes:
    st.subheader("Preview")
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