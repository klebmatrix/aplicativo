import streamlit as st
import random
import re
import os
import math
from fpdf import FPDF

# --- 1. CONFIGURAÇÃO E PERSISTÊNCIA ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

for key in ['perfil', 'sub_menu', 'preview_questoes', 'res_calc']:
    if key not in st.session_state:
        st.session_state[key] = [] if key == 'preview_questoes' else ""

# --- 2. LOGIN (Secrets Render) ---
def validar_acesso(pin):
    p_aluno = str(st.secrets.get("acesso_aluno", "123456")).strip()
    p_prof = str(st.secrets.get("chave_mestra", "chave_mestra")).strip().lower()
    return "admin" if pin == p_prof else "aluno" if pin == p_aluno else None

if not st.session_state.perfil:
    st.title("🔐 Login")
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
usar_cabecalho = st.sidebar.checkbox("Usar cabecalho.png", value=True)
recuo_cabecalho = st.sidebar.slider("Altura do Título:", 20, 80, 45)
layout_cols = st.sidebar.selectbox("Colunas PDF:", [1, 2, 3], index=1)

if st.sidebar.button("🧹 Limpar Atividade", use_container_width=True):
    st.session_state.preview_questoes = []; st.session_state.res_calc = ""; st.rerun()

if st.sidebar.button("🚪 Sair / Logout", use_container_width=True):
    st.session_state.clear(); st.rerun()

# --- 4. CENTRO DE COMANDO (AGORA COM OS 6 GERADORES) ---
st.title("🛠️ Centro de Comando Quantum")
g1, g2, g3, g4, g5, g6 = st.columns(6)
if g1.button("🔢 Operações"): st.session_state.sub_menu = "op"
if g2.button("📐 Equações"): st.session_state.sub_menu = "eq"
if g3.button("⛓️ Sistemas"): st.session_state.sub_menu = "sis"
if g4.button("⚖️ Álgebra"): st.session_state.sub_menu = "alg"
if g5.button("🎓 Colegial"): st.session_state.sub_menu = "col" # REINSTALADO
if g6.button("📄 Manual"): st.session_state.sub_menu = "man"

c1, c2, c3 = st.columns(3)
if c1.button("𝑓(x) Bhaskara"): st.session_state.sub_menu = "calc_f"
if c2.button("📊 PEMDAS"): st.session_state.sub_menu = "pemdas"
if c3.button("💰 Financeira"): st.session_state.sub_menu = "fin"

st.divider()
menu = st.session_state.sub_menu

# --- 5. LÓGICAS DOS GERADORES ---
if menu == "op":
    tipo = st.radio("Escolha:", ["Soma", "Subtração", "Multiplicação", "Divisão"], horizontal=True)
    if st.button("Gerar Atividade"):
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

elif menu == "sis":
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

elif menu == "col":
    tipo = st.radio("Tema:", ["Radiciação", "Potenciação", "Porcentagem"], horizontal=True)
    if st.button("Gerar Colegial"):
        if tipo == "Radiciação":
            qs = [f"SQRT({random.randint(2,12)**2}) =" for _ in range(10)]
        elif tipo == "Porcentagem":
            qs = [f"{random.randint(1,10)*5}% de {random.randint(10,100)*10} =" for _ in range(10)]
        else:
            qs = [f"{random.randint(2,15)}² =" for _ in range(10)]
        st.session_state.preview_questoes = [".M1", f"t. {tipo}", "1. Calcule:"] + qs

elif menu == "man":
    txt = st.text_area("Texto Manual:")
    if st.button("Aplicar"): st.session_state.preview_questoes = txt.split("\n")

# --- 6. CALCULADORES ---
elif menu == "calc_f":
    a = st.number_input("a", value=1.0); b = st.number_input("b", value=-5.0); c = st.number_input("c", value=6.0)
    if st.button("Calcular"):
        d = b**2 - 4*a*c
        if d >= 0: st.session_state.res_calc = f"Delta: {d} | x1: {(-b+math.sqrt(d))/(2*a):.2f} | x2: {(-b-math.sqrt(d))/(2*a):.2f}"
        else: st.session_state.res_calc = "Delta negativo."

elif menu == "pemdas":
    exp = st.text_input("Expressão:", "20 / (2+3) * 4")
    if st.button("Resolver"):
        try: st.session_state.res_calc = f"Resultado: {eval(exp.replace('x','*'))}"
        except: st.error("Erro na expressão.")

elif menu == "fin":
    cap = st.number_input("Capital", value=1000.0); tax = st.number_input("Taxa (%)", value=10.0); tmp = st.number_input("Meses", value=12)
    if st.button("Calcular Juros"):
        j = cap * (tax/100) * tmp
        st.session_state.res_calc = f"Juros: R$ {j:.2f} | Total: R$ {cap + j:.2f}"

if st.session_state.res_calc: st.success(st.session_state.res_calc)

# --- 7. MOTOR PDF ---
if st.session_state.preview_questoes:
    st.subheader("👁️ Preview")
    for l in st.session_state.preview_questoes: st.write(l.replace("SQRT", "√"))

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
                pdf.set_font("Helvetica", 'B', 12); pdf.cell(190, 10, line, ln=True); l_idx = 0
            else:
                col = l_idx % int(layout_cols)
                pdf.set_font("Helvetica", size=12)
                pdf.write(8, f"{letras[l_idx%26]}) ")
                if "SQRT" in line:
                    pdf.set_font("Symbol", size=12); pdf.write(8, chr(214))
                    pdf.set_font("Helvetica", size=12); pdf.write(8, line.replace("SQRT(","").replace(")",""))
                else:
                    pdf.write(8, line.encode('latin-1', 'replace').decode('latin-1'))
                l_idx += 1
                if col == int(layout_cols)-1: pdf.ln(12)
                else: pdf.set_x(pdf.get_x() + (larg_col - 40))
        return pdf.output()

    st.download_button("📥 Baixar PDF", data=export_pdf(), file_name="atividade.pdf", mime="application/pdf")