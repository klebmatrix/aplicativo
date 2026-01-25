import streamlit as st
import os
import numpy as np
import plotly.express as px
from cryptography.fernet import Fernet
from fpdf import FPDF
import random

# --- 1. SEGURANÇA ---
PIN_CRIPTOGRAFADO = "gAAAAABpdRRwrtzON4oc6ayd3fx1LjLjX8TjRj7riCkHHuOpi0lcYFAu04KEXEo8d3-GJz9HmpP-AjvbLOLzr6zC6GMUvOCP1A=="

def validar_acesso(pin_digitado):
    senha_aluno_env = os.environ.get('acesso_aluno')
    if senha_aluno_env and pin_digitado == senha_aluno_env:
        return "aluno"
    try:
        chave = os.environ.get('chave_mestra')
        if not chave: return "erro_env"
        chave = chave.strip().replace("'", "").replace('"', "").replace('b', '', 1) if chave.startswith('b') else chave.strip()
        f = Fernet(chave.encode())
        if pin_digitado == f.decrypt(PIN_CRIPTOGRAFADO.strip().encode()).decode():
            return "admin"
    except: pass
    return "negado"

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
    pin = st.text_input("Digite o PIN:", type="password")
    if st.button("Entrar"):
        acesso = validar_acesso(pin)
        if acesso != "negado":
            st.session_state.perfil = acesso
            st.rerun()
        else: st.error("PIN incorreto.")
    st.stop()

# --- TELA DO ALUNO ---
if st.session_state.perfil == "aluno":
    st.title("🎓 Portal do Aluno")
    st.sidebar.button("Sair", on_click=lambda: st.session_state.update({"perfil": None}))
    st.info("Acesse a pasta de atividades oficial no Google Drive abaixo:")
    link_drive = "https://drive.google.com/drive/folders/COLE_SEU_LINK_AQUI"
    st.link_button("📂 Abrir Pasta de Exercícios", link_drive)

# --- TELA DO PROFESSOR (ADMIN COMPLETO REATIVADO) ---
elif st.session_state.perfil == "admin":
    st.sidebar.title("🛠 Painel Professor")
    menu = st.sidebar.radio("Navegação", ["Gerador de Listas", "Sistemas Lineares", "Álgebra (Bhaskara)", "Geometria (Pitágoras)", "Financeiro"])
    st.sidebar.button("Sair", on_click=lambda: st.session_state.update({"perfil": None}))

    if menu == "Gerador de Listas":
        st.header("📝 Criador de Exercícios Profissionais")
        tema = st.selectbox("Escolha o Tema:", ["Equações 1º Grau", "Teorema de Pitágoras"])
        if st.button("🚀 Gerar 10 Questões + Gabarito"):
            qs, gs = [], []
            for i in range(1, 11):
                if "1º Grau" in tema:
                    a, x, b = random.randint(2, 6), random.randint(1, 15), random.randint(1, 20)
                    res = (a * x) + b
                    qs.append(f"{i}) Encontre o valor de x: {a}x + {b} = {res}")
                    gs.append(f"{i}) x = {x}")
                else:
                    ca, cb = random.randint(3, 9), random.randint(4, 12)
                    h = np.sqrt(ca**2 + cb**2)
                    qs.append(f"{i}) Catetos medindo {ca} e {cb}. Calcule a hipotenusa.")
                    gs.append(f"{i}) H = {h:.2f}")
            pdf_data = gerar_material_pdf(tema, qs, gs)
            st.success("Lista Gerada! Baixe e coloque na sua pasta do Google Drive.")
            st.download_button("📥 Baixar PDF", pdf_data, "atividade_quantum.pdf")

    elif menu == "Sistemas Lineares":
        st.header("📏 Sistemas Ax = B")
        st.latex(r"Ax = B")
        ordem = st.selectbox("Ordem do Sistema:", [2, 3])
        mat_A, vec_B = [], []
        for i in range(ordem):
            cols = st.columns(ordem + 1)
            mat_A.append([cols[j].number_input(f"A{i+1},{j+1}", value=float(i==j), key=f"A{i}{j}") for j in range(ordem)])
            vec_B.append(cols[ordem].number_input(f"B{i+1}", value=1.0, key=f"B{i}"))
        if st.button("Resolver Sistema"):
            try:
                A, B = np.array(mat_A), np.array(vec_B)
                sol = np.linalg.solve(A, B)
                st.divider()
                st.write("### Solução:")
                for idx, s in enumerate(sol): st.write(f"x{idx+1} = `{s:.4f}`")
                st.plotly_chart(px.imshow(A, text_auto=True, color_continuous_scale='Viridis'))
            except: st.error("O sistema não possui uma única solução.")

    elif menu == "Álgebra (Bhaskara)":
        st.header("🔍 Calculadora de Equações de 2º Grau")
        st.latex(r"ax^2 + bx + c = 0")
        c1, c2, c3 = st.columns(3)
        va = c1.number_input("Coeficiente a", 1.0)
        vb = c2.number_input("Coeficiente b", -5.0)
        vc = c3.number_input("Coeficiente c", 6.0)
        if st.button("Calcular Raízes"):
            delta = vb**2 - 4*va*vc
            if delta >= 0:
                x1 = (-vb + np.sqrt(delta)) / (2*va)
                x2 = (-vb - np.sqrt(delta)) / (2*va)
                st.success(f"Delta = {delta} | x1 = {x1:.2f} | x2 = {x2:.2f}")
            else: st.error("Raízes Complexas!")

    elif menu == "Geometria (Pitágoras)":
        st.header("📐 Teorema de Pitágoras")
        st.latex(r"a^2 + b^2 = c^2")
        ca = st.number_input("Cateto A", 3.0)
        cb = st.number_input("Cateto B", 4.0)
        if st.button("Calcular Hipotenusa"):
            st.success(f"Hipotenusa (c) = {np.sqrt(ca**2 + cb**2):.2f}")

    elif menu == "Financeiro":
        st.header("💰 Juros Compostos")
        st.latex(r"M = C(1+i)^t")
        cap = st.number_input("Capital Inicial", 1000.0)
        tax = st.number_input("Taxa mensal (%)", 1.0) / 100
        tmp = st.number_input("Meses", 12)
        if st.button("Calcular Montante"):
            m = cap * (1 + tax)**tmp
            st.metric("Montante Final", f"R$ {m:.2f}", f"Juros: R$ {m-cap:.2f}")