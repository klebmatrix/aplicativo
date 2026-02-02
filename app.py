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
usar_cabecalho = st.sidebar.checkbox("Ativar cabeçalho", value=True)
layout_cols = st.sidebar.selectbox("Colunas PDF:", [1, 2, 3], index=1)
if st.sidebar.button("🧹 Limpar Tudo"):
    st.session_state.preview_questoes = []; st.session_state.res_calc = ""; st.rerun()
if st.sidebar.button("🚪 Sair"):
    st.session_state.clear(); st.rerun()

# --- 4. CENTRO DE COMANDO ---
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

if menu == "col":
    t_col = st.radio("Tema:", ["Radiciação", "Potenciação", "Porcentagem"], horizontal=True)
    if t_col == "Radiciação":
        m_r = st.selectbox("Raiz:", ["Quadrada", "Cúbica", "Misturada"])
        if st.button("Gerar Radiciação"):
            qs = []
            for _ in range(12):
                sel = m_r if m_r != "Misturada" else random.choice(["Quadrada", "Cúbica"])
                if sel == "Quadrada": qs.append(f"SQRT({random.randint(2,12)**2}) =")
                else: qs.append(f"CBRT({random.randint(2,5)**3}) =")
            st.session_state.preview_questoes = [".M1", "t. Radiciação", "1. Calcule:"] + qs
    elif t_col == "Porcentagem":
        if st.button("Gerar Porcentagem"):
            qs = [f"{random.choice([5,10,15,20,25,50])}% de {random.randint(100, 1000)} =" for _ in range(10)]
            st.session_state.preview_questoes = [".M1", "t. Porcentagem", "1. Calcule os valores:"] + qs
    else: # Potenciação
        if st.button("Gerar Potenciação"):
            qs = [f"{random.randint(2,15)}² =" for _ in range(12)]
            st.session_state.preview_questoes = [".M1", "t. Potenciação", "1. Calcule as potências:"] + qs

elif menu == "op":
    tipo_op = st.radio("Operação:", ["Soma", "Subtração", "Multiplicação", "Divisão"], horizontal=True)
    if st.button("Gerar Operações"):
        s = {"Soma":"+", "Subtração":"-", "Multiplicação":"x", "Divisão":"÷"}[tipo_op]
        qs = [f"{random.randint(10,999)} {s} {random.randint(10,99)} =" for _ in range(12)]
        st.session_state.preview_questoes = [".M1", f"t. {tipo_op}", "1. Calcule:"] + qs

# --- 6. CALCULADORES ONLINE ---
if menu == "fin":
    st.subheader("Calculadora Financeira (Juros Simples)")
    cap = st.number_input("Capital (R$):", value=1000.0)
    tax = st.number_input("Taxa (% ao mês):", value=2.0)
    tem = st.number_input("Tempo (meses):", value=12)
    if st.button("Calcular Juros"):
        j = cap * (tax/100) * tem
        st.session_state.res_calc = f"Juros: R$ {j:.2f} | Total: R$ {cap + j:.2f}"

if menu == "calc_f":
    va = st.number_input("a", value=1.0); vb = st.number_input("b", value=-5.0); vc = st.number_input("c", value=6.0)
    if st.button("Calcular Bhaskara"):
        d = vb**2 - 4*va*vc
        if d >= 0: st.session_state.res_calc = f"Delta: {d} | x1: {(-vb+math.sqrt(d))/(2*va)} | x2: {(-vb-math.sqrt(d))/(2*va)}"
        else: st.session_state.res_calc = "Delta negativo (sem raízes reais)."

if st.session_state.res_calc:
    st.info(st.session_state.res_calc)

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