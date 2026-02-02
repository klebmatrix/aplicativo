import streamlit as st
import random
import re
import os
import math
from fpdf import FPDF  # fpdf2 também usa esse comando de importação

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
if st.sidebar.button("🚪 Sair", use_container_width=True):
    st.session_state.clear(); st.rerun()
st.sidebar.divider()
usar_cabecalho = st.sidebar.checkbox("Ativar Cabeçalho", value=True)
layout_cols = st.sidebar.selectbox("Colunas PDF:", [1, 2, 3], index=1)

# --- 4. CENTRO DE COMANDO (ATIVIDADES) ---
st.title("🛠️ Centro de Comando Quantum")
g1, g2, g3, g4, g5, g6 = st.columns(6)
if g1.button("🔢 Operações"): st.session_state.sub_menu = "op"
if g2.button("📐 Equações"): st.session_state.sub_menu = "eq"
if g3.button("⛓️ Sistemas"): st.session_state.sub_menu = "sis"
if g4.button("⚖️ Álgebra"): st.session_state.sub_menu = "alg"
if g5.button("🎓 Colegial"): st.session_state.sub_menu = "col"
if g6.button("📄 Manual"): st.session_state.sub_menu = "man"

st.write("---")
# --- OS 3 CALCULADORES (SOLICITADOS) ---
st.subheader("🧮 Calculadores em Tempo Real")
c1, c2, c3 = st.columns(3)
if c1.button("𝑓(x) Bhaskara"): st.session_state.sub_menu = "calc_f"
if c2.button("📊 PEMDAS"): st.session_state.sub_menu = "pemdas"
if c3.button("💰 Financeira"): st.session_state.sub_menu = "fin"

st.divider()
menu = st.session_state.sub_menu

# --- 5. LÓGICAS DOS CALCULADORES ---
if menu == "calc_f":
    st.subheader("𝑓(x) Bhaskara")
    col1, col2, col3 = st.columns(3)
    ca = col1.number_input("a", value=1.0)
    cb = col2.number_input("b", value=-5.0)
    cc = col3.number_input("c", value=6.0)
    if st.button("Calcular Agora"):
        delta = cb**2 - 4*ca*cc
        if delta >= 0:
            x1 = (-cb + math.sqrt(delta)) / (2*ca)
            x2 = (-cb - math.sqrt(delta)) / (2*ca)
            st.success(f"Delta: {delta} | x1: {x1:.2f} | x2: {x2:.2f}")
        else: st.error(f"Delta: {delta} (Sem raízes reais)")

elif menu == "pemdas":
    st.subheader("📊 PEMDAS / Expressões")
    exp_in = st.text_input("Digite a conta (ex: 10 + 5 * 2):")
    if st.button("Resolver"):
        try:
            res = eval(exp_in.replace('x', '*').replace(',', '.'))
            st.success(f"Resultado: {res}")
        except: st.error("Expressão inválida.")

elif menu == "fin":
    st.subheader("💰 Juros Simples")
    cap = st.number_input("Capital", value=1000.0)
    tax = st.number_input("Taxa (%)", value=5.0)
    tmp = st.number_input("Meses", value=12)
    if st.button("Calcular Financeira"):
        j = cap * (tax/100) * tmp
        st.success(f"Juros: R$ {j:.2f} | Total: R$ {cap+j:.2f}")

# --- 6. LÓGICAS DAS ATIVIDADES ---
elif menu == "eq":
    t_eq = st.radio("Grau:", ["1º Grau", "2º Grau"], horizontal=True)
    if st.button("Gerar Equações"):
        if t_eq == "1º Grau": qs = [f"{random.randint(2,10)}x + {random.randint(1,20)} = {random.randint(21,99)}" for _ in range(8)]
        else: qs = [f"x² - {random.randint(2,12)}x + {random.randint(1,20)} = 0" for _ in range(5)]
        st.session_state.preview_questoes = [".M1", f"t. Equações {t_eq}", "1. Resolva:"] + qs

