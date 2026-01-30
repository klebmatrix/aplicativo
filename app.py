import streamlit as st
import random
import re
import os
from fpdf import FPDF

# --- 1. CONFIGURAÇÃO E ESTADO ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

if 'perfil' not in st.session_state: st.session_state.perfil = None
if 'preview_questoes' not in st.session_state: st.session_state.preview_questoes = []
if 'sub_menu' not in st.session_state: st.session_state.sub_menu = None

# --- 2. LOGIN (Secrets Render) ---
def validar_acesso(pin_digitado):
    senha_aluno = str(st.secrets.get("acesso_aluno", "123456")).strip()
    senha_prof = str(st.secrets.get("chave_mestra", "chave_mestra")).strip().lower()
    if pin_digitado == senha_aluno: return "aluno"
    elif pin_digitado == senha_prof: return "admin"
    return "negado"

if st.session_state.perfil is None:
    st.title("🔐 Login")
    pin = st.text_input("PIN de Acesso:", type="password")
    if st.button("Entrar"):
        acesso = validar_acesso(pin)
        if acesso != "negado":
            st.session_state.perfil = acesso
            st.rerun()
        else: st.error("PIN incorreto.")
    st.stop()

# --- 3. SIDEBAR ---
st.sidebar.title(f"🚀 {'Professor' if st.session_state.perfil == 'admin' else 'Estudante'}")
usar_cabecalho = st.sidebar.checkbox("Incluir Cabeçalho", value=True)
incluir_gabarito = st.sidebar.checkbox("Gerar Gabarito", value=False)
layout_colunas = st.sidebar.selectbox("Colunas no PDF:", [1, 2, 3], index=1)

if st.sidebar.button("🚪 Sair / Logout"):
    st.session_state.clear()
    st.rerun()

# --- 4. PAINEL DE CONTROLE (BOTÕES) ---
st.title("🛠️ Painel de Controle")
st.subheader("📝 Geradores de PDF")
g1, g2, g3, g4, g5 = st.columns(5)
if g1.button("🔢 Operações", use_container_width=True): st.session_state.sub_menu = "op"
if g2.button("📐 Equações", use_container_width=True): st.session_state.sub_menu = "eq"
if g3.button("📚 Colegial", use_container_width=True): st.session_state.sub_menu = "col"
if g4.button("⚖️ Álgebra", use_container_width=True): st.session_state.sub_menu = "alg"
if g5.button("📄 Manual", use_container_width=True): st.session_state.sub_menu = "man"

st.subheader("🧮 Ferramentas de Cálculo")
c1, c2, c3 = st.columns(3)
if c1.button("𝑓(x) Funções", use_container_width=True): st.session_state.sub_menu = "calc_f"
if c2.button("📊 PEMDAS", use_container_width=True): st.session_state.sub_menu = "pemdas"
if c3.button("💰 Financeira", use_container_width=True): st.session_state.sub_menu = "fin"

menu = st.session_state.sub_menu
st.divider()

# --- 5. LÓGICA DE CADA BOTÃO ---
if menu == "op":
    st.header("🔢 Operações Automáticas")
    n_ini = st.number_input("Iniciar no nº:", value=6)
    if st.button("Gerar Operações"):
        st.session_state.preview_questoes = [".M1", "t. OPERAÇÕES", f"{n_ini}. Calcule:"] + \
            [f"{random.randint(10,999)} {random.choice(['+', '-', 'x'])} {random.randint(10,99)} =" for _ in range(12)]
        st.rerun()

elif menu == "eq":
    st.header("📐 Equações")
    grau = st.radio("Grau:", ["1º Grau", "2º Grau"])
    if st.button("Gerar Equações"):
        qs = [f"{random.randint(2,9)}x + {random.randint(1,20)} = {random.randint(21,99)}" for _ in range(8)]
        st.session_state.preview_questoes = [".M1", f"t. EQUAÇÕES {grau}", "6. Resolva:"] + qs
        st.rerun()

