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
    st.title("🔐 Login")
    pin_input = st.text_input("PIN:", type="password")
    if st.button("Acessar"):
        res = validar_acesso(pin_input)
        if res: st.session_state.perfil = res; st.rerun()
        else: st.error("PIN Incorreto")
    st.stop()

# --- 3. SIDEBAR ---
st.sidebar.title(f"🚀 {st.session_state.perfil.upper()}")
usar_cabecalho = st.sidebar.checkbox("Ativar Cabeçalho", value=True)
layout_cols = st.sidebar.selectbox("Colunas PDF:", [1, 2, 3], index=1)
if st.sidebar.button("🧹 Limpar Tudo"):
    st.session_state.preview_questoes = []; st.session_state.res_calc = ""; st.rerun()

# --- 4. CENTRO DE COMANDO ---
st.title("🛠️ Centro de Comando Quantum")
g1, g2, g3, g4, g5, g6 = st.columns(6)
if g1.button("🔢 Operações"): st.session_state.sub_menu = "op"
if g2.button("📐 Equações"): st.session_state.sub_menu = "eq"
if g3.button("⛓️ Sistemas"): st.session_state.sub_menu = "sis"
if g4.button("⚖️ Álgebra"): st.session_state.sub_menu = "alg"
if g5.button("🎓 Colegial"): st.session_state.sub_menu = "col"
if g6.button("📄 Manual"): st.session_state.sub_menu = "man"

st.write("---")
c1, c2, c3 = st.columns(3)
if c1.button("𝑓(x) Bhaskara"): st.session_state.sub_menu = "calc_f"
if c2.button("📊 PEMDAS"): st.session_state.sub_menu = "pemdas"
if c3.button("💰 Financeira"): st.session_state.sub_menu = "fin"

st.divider()
menu = st.session_state.sub_menu

# --- 5. LÓGICA DE OPERAÇÕES (CONSERTADA) ---
if menu == "op":
    st.subheader("🔢 Operações Básicas")
    t_op = st.radio("Escolha a Operação:", ["Soma", "Subtração", "Multiplicação", "Divisão"], horizontal=True)
    if st.button("Gerar Atividade de Operações"):
        if t_op == "Soma":
            qs = [f"{random.randint(100, 999)} + {random.randint(100, 999)} =" for _ in range(12)]
        elif t_op == "Subtração":
            qs = [f"{random.randint(500, 999)} - {random.randint(10, 499)} =" for _ in range(12)]
        elif t_op == "Multiplicação":
            qs = [f"{random.randint(10, 99)} x {random.randint(2, 9)} =" for _ in range(12)]
        else: # Divisão
            qs = []
            for _ in range(12):
                divisor = random.randint(2, 9)
                quociente = random.randint(10, 50)
                dividendo = divisor * quociente
                qs.append(f"{dividendo} ÷ {divisor} =")
        st.session_state.preview_questoes = [".M1", f"t. Atividade de {t_op}", "1. Resolva as operações abaixo:"] + qs

# --- 6. LÓGICA DO COLEGIAL ---
elif menu == "col":
    st.subheader("🎓 Módulo Colegial")
    t_col = st.radio("Tema:", ["Radiciação", "Potenciação", "Porcentagem"], horizontal=True)
    if t_col == "Radiciação":
        g_raiz = st.radio("Tipo:", ["Quadrada", "Cúbica"], horizontal=True)
        if st.button("Gerar Radiciação"):
            if g_raiz == "Quadrada": qs = [f"SQRT({random.randint(2,15)**2}) =" for _ in range(10)]
            else: qs = [f"3v({random.randint(2,10)**3}) =" for _ in range(10)]
            st.session_state.preview_questoes = [".M1", f"t. Radicacao {g_raiz}", "1. Calcule:"] + qs
    elif t_col == "Potenciação":
        e_pot = st.selectbox("Expoente:", [2, 3, 4])
        if st.button("Gerar Potenciação"):
            qs = [f"{random.randint(2,12)}^{e_pot} =" for _ in range(10)]
            st.session_state.preview_questoes = [".M1", f"t. Potenciacao (Exp {e_pot})", "1. Calcule:"] + qs
    elif t_col == "Porcentagem":
        if st.button("Gerar Porcentagem"):
            qs = [f"{random.randint(1,15)*5}% de {random.randint(10,100)*10} =" for _ in range(10)]
            st.session_state.preview_questoes = [".M1", "t. Porcentagem", "1. Calcule:"] + qs

# --- 7. CALCULADORES ---
elif menu == "calc_f":
    a_v = st.number_input("a", value=1.0); b_v = st.number_input("b", value=-5.0); c_v = st.number_input("c", value=6.0)
    if st.button("Calcular Bhaskara"):
        delta = b_v**2 - 4*a_v*c_v
        if delta >= 0:
            st.success(f"Delta: {delta} | x1: {(-b_v+math.sqrt(delta))/(2*a_v):.2f} | x2: {(-b_v-math.sqrt(delta))/(2*a_v):.2f}")
        else: st.error("Delta negativo.")

elif menu == "pemdas":
    exp_txt = st.text_input("Expressão (PEMDAS):")
    if st.button("Resolver Expressão"):
        try: st.success(f"Resultado: {eval(exp_txt.replace('x','*').replace(',','.'))}")
        except: st.error("Erro na conta.")

elif menu == "fin":
    cap = st.number_input("Capital", value=1000.0); taxa = st.number_input("Taxa %", value=10.0); meses = st.number_input("Meses", value=12)
    if st.button("Calcular Juros Simples"):
        st.success(f"Juros: R$ {cap*(taxa/100)*meses:.2f}")

# --- 8. MOTOR PDF ---
if st.session_state.preview_questoes:
    st.divider()
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