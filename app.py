import streamlit as st
import random
import re
import os
import math
from fpdf import FPDF  # Importação correta para fpdf2

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

# Persistência do perfil e menus
if 'perfil' not in st.session_state:
    st.session_state.perfil = None

if 'sub_menu' not in st.session_state:
    st.session_state.sub_menu = ""

if 'preview_questoes' not in st.session_state:
    st.session_state.preview_questoes = []

if 'res_calc' not in st.session_state:
    st.session_state.res_calc = ""

# --- 2. LOGIN (USANDO CHAVE_MESTRA E PIN) ---
def validar_acesso(pin):
    p_aluno = str(st.secrets.get("acesso_aluno", "123456")).strip()
    p_prof = str(st.secrets.get("chave_mestra", "chave_mestra")).strip().lower()
    if pin == p_prof: return "admin"
    if pin == p_aluno: return "aluno"
    return None

if st.session_state.perfil is None:
    st.title("🔐 Login Quantum")
    pin_input = st.text_input("Digite seu PIN de acesso:", type="password")
    if st.button("Acessar"):
        res = validar_acesso(pin_input)
        if res:
            st.session_state.perfil = res
            st.rerun()
        else:
            st.error("PIN Incorreto.")
    st.stop()

# --- 3. SIDEBAR ---
st.sidebar.title(f"🚀 {st.session_state.perfil.upper()}")
usar_cabecalho = st.sidebar.checkbox("Usar cabecalho.png", value=True)
recuo_cabecalho = st.sidebar.slider("Altura do Título (PDF):", 20, 80, 45)
layout_cols = st.sidebar.selectbox("Colunas no PDF:", [1, 2, 3], index=1)

if st.sidebar.button("🧹 Limpar Atividade"):
    st.session_state.preview_questoes = []
    st.session_state.res_calc = ""
    st.rerun()

# --- 4. CENTRO DE COMANDO (6 GERADORES + 3 CALCULADORES) ---
st.title("🛠️ Centro de Comando")
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

menu = st.session_state.sub_menu

# --- 5. LÓGICA DO MENU COLEGIAL (RADICIAÇÃO) ---
if menu == "col":
    tipo = st.radio("Escolha o tema:", ["Radiciação", "Potenciação", "Porcentagem"], horizontal=True)
    
    if tipo == "Radiciação":
        modo_raiz = st.selectbox("Tipo de Raiz:", ["Misturada", "Apenas Quadrada", "Apenas Cúbica"])
        if st.button("Gerar Atividade"):
            qs = []
            for _ in range(12):
                # Decide se é quadrada ou cúbica
                escolha = modo_raiz
                if modo_raiz == "Misturada":
                    escolha = random.choice(["Apenas Quadrada", "Apenas Cúbica"])
                
                if escolha == "Apenas Quadrada":
                    n = random.randint(2, 12)
                    qs.append(f"√{n**2} =")
                else:
                    n = random.randint(2, 5)
                    qs.append(f"³√{n**3} =")
            st.session_state.preview_questoes = [".M1", "t. Atividade de Radiciação", "1. Calcule as raízes abaixo:"] + qs

# (Aqui você pode incluir as lógicas de 'op', 'eq', 'sis', 'alg', 'man' seguindo o mesmo padrão)

# --- 6. CALCULADORES ---
if menu == "calc_f":
    a = st.number_input("a", value=1.0); b = st.number_input("b", value=-5.0); c = st.number_input("c", value=6.0)
    if st.button("Calcular"):
        delta = b**2 - 4*a*c
        if delta < 0: st.session_state.res_calc = "Delta negativo, não há raízes reais."
        else:
            x1 = (-b + math.sqrt(delta)) / (2*a)
            x2 = (-b - math.sqrt(delta)) / (2*a)
            st.session_state.res_calc = f"Delta: {delta} | x1: {x1} | x2: {x2}"
    if st.session_state.res_calc: st.success(st.session_state.res_calc)

# --- 7. MOTOR PDF ---
if st.session_state.preview_questoes:
    st.subheader("👁️ Preview da Atividade")
    with st.container(border=True):
        for line in st.session_state.preview_questoes:
            st.write(line)

    def export_pdf():
        pdf = FPDF()
        pdf.add_page()
        
        # Título e Cabeçalho
        y_pos = 10
        if usar_cabecalho and os.path.exists("cabecalho.png"):
            pdf.image("cabecalho.png", 10, 10, 190)
            y_pos = recuo_cabecalho
        pdf.set_y(y_pos)

        letras = "abcdefghijklmnopqrstuvwxyz"
        l_idx = 0
        larg_col = 190 / int(layout_cols)

        for line in st.session_state.preview_questoes:
            line = line.strip()
            if not line: continue

            # AJUSTE DE SÍMBOLOS PARA O PDF (Evita o erro UnicodeException)
            # Substituímos o símbolo real por um que a fonte padrão entenda ou por texto seguro
            line_pdf = line.replace('³√', '3v').replace('√', 'v').replace('²', '^2')

            if line.startswith(".M"):
                pdf.set_font("Helvetica", size=10)
                pdf.cell(190, 8, line[1:], ln=True)
            elif line.startswith("t."):
                pdf.set_font("Helvetica", 'B', 14)
                pdf.cell(190, 10, line[2:].strip(), ln=True, align='C')
            elif re.match(r'^\d+\.', line):
                pdf.set_font("Helvetica", 'B', 12)
                pdf.cell(190, 10, line, ln=True)
                l_idx = 0 # Reinicia letras para nova questão numérica
            else:
                pdf.set_font("Helvetica", size=12)
                col = l_idx % int(layout_cols)
                # Regra: linha posterior começa com letra
                item = f"{letras[l_idx % 26]}) {line_pdf}"
                pdf.cell(larg_col, 8, item, ln=(col == int(layout_cols)-1))
                l_idx += 1
        
        return bytes(pdf.output())

    st.download_button("📥 Baixar PDF", data=export_pdf(), file_name="atividade_quantum.pdf", mime="application/pdf")