elif menu == "col":
    st.header("📚 Temas Colegial")
    tema = st.selectbox("Tema:", ["Logaritmos", "Matrizes", "Trigonometria"])
    if st.button("Gerar Atividade"):
        st.session_state.preview_questoes = [".M1", f"t. {tema.upper()}", "6. Resolva os problemas:"] + \
            [f"Problema de {tema} nível {i+1} =" for i in range(5)]
        st.rerun()

elif menu == "alg":
    st.header("⚖️ Álgebra")
    if st.button("Gerar Álgebra"):
        st.session_state.preview_questoes = [".M1", "t. ÁLGEBRA", "6. Simplifique as expressões:"] + \
            ["(2x + 3y)^2 =", "3x(x - 4) + 2x^2 =", "a^2 - b^2 ="]
        st.rerun()

elif menu == "man":
    st.header("📄 Modo Manual")
    txt = st.text_area("Digite linha por linha:")
    if st.button("Aplicar"):
        st.session_state.preview_questoes = txt.split('\n')
        st.rerun()

elif menu == "calc_f":
    st.header("𝑓(x) Calculadora de Funções")
    f_expr = st.text_input("Função (ex: 2*x + 5):", "x**2 - 4")
    x_val = st.number_input("Valor de x:", value=0.0)
    if st.button("Calcular"):
        res = eval(f_expr.replace('x', f'({x_val})'))
        st.success(f"f({x_val}) = {res}")

elif menu == "pemdas":
    st.header("📊 Expressões PEMDAS")
    exp_p = st.text_input("Expressão:", "2 + 3 * (4**2)")
    if st.button("Resolver"):
        st.info(f"Resultado: {eval(exp_p)}")

elif menu == "fin":
    st.header("💰 Financeira")
    capital = st.number_input("Capital:", 1000.0)
    taxa = st.number_input("Taxa (% a.m):", 1.0)
    if st.button("Calcular Juros (1 ano)"):
        st.metric("Montante Final", f"R$ {capital * (1 + taxa/100)**12:.2f}")

# --- 6. PDF ENGINE ---
if st.session_state.preview_questoes:
    st.divider()
    st.subheader("👁️ Preview")
    for l in st.session_state.preview_questoes: st.text(l)

    def export_pdf():
        try:
            pdf = FPDF()
            pdf.add_page()
            y_pos = 10
            if usar_cabecalho and os.path.exists("cabecalho.png"):
                pdf.image("cabecalho.png", 10, 10, 190)
                y_pos = 65
            pdf.set_y(y_pos)
            letras, l_idx = "abcdefghijklmnopqrstuvwxyz", 0
            n_cols = int(layout_colunas)
            larg_col = 190 / n_cols
            
            for line in st.session_state.preview_questoes:
                line = line.strip()
                if not line: continue
                if line.lower().startswith("t."):
                    pdf.set_font("Helvetica", 'B', 14)
                    pdf.cell(190, 10, line[2:].strip(), ln=True, align='C')
                    l_idx = 0
                elif line.startswith(".M"):
                    pdf.set_font("Helvetica", 'B', 12)
                    pdf.cell(190, 10, line[1:], ln=True, align='L')
                    l_idx = 0
                elif re.match(r'^\d+\.', line):
                    pdf.set_font("Helvetica", size=12)
                    pdf.cell(190, 10, line, ln=True, align='L')
                    l_idx = 0
                else:
                    pdf.set_font("Helvetica", size=12)
                    col = l_idx % n_cols
                    pdf.cell(larg_col, 8, f"{letras[l_idx%26]}) {line.lstrip('. ')}", align='L', ln=(col == n_cols-1))
                    l_idx += 1
            return pdf.output(dest='S').encode('latin-1')
        except: return b""

    st.download_button("📥 Baixar PDF", data=export_pdf(), file_name="atividade.pdf")