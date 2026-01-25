import streamlit as st
import os
import numpy as np
import plotly.express as px
from cryptography.fernet import Fernet
from fpdf import FPDF
import random
from datetime import datetime

# Garante que a pasta física exista
if not os.path.exists("atividades"):
    os.makedirs("atividades")

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
    except:
        pass
    return "negado"

st.set_page_config(page_title="Quantum Lab", layout="wide")

if 'perfil' not in st.session_state: st.session_state.perfil = None
if 'nuvem_pdf' not in st.session_state: st.session_state.nuvem_pdf = []
if 'preview_pdf' not in st.session_state: st.session_state.preview_pdf = None

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
    pdf.set_font("Arial", size=12)
    for r in respostas:
        pdf.multi_cell(0, 10, txt=r); pdf.ln(2)
    return pdf.output(dest='S').encode('latin-1')

# --- LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Quantum Math Lab")
    pin = st.text_input("PIN de acesso:", type="password")
    if st.button("Entrar"):
        acesso = validar_acesso(pin)
        if acesso != "negado":
            st.session_state.perfil = acesso
            st.rerun()
        else:
            st.error("PIN inválido.")
    st.stop()

# --- ÁREA DO ALUNO ---
if st.session_state.perfil == "aluno":
    st.title("🎓 Portal do Aluno")
    if st.sidebar.button("Sair"):
        st.session_state.perfil = None
        st.rerun()
    
    st.subheader("📄 Atividades Disponíveis")
    if not st.session_state.nuvem_pdf:
        st.info("Nenhuma atividade publicada.")
    else:
        for i, item in enumerate(st.session_state.nuvem_pdf):
            c1, c2 = st.columns([4, 1])
            c1.write(f"📌 **{item['nome']}** | {item['tema']}")
            c2.download_button("Baixar", item['bin'], file_name=f"{item['nome']}.pdf", key=f"al_{i}")

# --- ÁREA DO ADMIN ---
elif st.session_state.perfil == "admin":
    st.sidebar.title("🛠 Painel Admin")
    menu = st.sidebar.radio("Menu", ["Gerador de Atividades", "Álgebra", "Geometria", "Sistemas Lineares", "Financeiro"])
    if st.sidebar.button("Sair"):
        st.session_state.perfil = None
        st.rerun()

    # GERADOR COM SALVAMENTO EM PASTA
    if menu == "Gerador de Atividades":
        st.header("📝 Criar e Publicar")
        tema = st.selectbox("Tema:", ["Álgebra", "Geometria"])
        nome_doc = st.text_input("Nome da Atividade:", "Lista_Matematica")
        
        if st.button("👁️ Gerar Prévia"):
            qs, gs = [f"Questao 1 de {tema}?"], ["Resposta 1"]
            st.session_state.preview_pdf = {
                "nome": nome_doc, "tema": tema, "bin": gerar_material_pdf(tema, qs, gs)
            }
        
        if st.session_state.preview_pdf:
            st.write("---")
            st.download_button("📥 Conferir PDF", st.session_state.preview_pdf['bin'], "revisao.pdf")
            if st.button("✅ Publicar (Salvar na Pasta e Nuvem)"):
                # Salva na pasta 'atividades'
                caminho = f"atividades/{st.session_state.preview_pdf['nome']}.pdf"
                with open(caminho, "wb") as f:
                    f.write(st.session_state.preview_pdf['bin'])
                # Manda para o Aluno
                st.session_state.nuvem_pdf.append(st.session_state.preview_pdf)
                st.session_state.preview_pdf = None
                st.success("Salvo com sucesso!")
                st.rerun()

    # ÁLGEBRA
    elif menu == "Álgebra":
        st.header("🔍 Equações de 1º e 2º Grau")
        st.latex(r"ax^2 + bx + c = 0")
        c1, c2, c3 = st.columns(3)
        va = c1.number_input("a", 1.0)
        vb = c2.number_input("b", -5.0)
        vc = c3.number_input("c", 6.0)
        if st.button("Resolver"):
            delta = vb**2 - 4*va*vc
            if delta >= 0:
                st.success(f"x1: {(-vb+np.sqrt(delta))/(2*va):.2f} | x2: {(-vb-np.sqrt(delta))/(2*va):.2f}")
            else: st.error("Raízes complexas.")

    # GEOMETRIA
    elif menu == "Geometria":
        st.header("📐 Teorema de Pitágoras")
        st.latex(r"a^2 + b^2 = c^2")
        cat1 = st.number_input("Cateto A", 3.0)
        cat2 = st.number_input("Cateto B", 4.0)
        if st.button("Calcular Hipotenusa"):
            st.success(f"H = {np.sqrt(cat1**2 + cat2**2):.2f}")

    # SISTEMAS
    elif menu == "Sistemas Lineares":
        st.header("📏 Sistemas Ax = B")
        ordem = st.selectbox("Ordem:", [2, 3])
        mat_A, vec_B = [], []
        for i in range(ordem):
            cols = st.columns(ordem + 1)
            mat_A.append([cols[j].number_input(f"A{i}{j}", value=float(i==j), key=f"A{i}{j}") for j in range(ordem)])
            vec_B.append(cols[ordem].number_input(f"B{i}", value=1.0, key=f"B{i}"))
        if st.button("Resolver Sistema"):
            try:
                sol = np.linalg.solve(np.array(mat_A), np.array(vec_B))
                st.write("Solução:", sol)
                st.plotly_chart(px.imshow(np.array(mat_A), text_auto=True))
            except: st.error("Sem solução única.")

    # FINANCEIRO
    elif menu == "Financeiro":
        st.header("💰 Juros Compostos")
        st.latex(r"M = C(1+i)^t")
        cap = st.number_input("Capital", 1000.0)
        tax = st.number_input("Taxa %", 1.0)/100
        tmp = st.number_input("Meses", 12.0)
        st.metric("Montante", f"R$ {cap*(1+tax)**tmp:.2f}")