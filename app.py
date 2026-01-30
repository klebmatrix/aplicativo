import streamlit as st
import random
import re
import os
import math
from fpdf import FPDF

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

if 'perfil' not in st.session_state: st.session_state.perfil = None
if 'sub_menu' not in st.session_state: st.session_state.sub_menu = None
if 'preview_questoes' not in st.session_state: st.session_state.preview_questoes = []

# --- 2. LOGIN (Secrets Render) ---
def validar_acesso(pin):
    p_aluno = str(st.secrets.get("acesso_aluno", "123456")).strip()
    p_prof = str(st.secrets.get("chave_mestra", "chave_mestra")).strip().lower()
    return "admin" if pin == p_prof else "aluno" if pin == p_aluno else None

if st.session_state.perfil is None:
    st.title("🔐 Login")
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

if st.sidebar.button("🧹 Limpar Tudo", use_container_width=True):
    st.session_state.preview_questoes = []; st.session_state.sub_menu = None; st.rerun()

if st.sidebar.button("🚪 Sair", use_container_width=True):
    st.session_state.clear(); st.rerun()

# --- 4. PAINEL COM 8 BOTÕES ---
st.title("🛠️ Centro de Comando")
g1, g2, g3, g4, g5 = st.columns(5)
if g1.button("🔢 Operações"): st.session_state.sub_menu = "op"
if g2.button("📐 Equações"): st.session_state.sub_menu = "eq"
if g3.button("📚 Colegial"): st.session_state.sub_menu = "col"
if g4.button("⚖️ Álgebra"): st.session_state.sub_menu = "alg"
if g5.button("📄 Manual"): st.session_state.sub_menu = "man"

c1, c2, c3 = st.columns(3)
if c1.button("𝑓(x) Funções"): st.session_state.sub_menu = "calc_f"
if c2.button("📊 PEMDAS"): st.session_state.sub_menu = "pemdas"
if c3.button("💰 Financeira"): st.session_state.sub_menu = "fin"

st.divider()
menu = st.session_state.sub_menu

# --- LÓGICAS DE GERAÇÃO ---
if menu == "op":
    n = st.number_input("Início:", value=6)
    if st.button("Gerar"):
        st.session_state.preview_questoes = [".M1", "t. OPERAÇÕES", f"{n}. Resolva:"] + \
            [f"{random.randint(10,99)} + {random.randint(10,99)} =" for _ in range(12)]
        st.rerun()

elif menu == "eq":
    n = st.number_input("Início:", value=6)
    if st.button("Gerar"):
        st.session_state.preview_questoes = [".M1", "t. EQUAÇÕES", f"{n}. Ache o x:"] + \
            [f"{random.randint(2,9)}x = {random.randint(10,90)}" for _ in range(10)]
        st.rerun()

elif menu == "col":
    n = st.number_input("Início:", value=6)
    if st.button("Gerar"):
        st.session_state.preview_questoes = [".M1", "t. POTÊNCIAS", f"{n}. Calcule:"] + \
            [f"{random.randint(2,10)}^2 =" for _ in range(10)]
        st.rerun()

elif menu == "alg":
    n = st.number_input("Início:", value=6)
    if st.button("Gerar"):
        st.session_state.preview_questoes = [".M1", "t. ÁLGEBRA", f"{n}. Simplifique:"] + ["(x+1)^2 =", "(x-2)^2 =", "x(x+3) ="]
        st.rerun()

elif menu == "man":
    txt = st.text_area("Manual:")
    if st.button("Aplicar"): st.session_state.preview_questoes = txt.split("\n"); st.rerun()

elif menu == "calc_f":
    a = st.number_input("a", value=1.0)
    b = st.number_input("b", value=-5.0)
    c = st.number_input("c", value=6.0)
    if st.button("Calcular"):
        d = b**2 - 4*a*c
        if d >= 0: st.success(f"x1: {(-b+math.sqrt(d))/(2*a)} | x2: {(-b-math.sqrt(d))/(2*a)}")

elif menu == "pemdas":
    exp = st.text_input("Expressão:", "10 / 2 + 5")
    if st.button("Resolver"): st.write(f"Res: {eval(exp)}")

elif menu == "fin":
    cap = st.number_input("Capital", value=1000.0)
    if st.button("Calcular"): st.write(f"Total (+10%): {cap * 1.1}")

# --- 5. MOTOR PDF (SOMENTE IMAGEM NO TOPO) ---
if st.session_state.preview_questoes:
    st.divider()
    def export_pdf():
        pdf = FPDF()
        pdf.add_page()
        y_pos = 10
        
        # Pega a imagem da pasta e coloca no topo
        if usar_cabecalho and os.path.exists("cabecalho.png"):
            pdf.image("cabecalho.png", x=10, y=10, w=190)
            y_pos = 65 
        
        pdf.set_y(y_pos)
        letras, l_idx = "abcdefghijklmnopqrstuvwxyz", 0
        n_cols = int(layout_cols)
        larg_col = 190 / n_cols
        
        for line in st.session_state.preview_questoes:
            line = line.strip()
            if not line: continue
            
            if line.startswith(".M"):
                pdf.set_font("Helvetica", 'B', 12); pdf.cell(190, 10, line[1:], ln=True)
            elif line.lower().startswith("t."):
                pdf.set_font("Helvetica", 'B', 14); pdf.cell(190, 10, line[2:].strip().upper(), ln=True, align='C')
            elif re.match(r'^\d+\.', line): # Linha começa com número
                pdf.set_font("Helvetica", size=12); pdf.cell(190, 10, line, ln=True); l_idx = 0
            else: # Linha vira letra (a, b, c) automaticamente
                pdf.set_font("Helvetica", size=12)
                col = l_idx % n_cols
                pdf.cell(larg_col, 8, f"{letras[l_idx%26]}) {line.lstrip('. ')}", ln=(col == n_cols-1))
                l_idx += 1
        return pdf.output(dest='S').encode('latin-1')

    st.download_button("📥 Baixar PDF", data=export_pdf(), file_name="atividade.pdf")