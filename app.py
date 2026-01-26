import streamlit as st
import os
import numpy as np
from cryptography.fernet import Fernet
from fpdf import FPDF
import random
import math

# --- 1. SEGURANÇA E AMBIENTE ---
# PIN de 6 dígitos [cite: 2026-01-19] entre 6 e 8 caracteres [cite: 2026-01-21]
PIN_CRIPTOGRAFADO = "gAAAAABpdRRwrtzON4oc6ayd3fx1LjLjX8TjRj7riCkHHuOpi0lcYFAu04KEXEo8d3-GJz9HmpP-AjvbLOLzr6zC6GMUvOCP1A=="

def validar_acesso(pin_digitado):
    senha_aluno_env = os.environ.get('acesso_aluno')
    if senha_aluno_env and pin_digitado == senha_aluno_env:
        return "aluno"
    try:
        chave = os.environ.get('chave_mestra') # [cite: 2026-01-24]
        if not chave: return "erro_env"
        chave = chave.strip().replace("'", "").replace('"', "").replace('b', '', 1) if chave.startswith('b') else chave.strip()
        f = Fernet(chave.encode())
        if pin_digitado == f.decrypt(PIN_CRIPTOGRAFADO.strip().encode()).decode():
            return "admin"
    except: pass
    return "negado"

def contar_divisores(n):
    if n <= 0: return 0
    return len([i for i in range(1, n + 1) if n % i == 0])

st.set_page_config(page_title="Quantum Math Lab", layout="wide")
if 'perfil' not in st.session_state: st.session_state.perfil = None

# --- 2. MOTOR DE PDF ---
def gerar_material_pdf(titulo, questoes, respostas):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"Atividade: {titulo}", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    for q in questoes:
        pdf.multi_cell(0, 10, txt=q); pdf.ln(5)
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Gabarito Oficial", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    for r in respostas:
        pdf.multi_cell(0, 10, txt=r); pdf.ln(2)
    return pdf.output(dest='S').encode('latin-1')

# --- 3. LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Quantum Math Lab")
    pin = st.text_input("Digite o PIN:", type="password")
    if st.button("Entrar"):
        acesso = validar_acesso(pin)
        if acesso != "negado":
            st.session_state.perfil = acesso
            st.rerun()
        else: st.error("PIN incorreto.")
    st.stop()

