import streamlit as st
import os
import numpy as np
import plotly.express as px
from cryptography.fernet import Fernet
from fpdf import FPDF
import random
from datetime import datetime

# --- 1. SEGURANÇA ---
PIN_CRIPTOGRAFADO = "gAAAAABpdRRwrtzON4oc6ayd3fx1LjLjX8TjRj7riCkHHuOpi0lcYFAu04KEXEo8d3-GJz9HmpP-AjvbLOLzr6zC6GMUvOCP1A=="

def validar_acesso(pin_digitado):
    if pin_digitado == "123456": return "aluno"
    try:
        chave = os.environ.get('chave_mestra')
        if not chave: return "erro_env"
        chave = chave.strip().replace("'", "").replace('"', "").replace('b', '', 1) if chave.startswith('b') else chave.strip()
        f = Fernet(chave.encode())
        if pin_digitado == f.decrypt(PIN_CRIPTOGRAFADO.strip().encode()).decode(): return "admin"
    except: pass
    return "negado"

st.set_page_config(page_title="Quantum Lab", layout="wide")

if 'perfil' not in st.session_state: st.session_state.perfil = None
if 'nuvem_pdf' not in st.session_state: st.session_state.nuvem_pdf = []

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

# --- TELA DE LOGIN ---
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

# --- ÁREA DO ALUNO ---
if st.session_state.perfil == "aluno":
    st.title("🎓 Portal do Aluno")
    if st.sidebar.button("Sair"):
        st.session_state.perfil = None
        st.rerun()

    st.subheader("📄 Atividades para Download")
    if not st.session_state.nuvem_pdf:
        st.info("Nenhuma atividade disponível no momento.")
    else:
        for i, item in enumerate(st.session_state.nuvem_pdf):
            c1, c2 = st.columns([4, 1])
            c1.write(f"📌 **{item['nome']}** | Tema: {item['tema']}")
            c2.download_button("Baixar", item['bin'], file_name=f"{item['nome']}.pdf", key=f"btn_{i}")
            st.divider()

# --- ÁREA DO PROFESSOR (ADMIN) ---
elif st.session_state.perfil == "admin":
    st.sidebar.title("🛠 Painel Admin")
    menu = st.sidebar.radio("Navegação", ["Gerenciador de Nuvem", "Ferramentas de Cálculo"])
    if st.sidebar.button("Sair"):
        st.session_state.perfil = None
        st.rerun()

    if menu == "Gerenciador de Nuvem":
        st.header("📝 Criar e Publicar Atividades")
        tema = st.selectbox("Tema:", ["Álgebra", "Geometria"])
        nome_doc = st.text_input("Nome do Arquivo:", "Lista_Exercicio")
        
        if st.button("🚀 Publicar para Alunos"):
            # Lógica simples de geração
            qs, gs = [], []
            for i in range(1, 11):
                n1, n2 = random.randint(1, 50), random.randint(1, 50)
                qs.append(f"{i}) Quanto e {n1} + {n2}?")
                gs.append(f"{i}) Resposta: {n1+n2}")
            
            pdf_bin = gerar_material_pdf(tema, qs, gs)
            st.session_state.nuvem_pdf.append({
                "nome": nome_doc, "tema": tema, "bin": pdf_bin, 
                "data": datetime.now().strftime("%H:%M")
            })
            st.success("Atividade enviada com sucesso!")

        st.divider()
        st.subheader("🗑️ Gerenciar Atividades Publicadas")
        for idx, doc in enumerate(st.session_state.nuvem_pdf):
            col_n, col_b = st.columns([4, 1])
            col_n.write(f"📄 {doc['nome']} ({doc['tema']})")
            if col_b.button("Excluir", key=f"del_{idx}"):
                st.session_state.nuvem_pdf.pop(idx)
                st.rerun()

    elif menu == "Ferramentas de Cálculo":
        t1, t2, t3 = st.tabs(["Sistemas Ax=B", "Álgebra", "Financeiro"])
        
        with t1:
            st.subheader("Sistemas Lineares")
            st.latex(r"Ax = B")
            ordem = st.selectbox("Ordem:", [2, 3])
            mat_A, vec_B = [], []
            for i in range(ordem):
                cols = st.columns(ordem + 1)
                mat_A.append([cols[j].number_input(f"A{i}{j}", value=float(i==j), key=f"A{i}{j}") for j in range(ordem)])
                vec_B.append(cols[ordem].number_input(f"B{i}", value=1.0, key=f"B{i}"))
            if st.button("Resolver"):
                try:
                    sol = np.linalg.solve(np.array(mat_A), np.array(vec_B))
                    st.success(f"Solução: {sol}")
                    st.plotly_chart(px.imshow(np.array(mat_A), text_auto=True))
                except: st.error("Erro no cálculo.")

        with t2:
            st.subheader("Equações")
            st.latex(r"ax^2 + bx + c = 0")
            c1, c2, c3 = st.columns(3)
            va = c1.number_input("a", 1.0)
            vb = c2.number_input("b", -5.0)
            vc = c3.number_input("c", 6.0)
            if st.button("Bhaskara"):
                delta = vb**2 - 4*va*vc
                if delta >= 0:
                    st.success(f"x1: {(-vb+np.sqrt(delta))/(2*va):.2f} | x2: {(-vb-np.sqrt(delta))/(2*va):.2f}")
                else: st.error("Delta negativo.")

        with t3:
            st.subheader("Financeiro")
            st.latex(r"M = C(1+i)^t")
            cap = st.number_input("Capital", 1000.0)
            tax = st.number_input("Taxa (%)", 1.0)/100
            tmp = st.number_input("Tempo", 12.0)
            st.metric("Montante", f"R$ {cap*(1+tax)**tmp:.2f}")