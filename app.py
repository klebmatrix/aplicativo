import streamlit as st
import os
import numpy as np
import plotly.express as px
from cryptography.fernet import Fernet
from fpdf import FPDF
import random

# --- 1. SEGURANÇA (Render) ---
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
    st.info("Acesse suas atividades abaixo:")
    # Link da pasta pública dos alunos
    link_aluno = "https://drive.google.com/drive/folders/1NkFeom_k3LUJYAFVBBDu4GD5aYVeNEZc?usp=drive_link"
    st.link_button("📂 Abrir Pasta de Exercícios", link_aluno)

# --- TELA DO PROFESSOR (ADMIN) ---
elif st.session_state.perfil == "admin":
    st.sidebar.title("🛠 Painel Professor")
    menu = st.sidebar.radio("Navegação", ["Gerador de Listas", "Sistemas Lineares", "Álgebra", "Geometria", "Financeiro", "Pasta Professor"])
    st.sidebar.button("Sair", on_click=lambda: st.session_state.update({"perfil": None}))

    # NOVO MÓDULO: LINK PARA GOOGLE DRIVE DO PROFESSOR
    if menu == "Pasta Professor":
        st.header("📂 Gerenciador de Arquivos no Drive")
        st.write("Acesse sua pasta privada para organizar, excluir ou renomear arquivos.")
        link_admin_drive = "https://drive.google.com/drive/folders/1mvSy-0J6GCGCls4CReGyRXVFbJNkFMfQ?usp=drive_link"
        st.link_button("🚀 Abrir Meu Google Drive", link_admin_drive)

    elif menu == "Gerador de Listas":
        st.header("📝 Criador de Exercícios")
        tema = st.selectbox("Escolha o Tema:", ["Equações 1º Grau", "Teorema de Pitágoras"])
        if st.button("🚀 Gerar 10 Questões"):
            qs, gs = [], []
            for i in range(1, 11):
                if "1º Grau" in tema:
                    a, x, b = random.randint(2, 6), random.randint(1, 15), random.randint(1, 20)
                    res = (a * x) + b
                    qs.append(f"{i}) Resolva: {a}x + {b} = {res}")
                    gs.append(f"{i}) x = {x}")
                else:
                    ca, cb = random.randint(3, 9), random.randint(4, 12)
                    h = np.sqrt(ca**2 + cb**2)
                    qs.append(f"{i}) Catetos {ca} e {cb}. Calcule a hipotenusa.")
                    gs.append(f"{i}) H = {h:.2f}")
            pdf_data = gerar_material_pdf(tema, qs, gs)
            st.download_button("📥 Baixar PDF", pdf_data, "atividade.pdf")

    elif menu == "Sistemas Lineares":
        st.header("📏 Sistemas Ax = B")
        ordem = st.selectbox("Ordem:", [2, 3])
        mat_A, vec_B = [], []
        for i in range(ordem):
            cols = st.columns(ordem + 1)
            mat_A.append([cols[j].number_input(f"A{i}{j}", value=float(i==j), key=f"A{i}{j}") for j in range(ordem)])
            vec_B.append(cols[ordem].number_input(f"B{i}", value=1.0, key=f"B{i}"))
        if st.button("Resolver"):
            try:
                A, B = np.array(mat_A), np.array(vec_B)
                sol = np.linalg.solve(A, B)
                st.write(f"Solução: {sol}")
                st.plotly_chart(px.imshow(A, text_auto=True))
            except: st.error("Erro matemático.")

    elif menu == "Álgebra":
        st.header("🔍 Bhaskara")
        st.latex(r"ax^2 + bx + c = 0")
        c1, c2, c3 = st.columns(3)
        va, vb, vc = c1.number_input("a", 1.0), c2.number_input("b", -5.0), c3.number_input("c", 6.0)
        if st.button("Calcular"):
            d = vb**2 - 4*va*vc
            if d >= 0:
                st.write(f"x1 = {(-vb+np.sqrt(d))/(2*va):.2f} | x2 = {(-vb-np.sqrt(d))/(2*va):.2f}")
            else: st.error("Delta negativo.")

    elif menu == "Geometria":
        st.header("📐 Pitágoras")
        st.latex(r"a^2 + b^2 = c^2")
        ca, cb = st.number_input("Cateto A", 3.0), st.number_input("Cateto B", 4.0)
        if st.button("Calcular Hipotenusa"):
            st.success(f"H = {np.sqrt(ca**2 + cb**2):.2f}")

    elif menu == "Financeiro":
        st.header("💰 Juros Compostos")
        st.latex(r"M = C(1+i)^t")
        cap, tax, tmp = st.number_input("Capital", 1000.0), st.number_input("Taxa %", 1.0)/100, st.number_input("Meses", 12)
        if st.button("Calcular"):
            st.metric("Montante", f"R$ {cap*(1+tax)**tmp:.2f}")