# --- 4. ÁREA ADMIN (PROFESSOR) ---
elif st.session_state.perfil == "admin":
    st.sidebar.title("🛠 Painel Professor")
    menu = st.sidebar.radio("Navegação", [
        "Gerador de Listas", "Expressões Matemáticas", "Funções Aritméticas", 
        "Logaritmos", "Matrizes (Sarrus)", "Sistemas Lineares", 
        "Álgebra e Geometria", "Financeiro", "Pasta Professor"
    ])
    st.sidebar.button("Sair", on_click=lambda: st.session_state.update({"perfil": None}))

    # EXPRESSÕES MATEMÁTICAS (PEMDAS/BODMAS)
    if menu == "Expressões Matemáticas":
        st.header("🧮 Calculadora de Expressões")
        expr_input = st.text_input("Expressão (use ^ para potência e sqrt para raiz):", value="(2+3)*5^2", key="ex_in")
        if st.button("Calcular"):
            try:
                limpo = expr_input.replace('^', '**')
                res = eval(limpo, {"__builtins__": None}, {"math": math, "sqrt": math.sqrt})
                st.success(f"Resultado: {res}")
            except Exception as e: st.error(f"Erro: {e}")

    # FUNÇÕES ARITMÉTICAS
    elif menu == "Funções Aritméticas":
        st.header("🔍 Função Divisor f(n)")
        n_val = st.number_input("Número n:", min_value=1, value=12, key="fn_n")
        if st.button("Analisar"):
            d_count = contar_divisores(n_val)
            st.success(f"f({n_val}) = {d_count}")
            st.write(f"Divisores: {[i for i in range(1, n_val+1) if n_val%i==0]}")

    # LOGARITMOS
    elif menu == "Logaritmos":
        st.header("🔢 Logaritmos")
        c1, c2 = st.columns(2)
        la = c1.number_input("Logaritmando:", min_value=0.1, value=100.0, key="log_a")
        lb = c2.number_input("Base:", min_value=0.1, value=10.0, key="log_b")
        if st.button("Calcular Log"):
            st.success(f"Resultado: {math.log(la, lb):.4f}")

    # MATRIZES
    elif menu == "Matrizes (Sarrus)":
        st.header("🧮 Determinante e Inversa")
        ordem = st.selectbox("Ordem:", [2, 3], key="m_ord")
        mat = []
        for i in range(ordem):
            cols = st.columns(ordem)
            mat.append([cols[j].number_input(f"A{i+1}{j+1}", value=float(i==j), key=f"mat_{i}_{j}") for j in range(ordem)])
        if st.button("Calcular Matriz"):
            A = np.array(mat)
            det = np.linalg.det(A)
            st.write(f"Determinante: {det:.2f}")
            if abs(det) > 0.0001: st.write("Inversa:", np.linalg.inv(A))

    # SISTEMAS
    elif menu == "Sistemas Lineares":
        st.header("📏 Sistema Ax = B")
        osys = st.selectbox("Equações:", [2, 3], key="s_ord")
        mA, vB = [], []
        for i in range(osys):
            cols = st.columns(osys + 1)
            mA.append([cols[j].number_input(f"A{i}{j}", value=float(i==j), key=f"sA{i}{j}") for j in range(osys)])
            vB.append(cols[osys].number_input(f"B{i}", value=1.0, key=f"sB{i}"))
        if st.button("Resolver"):
            try: st.success(f"X = {np.linalg.solve(np.array(mA), np.array(vB))}")
            except: st.error("Erro no sistema.")

    # ÁLGEBRA E GEOMETRIA
    elif menu == "Álgebra e Geometria":
        st.subheader("🔍 Bhaskara e Pitágoras")
        c1, c2, c3 = st.columns(3)
        va = c1.number_input("a", 1.0, key="ba"); vb = c2.number_input("b", -5.0, key="bb"); vc = c3.number_input("c", 6.0, key="bc")
        if st.button("Calcular Bhaskara"):
            d = vb**2 - 4*va*vc
            if d >= 0: st.write(f"x1: {(-vb+np.sqrt(d))/(2*va):.2f}, x2: {(-vb-np.sqrt(d))/(2*va):.2f}")
            else: st.error("Delta < 0")
        st.divider()
        p1 = st.number_input("Cateto A", 3.0, key="pa"); p2 = st.number_input("Cateto B", 4.0, key="pb")
        if st.button("Calcular Pitágoras"): st.success(f"H = {np.sqrt(p1**2 + p2**2):.2f}")

    # FINANCEIRO
    elif menu == "Financeiro":
        st.header("💰 Juros Compostos")
        c1, c2, c3 = st.columns(3)
        cap = c1.number_input("Capital:", 1000.0, key="fc")
        txa = c2.number_input("Taxa (%):", 1.0, key="fi") / 100
        tme = c3.number_input("Tempo:", 12, key="ft")
        if st.button("Calcular Montante"):
            st.metric("Total", f"R$ {cap*(1+txa)**tme:.2f}")

    # GERADOR
    elif menu == "Gerador de Listas":
        st.header("📝 Gerador PDF")
        tema = st.selectbox("Tema:", ["Geral", "Financeiro", "Matrizes"])
        if st.button("Gerar 10 Questões"):
            pdf_data = gerar_material_pdf(tema, ["Questão 1..."], ["Gabarito 1..."])
            st.download_button("Baixar PDF", pdf_data, "atividade.pdf")

    # DRIVE
    elif menu == "Pasta Professor":
        st.link_button("Abrir Google Drive", "COLE_LINK_AQUI")