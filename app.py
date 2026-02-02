import streamlit as st
import random
import re
import os
import math
from fpdf import FPDF

# --- 1. CONFIGURAÇÃO E ESTADOS ---
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

# --- 3. SIDEBAR (MENU DO PROFESSOR) ---
st.sidebar.title(f"🚀 {st.session_state.perfil.upper()}")
usar_cabecalho = st.sidebar.checkbox("Usar cabeçalho (cabecalho.png)", value=True)
recuo_cabecalho = st.sidebar.slider("Altura Título PDF:", 20, 80, 45)
layout_cols = st.sidebar.selectbox("Número de Colunas:", [1, 2, 3], index=1)

if st.sidebar.button("🧹 Limpar Atividade"):
    st.session_state.preview_questoes = []; st.session_state.res_calc = ""; st.rerun()

if st.sidebar.button("🚪 Sair"):
    st.session_state.clear()
    st.rerun()

# --- 4. CENTRO DE COMANDO (6 GERADORES EM CIMA) ---
st.title("🛠️ Centro de Comando Quantum")
g1, g2, g3, g4, g5, g6 = st.columns(6)
if g1.button("🔢 Operações", use_container_width=True): st.session_state.sub_menu = "op"
if g2.button("📐 Equações", use_container_width=True): st.session_state.sub_menu = "eq"
if g3.button("⛓️ Sistemas", use_container_width=True): st.session_state.sub_menu = "sis"
if g4.button("⚖️ Álgebra", use_container_width=True): st.session_state.sub_menu = "alg"
if g5.button("🎓 Colegial", use_container_width=True): st.session_state.sub_menu = "col"
if g6.button("📄 Manual", use_container_width=True): st.session_state.sub_menu = "man"

st.write("---")

# (3 CALCULADORES EMBAIXO)
c1, c2, c3 = st.columns(3)
if c1.button("𝑓(x) Bhaskara", use_container_width=True): st.session_state.sub_menu = "calc_f"
if c2.button("📊 PEMDAS", use_container_width=True): st.session_state.sub_menu = "pemdas"
if c3.button("💰 Financeira", use_container_width=True): st.session_state.sub_menu = "fin"

menu = st.session_state.sub_menu

# --- 5. LÓGICAS DOS GERADORES ---
if menu == "op":
    tipo = st.radio("Tipo:", ["Soma", "Subtração", "Multiplicação", "Divisão"], horizontal=True)
    if st.button("Gerar"):
        s = {"Soma": "+", "Subtração": "-", "Multiplicação": "x", "Divisão": "÷"}[tipo]
        qs = [f"{random.randint(10, 99)} {s} {random.randint(10, 99)} =" for _ in range(12)]
        st.session_state.preview_questoes = [".M1", f"t. {tipo}", "1. Calcule:"] + qs

elif menu == "col":
    tipo_col = st.radio("Tema:", ["Radiciação", "Potenciação", "Porcentagem"], horizontal=True)
    if tipo_col == "Radiciação":
        modo = st.selectbox("Raiz:", ["Quadrada", "Cúbica", "Misturada"])
        if st.button("Gerar Radiciação"):
            qs = []
            for _ in range(12):
                m = modo if modo != "Misturada" else random.choice(["Quadrada", "Cúbica"])
                if m == "Quadrada": qs.append(f"SQRT({random.randint(2, 12)**2}) =")
                else: qs.append(f"CBRT({random.randint(2, 5)**3}) =")
            st.session_state.preview_questoes = [".M1", "t. Radiciação", "1. Resolva as raízes:"] + qs

elif menu == "man":
    txt = st.text_area("Texto livre (Use .M para margem e t. para título):")
    if st.button("Aplicar"): st.session_state.preview_questoes = txt.split("\n")

# --- 6. CALCULADORES ONLINE ---
if menu == "calc_f":
    va = st.number_input("a", value=1.0); vb = st.number_input("b", value=-5.0); vc = st.number_input("c", value=6.0)
    if st.button("Calcular"):
        d = vb**2 - 4*va*vc
        if d >= 0: st.session_state.res_calc = f"Delta: {d} | x1: {(-vb+math.sqrt(d))/(2*va)} | x2: {(-vb-math.sqrt(d))/(2*va)}"
        else: st.session_state.res_calc = "Delta negativo (sem raízes reais)."

elif menu == "pemdas":
    exp = st.text_input("Expressão:", "2 + 3 * 4")
    if st.button("Resolver"):
        try: st.session_state.res_calc = f"Resultado: {eval(exp)}"
        except: st.session_state.res_calc = "Erro na expressão."

if st.session_state.res_calc: st.info(st.session_state.res_calc)

# --- 7. MOTOR PDF COM SÍMBOLOS REAIS ---
if st.session_state.preview_questoes:
    st.subheader("👁️ Preview")
    for line in st.session_state.preview_questoes:
        st.write(line.replace("SQRT", "√").replace("CBRT", "∛"))

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
                pdf.set_font("Helvetica", size=10); pdf.cell(190, 8, line[1:], ln=True)
            elif line.startswith("t."):
                pdf.set_font("Helvetica", 'B', 14); pdf.cell(190, 10, line[2:].strip(), ln=True, align='C')
            elif re.match(r'^\d+\.', line):
                pdf.set_font("Helvetica", 'B', 12); pdf.cell(190, 10, line, ln=True); l_idx = 0
            else:
                # Regra de letras a), b), c)
                col = l_idx % int(layout_cols)
                pdf.set_font("Helvetica", size=12)
                pdf.write(8, f"{letras[l_idx%26]}) ")
                
                # SÍMBOLO DA RAIZ REAL
                if "SQRT" in line:
                    pdf.set_font("Symbol", size=12); pdf.write(8, chr(214))
                    pdf.set_font("Helvetica", size=12); pdf.write(8, line.replace("SQRT(", "").replace(")", ""))
                elif "CBRT" in line:
                    pdf.set_font("Helvetica", size=8); pdf.write(8, "3")
                    pdf.set_font("Symbol", size=12); pdf.write(8, chr(214))
                    pdf.set_font("Helvetica", size=12); pdf.write(8, line.replace("CBRT(", "").replace(")", ""))
                else:
                    pdf.set_font("Helvetica", size=12); pdf.write(8, line)
                
                l_idx += 1
                if col == int(layout_cols) - 1: pdf.ln(10)
                else: pdf.set_x(pdf.get_x() + (larg_col - 35))
        
        return bytes(pdf.output())

    st.download_button("📥 Baixar PDF", data=export_pdf(), file_name="atividade.pdf", mime="application/pdf")