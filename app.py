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

# --- 3. SIDEBAR ---
st.sidebar.title(f"🚀 {st.session_state.perfil.upper()}")
usar_cabecalho = st.sidebar.checkbox("Usar cabecalho.png", value=True)
layout_cols = st.sidebar.selectbox("Colunas PDF:", [1, 2, 3], index=1)
if st.sidebar.button("🧹 Limpar Atividade"):
    st.session_state.preview_questoes = []; st.session_state.res_calc = ""; st.rerun()
if st.sidebar.button("🚪 Sair"):
    st.session_state.clear(); st.rerun()

# --- 4. CENTRO DE COMANDO (TODOS OS 8 BOTÕES) ---
st.title("🛠️ Centro de Comando Quantum")
g1, g2, g3, g4, g5, g6 = st.columns(6)
if g1.button("🔢 Operações"): st.session_state.sub_menu = "op"
if g2.button("📐 Equações"): st.session_state.sub_menu = "eq"
if g3.button("⛓️ Sistemas"): st.session_state.sub_menu = "sis"
if g4.button("⚖️ Álgebra"): st.session_state.sub_menu = "alg"
if g5.button("🎓 Colegial"): st.session_state.sub_menu = "col" # NOVO
if g6.button("📄 Manual"): st.session_state.sub_menu = "man"

st.write("")
c1, c2, c3 = st.columns(3)
if c1.button("𝑓(x) Bhaskara"): st.session_state.sub_menu = "calc_f"
if c2.button("📊 Exp. Numéricas"): st.session_state.sub_menu = "pemdas"
if c3.button("💰 Financeira"): st.session_state.sub_menu = "fin"

st.divider()
menu = st.session_state.sub_menu

# --- 5. LÓGICAS DOS GERADORES ---
if menu == "op":
    tipo = st.radio("Escolha:", ["Soma", "Subtração", "Multiplicação", "Divisão"], horizontal=True)
    if st.button("Gerar Operações"):
        s = {"Soma": "+", "Subtração": "-", "Multiplicação": "x", "Divisão": "÷"}[tipo]
        qs = [f"{random.randint(10, 999)} {s} {random.randint(10, 99)} =" for _ in range(12)]
        st.session_state.preview_questoes = [".M1", f"t. Atividade de {tipo}", "1. Calcule:"] + qs

elif menu == "eq":
    tipo = st.radio("Grau:", ["1º Grau", "2º Grau"], horizontal=True)
    if st.button("Gerar Equações"):
        if tipo == "1º Grau":
            qs = [f"{random.randint(2,10)}x {'+' if random.random()>0.5 else '-'} {random.randint(1,20)} = {random.randint(21,99)}" for _ in range(8)]
        else:
            qs = [f"x² {'-' if random.random()>0.5 else '+'} {random.randint(2,10)}x + {random.randint(1,16)} = 0" for _ in range(5)]
        st.session_state.preview_questoes = [".M1", f"t. Equações de {tipo}", "1. Resolva:"] + qs

elif menu == "col":
    tipo = st.radio("Tema:", ["Radiciação", "Potenciação", "Porcentagem"], horizontal=True)
    if st.button("Gerar Colegial"):
        if tipo == "Radiciação":
            qs = [f"SQRT({random.randint(2,12)**2}) =" for _ in range(10)]
            st.session_state.preview_questoes = [".M1", "t. Radiciação", "1. Calcule:"] + qs
        elif tipo == "Porcentagem":
            qs = [f"{random.randint(1,10)*5}% de {random.randint(10,100)*10} =" for _ in range(10)]
            st.session_state.preview_questoes = [".M1", "t. Porcentagem", "1. Calcule:"] + qs
        else:
            qs = [f"{random.randint(2,15)}² =" for _ in range(10)]
            st.session_state.preview_questoes = [".M1", "t. Potenciação", "1. Calcule:"] + qs

elif menu == "man":
    txt = st.text_area("Texto Manual:")
    if st.button("Aplicar Manual"): st.session_state.preview_questoes = txt.split("\n")

# --- 6. CALCULADORES ---
elif menu == "calc_f":
    va = st.number_input("a", value=1.0); vb = st.number_input("b", value=-5.0); vc = st.number_input("c", value=6.0)
    if st.button("Calcular Bhaskara"):
        d = vb**2 - 4*va*vc
        if d >= 0: st.session_state.res_calc = f"Delta: {d} | x1: {(-vb+math.sqrt(d))/(2*va):.2f} | x2: {(-vb-math.sqrt(d))/(2*va):.2f}"
        else: st.session_state.res_calc = "Delta negativo."

elif menu == "fin":
    cap = st.number_input("Capital", 100.0); tax = st.number_input("Taxa %", 1.0); tmp = st.number_input("Meses", 1)
    if st.button("Calcular Juros"):
        j = cap * (tax/100) * tmp
        st.session_state.res_calc = f"Juros: R$ {j:.2f} | Total: R$ {cap+j:.2f}"

if st.session_state.res_calc: st.success(st.session_state.res_calc)

# --- 7. MOTOR PDF COM SÍMBOLO DE RAIZ ---
if st.session_state.preview_questoes:
    st.subheader("👁️ Preview")
    for line in st.session_state.preview_questoes:
        st.write(line.replace("SQRT", "√"))

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
                pdf.set_font("Helvetica", size=11); pdf.cell(190, 8, line[1:], ln=True)
            elif line.lower().startswith("t."):
                pdf.set_font("Helvetica", 'B', 14); pdf.cell(190, 10, line[2:].strip(), ln=True, align='C')
            elif re.match(r'^\d+\.', line):
                pdf.set_font("Helvetica", 'B', 12); pdf.cell(190, 10, line, ln=True); l_idx = 0
            else:
                col = l_idx % int(layout_cols)
                pdf.set_font("Helvetica", size=12)
                pdf.write(8, f"{letras[l_idx%26]}) ")
                if "SQRT" in line:
                    pdf.set_font("Symbol", size=12); pdf.write(8, chr(214)) # Símbolo √
                    pdf.set_font("Helvetica", size=12); pdf.write(8, line.replace("SQRT(","").replace(")",""))
                else:
                    pdf.write(8, line)
                l_idx += 1
                if col == int(layout_cols)-1: pdf.ln(10)
                else: pdf.set_x(pdf.get_x() + (larg_col - 35))
        return pdf.output(dest='S').encode('latin-1')

    st.download_button("📥 Baixar PDF", data=export_pdf(), file_name="atividade.pdf")