elif menu == "sis":
    t_sis = st.radio("Tipo:", ["1º Grau", "2º Grau"], horizontal=True)
    if st.button("Gerar Sistemas"):
        if t_sis == "1º Grau": qs = [f"{{ x + y = {random.randint(10,30)} \n  {{ x - y = {random.randint(2,10)}" for _ in range(4)]
        else: qs = [f"{{ x + y = {random.randint(5,15)} \n  x * y = {random.randint(6,50)}" for _ in range(3)]
        st.session_state.preview_questoes = [".M1", f"t. Sistemas {t_sis}", "1. Resolva:"] + qs

elif menu == "col":
    t_col = st.radio("Tema:", ["Radiciação", "Potenciação", "Porcentagem"], horizontal=True)
    if t_col == "Radiciação":
        g_r = st.radio("Raiz:", ["Quadrada", "Cúbica"], horizontal=True)
        if st.button("Gerar Radic."):
            qs = [f"SQRT({random.randint(2,15)**2}) =" for _ in range(10)] if g_r == "Quadrada" else [f"3v({random.randint(2,10)**3}) =" for _ in range(10)]
            st.session_state.preview_questoes = [".M1", f"t. Radicacao {g_r}", "1. Calcule:"] + qs
    elif t_col == "Potenciação":
        ex_p = st.selectbox("Expoente:", [2, 3, 4])
        if st.button("Gerar Potênc."):
            qs = [f"{random.randint(2,12)}^{ex_p} =" for _ in range(10)]
            st.session_state.preview_questoes = [".M1", f"t. Potenciacao (Exp {ex_p})", "1. Calcule:"] + qs
    else:
        if st.button("Gerar Porcent."):
            qs = [f"{random.randint(1,15)*5}% de {random.randint(10,100)*10} =" for _ in range(10)]
            st.session_state.preview_questoes = [".M1", "t. Porcentagem", "1. Resolva:"] + qs

elif menu == "man":
    txt = st.text_area("Digite as questões (uma por linha):")
    if st.button("Aplicar"): st.session_state.preview_questoes = txt.split("\n")

elif menu == "op":
    t_o = st.radio("Operação:", ["Soma", "Subtração", "Multiplicação", "Divisão"], horizontal=True)
    if st.button("Gerar Ops"):
        if t_o == "Soma": qs = [f"{random.randint(100,999)} + {random.randint(100,999)} =" for _ in range(12)]
        elif t_o == "Subtração": qs = [f"{random.randint(500,999)} - {random.randint(10,499)} =" for _ in range(12)]
        elif t_o == "Multiplicação": qs = [f"{random.randint(10,99)} x {random.randint(2,9)} =" for _ in range(12)]
        else: qs = [f"{random.randint(10,50)*d} ÷ {d} =" for d in [random.randint(2,9) for _ in range(12)]]
        st.session_state.preview_questoes = [".M1", f"t. {t_o}", "1. Calcule:"] + qs

# --- 7. MOTOR PDF ---
if st.session_state.preview_questoes:
    st.divider()
    st.subheader("👁️ Preview")
    for l in st.session_state.preview_questoes: st.write(l.replace("SQRT", "√"))
    
    def export_pdf():
        pdf = FPDF()
        pdf.add_page()
        if usar_cabecalho and os.path.exists("cabecalho.png"):
            pdf.image("cabecalho.png", 10, 10, 190); pdf.set_y(55)
        else: pdf.set_y(15)
        letras = "abcdefghijklmnopqrstuvwxyz"; l_idx = 0; larg_col = 190 / int(layout_cols)
        for line in st.session_state.preview_questoes:
            line = line.strip()
            if not line: continue
            if line.startswith(".M"): pdf.set_font("Arial", size=10); pdf.cell(190, 8, line[1:], ln=True)
            elif line.lower().startswith("t."): pdf.set_font("Arial", 'B', 14); pdf.cell(190, 10, line[2:].strip(), ln=True, align='C')
            elif re.match(r'^\d+\.', line): pdf.set_font("Arial", 'B', 12); pdf.cell(190, 10, line, ln=True); l_idx = 0
            else:
                pdf.set_font("Arial", size=12)
                txt = f"{letras[l_idx%26]}) {line}".encode('latin-1', 'ignore').decode('latin-1')
                pdf.cell(larg_col, 8, txt, ln=(l_idx % int(layout_cols) == int(layout_cols)-1)); l_idx += 1
        return bytes(pdf.output())

    st.download_button("📥 Baixar PDF", data=export_pdf(), file_name="atividade.pdf", mime="application/pdf")