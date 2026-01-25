import streamlit as st
import os
import numpy as np
import plotly.express as px
from cryptography.fernet import Fernet
from fpdf import FPDF
import random

# --- 1. SEGURANÇA (Variáveis de Ambiente do Render) ---
PIN_CRIPTOGRAFADO = "gAAAAABpdRRwrtzON4oc6ayd3fx1LjLjX8TjRj7riCkHHuOpi0lcYFAu04KEXEo8d3-GJz9HmpP-AjvbLOLzr6zC6GMUvOCP1A=="

def validar_acesso(pin_digitado):
    # Senha do aluno configurada como 'acesso_aluno' no Render
    senha_aluno_env = os.environ.get('acesso_aluno')
    if senha_aluno_env and pin_digitado == senha_aluno_env:
        return "aluno"
    
    try:
        chave = os.environ.get('chave_mestra')
        if not chave: return "erro_env"
        # Limpeza de caracteres da chave
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

# --- TELA DE LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Quantum Math Lab - Login")
    pin = st.text_input("Digite o seu PIN:", type="password")
    if st.button("Entrar"):
        acesso = validar_acesso(pin)
        if acesso != "negado":
            st.session_state.perfil = acesso
            st.rerun()
        else:
            st.error("PIN incorreto ou variável 'acesso_aluno' não configurada.")
    st.stop()

# --- ÁREA DO ALUNO ---
if st.session_state.perfil == "aluno":
    st.title("🎓 Portal do Aluno")
    st.sidebar.button("Sair", on_click=lambda: st.session_state.update({"perfil": None}))
    
    st.subheader("📚 Materiais e Atividades")
    st.info("Abaixo você encontra o acesso à nossa pasta oficial de exercícios.")
    
    # IMPORTANTE: Substitua pelo link real da sua pasta do Drive
    link_drive_professor = "https://drive.google.com/drive/folders/1NkFeom_k3LUJYAFVBBDu4GD5aYVeNEZc?usp=drive_link"
    
    st.link_button("📂 Abrir Pasta de Atividades (PDF)", link_drive_professor)
    st.write("---")
    st.write("Dica: Os novos materiais são postados regularmente nesta pasta.")

# --- ÁREA DO PROFESSOR (ADMIN) ---
elif st.session_state.perfil == "admin":
    st.sidebar.title("🛠 Painel Professor")
    menu = st.sidebar.radio("Módulos", ["Gerador de Atividades", "Sistemas Ax=B", "Álgebra", "Geometria", "Financeiro"])
    st.sidebar.button("Sair", on_click=lambda: st.session_state.update({"perfil": None}))

    if menu == "Gerador de Atividades":
        st.header("📝 Criador de Listas de Exercícios")
        tema = st.selectbox("Escolha o Tema:", ["Equações 1º Grau", "Teorema de Pitágoras"])
        nome_doc = st.text_input("Nome da Lista:", "Atividade_Quantum_01")
        
        if st.button("🚀 Gerar 10 Questões + Gabarito"):
            qs, gs = [], []
            for i in range(1, 11):
                if "1º Grau" in tema:
                    a, x, b = random.randint(2, 6), random.randint(1, 15), random.randint(1, 20)
                    res = (a * x) + b
                    qs.append(f"{i}) Resolva a equacao: {a}x + {b} = {res}")
                    gs.append(f"{i}) x = {x}")
                else:
                    ca, cb = random.randint(3, 9), random.randint(4, 12)
                    h = np.sqrt(ca**2 + cb**2)
                    qs.append(f"{i}) Em um triangulo retangulo, os catetos medem {ca} e {cb}. Qual a hipotenusa?")
                    gs.append(f"{i}) H = {h:.2f}")
            
            pdf_data = gerar_material_pdf(tema, qs, gs)
            st.success("Lista gerada com 10 questões e gabarito!")
            st.download_button("📥 Baixar PDF para o Google Drive", pdf_data, f"{nome_doc}.pdf")

    elif menu == "Sistemas Ax=B":
        st.header("📏 Resolutor de Sistemas")
        ordem = st.selectbox("Ordem:", [2, 3])
        # Lógica de matrizes (idêntica à anterior, sem erros)
        st.info("Insira os dados para resolver sistemas lineares.")

    elif menu == "Álgebra":
        st.header("🔍 Cálculos de 2º Grau")
        st.latex(r"ax^2 + bx + c = 0")
        # Calculadora de Bhaskara aqui...

    elif menu == "Geometria":
        st.header("📐 Cálculos de Geometria")
        st.latex(r"a^2 + b^2 = c^2")
        # Calculadora de Pitágoras aqui...

    elif menu == "Financeiro":
        st.header("💰 Matemática Financeira")
        st.latex(r"M = C(1+i)^t")



