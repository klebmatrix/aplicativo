import streamlit as st
import os
import numpy as np
import plotly.express as px
from cryptography.fernet import Fernet
from fpdf import FPDF
import random
import math

# --- 1. SEGURANÇA (Render) ---
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
        # PIN entre 6 e 8 caracteres [cite: 2026-01-21]
        if pin_digitado == f.decrypt(PIN_CRIPTOGRAFADO.strip().encode()).decode():
            return "admin"
    except: pass
    return "negado"

def contar_divisores(n):
    if n <= 0: return 0
    return len([i for i in range(1, n + 1) if n % i == 0])

st.set_page_config(page_title="Quantum Math Lab", layout="wide")
if 'perfil' not in st.session_state: st.session_state.perfil = None

# --- MOTOR DE PDF ---
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

# --- LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Quantum Math Lab")
    # Acesso via PIN de 6 dígitos [cite: 2026-01-19]
    pin = st.text_input("Digite o PIN:", type="password")
    if st.button("Entrar"):
        acesso = validar_acesso(pin)
        if acesso != "negado":
            st.session_state.perfil = acesso
            st.rerun()
        else: st.error("PIN incorreto.")
    st.stop()

# --- ÁREA DO ALUNO ---
if st.session_state.perfil == "aluno":
    st.title("🎓 Portal do Aluno")
    st.sidebar.button("Sair", on_click=lambda: st.session_state.update({"perfil": None}))
    st.link_button("📂 Abrir Pasta de Exercícios", "COLE_LINK_ALUNO_AQUI")

# --- ÁREA DO PROFESSOR (ADMIN) ---
elif st.session_state.perfil == "admin":
    st.sidebar.title("🛠 Painel Professor")
    menu = st.sidebar.radio("Navegação", ["Gerador de Listas", "Logaritmos", "Matrizes (Inversa/Sarrus)", "Funções (Divisores)", "Sistemas Lineares", "Álgebra/Geometria", "Financeiro", "Pasta Professor"])
    st.sidebar.button("Sair", on_click=lambda: st.session_state.update({"perfil": None}))

    # 1. NOVO MÓDULO: LOGARITMOS
    if menu == "Logaritmos":
        st.header("🔢 Calculadora de Logaritmos")
        st.latex(r"\log_{b}(a) = x \iff b^x = a")
        col1, col2 = st.columns(2)
        log_a = col1.number_input("Logaritmando (a):", min_value=0.1, value=100.0)
        log_b = col2.number_input("Base (b):", min_value=0.1, value=10.0)
        if st.button("Calcular Log"):
            try:
                res_log = math.log(log_a, log_b)
                st.success(f"Log de {log_a} na base {log_b} é: {res_log:.4f}")
            except: st.error("Erro no cálculo (verifique a base).")

    # 2. GERADOR DE LISTAS ATUALIZADO
    elif menu == "Gerador de Listas":
        st.header("📝 Gerador Multidisciplinar")
        tema = st.selectbox("Escolha o Tema:", ["Logaritmos", "Matriz Inversa", "Funções (Divisores)", "Equações 1º Grau"])
        if st.button("🚀 Gerar 10 Questões"):
            qs, gs = [], []
            for i in range(1, 11):
                if tema == "Logaritmos":
                    base = random.choice([2, 3, 5, 10])
                    exp = random.randint(2, 4)
                    qs.append(f"{i}) Calcule o valor de log de {base**exp} na base {base}.")
                    gs.append(f"{i}) Resposta: {exp}")
                elif tema == "Matriz Inversa":
                    v = random.randint(1, 4)
                    qs.append(f"{i}) Determine a inversa de A = [[{v}, 0, 0], [0, {v+1}, 0], [0, 0, 1]].")
                    gs.append(f"{i}) Det = {v*(v+1)}")
                elif tema == "Funções (Divisores)":
                    n = random.randint(12, 60)
                    qs.append(f"{i}) Determine f({n}), onde f(n) e o numero de divisores de n.")
                    gs.append(f"{i}) f({n}) = {contar_divisores(n)}")
                elif tema == "Equações 1º Grau":
                    a, x = random.randint(2, 5), random.randint(2, 10)
                    qs.append(f"{i}) Resolva: {a}x + {random.randint(1,10)} = {(a*x)+random.randint(1,10)}")
                    gs.append(f"{i}) x aproximado")
            
            pdf_data = gerar_material_pdf(tema, qs, gs)
            st.download_button("📥 Baixar PDF", pdf_data, f"quantum_{tema.lower()}.pdf")

    # 3. MATRIZES
    elif menu == "Matrizes (Inversa/Sarrus)":
        st.header("🧮 Sarrus e Inversa")
        ordem = st.selectbox("Ordem:", [2, 3], key="ordem_m")
        mat_M = []
        for i in range(ordem):
            cols = st.columns(ordem)
            mat_M.append([cols[j].number_input(f"A{i+1}{j+1}", value=float(i==j), key=f"v_{i}{j}") for j in range(ordem)])
        if st.button("Calcular"):
            A = np.array(mat_M)
            det = np.linalg.det(A)
            st.write(f"Determinante: {det:.2f}")
            if abs(det) > 0.0001: st.write("Inversa:", np.linalg.inv(A))

    # 4. OUTROS (Resumidos para evitar quebra)
    elif menu == "Funções (Divisores)":
        n = st.number_input("n:", min_value=1, value=12)
        if st.button("Calcular f(n)"): st.success(f"f({n}) = {contar_divisores(n)}")

    elif menu == "Pasta Professor":
        st.link_button("🚀 Abrir Drive Admin", "COLE_LINK_PROFESSOR_AQUI")