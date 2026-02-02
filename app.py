import streamlit as st
import random
import re
import os
import math
from fpdf import FPDF

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

# Inicialização de estados
for key in ['perfil', 'sub_menu', 'preview_questoes', 'res_calc']:
    if key not in st.session_state:
        st.session_state[key] = [] if key == 'preview_questoes' else ""

# --- 2. LOGIN ---
def validar_acesso(pin):
    p_aluno = str(st.secrets.get("acesso_aluno", "123456")).strip()
    p_prof = str(st.secrets.get("chave_mestra", "chave_mestra")).strip().lower()
    if pin == p_prof: return "admin"
    if pin == p_aluno: return "aluno"
    return None

if not st.session_state.perfil:
    st.title("🔐 Login Quantum")
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
usar_cabecalho = st.sidebar.checkbox("Usar cabeçalho", value=True)
recuo_cabecalho = st.sidebar.slider("Altura Título:", 20, 80, 45)
layout_cols = st.sidebar.selectbox("Colunas:", [1, 2, 3], index=1)

if st.sidebar.button("🧹 Limpar Tudo"):
    st.session_state.preview_questoes = []
    st.session_state.res_calc = ""
    st.rerun()

# --- 4. CENTRO DE COMANDO (6+3) ---
st.title("🛠️ Centro de Comando")
g1, g2, g3, g4, g5, g6 = st.columns(6)
if g1.button("🔢 Operações", use_container_width=True): st.session_state.sub_menu = "op"
if g2.button("📐 Equações", use_container_width=True): st.session_state.sub_menu = "eq"
if g3.button("⛓️ Sistemas", use_container_width=True): st.session_state.sub_menu = "sis"
if g4.button("⚖️ Álgebra", use_container_width=True): st.session_state.sub_menu = "alg"
if g5.button("🎓 Colegial", use_container_width=True): st.session_state.sub_menu = "col"
if g6.button("📄 Manual", use_container_width=True): st.session_state.sub_menu = "man"

st.write("---")
c1, c2, c3 = st.columns(3)
if c1.button("𝑓(x) Bhaskara", use_container_width=True): st.session_state.sub_menu = "calc_f"
if c2.button("📊 PEMDAS", use_container_width=True): st.session_state.sub_menu = "pemdas"
if c3.button("💰 Financeira", use_container_width=True): st.session_state.sub_menu = "fin"

menu = st.session_state.sub_menu

# --- 5. LÓGICAS DOS CALCULADORES (CORRIGIDAS) ---
if menu == "calc_f":
    st.subheader("Calculadora de Bhaskara")
    col_a, col_b, col_c = st.columns(3)
    va = col_a.number_input("a", value=1.0)
    vb = col_b.number_input("b", value=-5.0)
    vc = col_c.number_input("c", value=6.0)
    if st.button("Calcular Raízes"):
        delta = vb**2 - 4*va*vc
        if delta < 0: st.session_state.res_calc = f"Delta: {delta} (Sem raízes reais)"
        else:
            x1 = (-vb + math.sqrt(delta))/(2*va)
            x2 = (-vb - math.sqrt(delta))/(2*va)
            st.session_state.res_calc = f"Delta: {delta} | x1: {x1} | x2: {x2}"

elif menu == "pemdas":
    st.subheader("Calculadora PEMDAS")
    exp = st.text_input("Expressão (use * para multiplicar):", "2 + 3 * (10/2)")
    if st.button("Resolver"):
        try: st.session_state.res_calc = f"Resultado: {eval(exp)}"
        except: st.session_state.res_calc = "Erro na expressão!"

elif menu == "fin":
    st.subheader("Juros Simples")
    cap = st.number_input("Capital:", value=1000.0)
    tax = st.number_input("Taxa (% ao mês):", value=2.0)
    tem = st.number_input("Meses:", value=12)
    if st.button("Calcular Montante"):
        juros = cap * (tax/100) * tem
        st.session_state.res_calc = f"Juros: R$ {juros:.2f} | Total: R$ {cap + juros:.2f}"

# Exibe o resultado do cálculo se houver
if st.session_state.res_calc:
    st.info(st.session_state.res_calc)

# --- 6. LÓGICA COLEGIAL ---
if menu == "col":
    tipo = st.radio("Tema:", ["Radiciação", "Potenciação"], horizontal=True)
    if tipo == "Radiciação":
        modo = st.selectbox("Tipo:", ["Quadrada", "Cúbica", "Misturada"])
        if st.button("Gerar Questoes"):
            qs = []
            for _ in range(12):
                m = modo if modo != "Misturada" else random.choice(["Quadrada", "Cúbica"])
                if m == "Quadrada":
                    n = random.randint(2, 12)
                    qs.append(f"sqrt({n**2}) =")
                else:
                    n = random.randint(2, 5)
                    qs.append(f"cbrt({n**3}) =")
            st.session_state.preview_questoes = [".M1", "t. Atividade de Radiciação", "1. Resolva:"] + qs

# --- 7. MOTOR PDF ---
if st.session_state.preview_questoes:
    st.subheader("Preview")
    for line in st.session_state.preview_questoes:
        st.write(line.replace("sqrt", "√").replace("cbrt", "∛"))

    def export_pdf():
        pdf = FPDF()
        pdf.add_page()
        y = 10
        if usar_cabecalho and os.path.exists("cabecalho.png"):
            pdf.image("cabecalho.png", 10, 10, 190)
            y = recuo_cabecalho
        pdf.set_y(y)
        
        letras = "abcdefghijklmnopqrstuvwxyz"
        l_idx = 0
        larg = 190 / int(layout_cols)
        
        for line in st.session_state.preview_questoes:
            line = line.strip()
            if not line: continue
            
            # Limpeza para evitar erro de Unicode no PDF
            # Usamos nomes que o PDF entende 100%
            line_pdf = line.replace("sqrt", "raiz").replace("cbrt", "raiz cubica")
            
            if line.startswith(".M"):
                pdf.set_font("Helvetica", size=10); pdf.cell(190, 8, line[1:], ln=True)
            elif line.startswith("t."):
                pdf.set_font("Helvetica", 'B', 14); pdf.cell(190, 10, line[2:], ln=True, align='C')
            elif re.match(r'^\d+\.', line):
                pdf.set_font("Helvetica", 'B', 12); pdf.cell(190, 10, line, ln=True); l_idx = 0
            else:
                pdf.set_font("Helvetica", size=12)
                col = l_idx % int(layout_cols)
                txt = f"{letras[l_idx%26]}) {line_pdf}"
                pdf.cell(larg, 8, txt, ln=(col == int(layout_cols)-1))
                l_idx += 1
        return bytes(pdf.output())

    st.download_button("📥 Baixar PDF", data=export_pdf(), file_name="quantum.pdf")