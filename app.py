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

# --- CONFIGURAÇÃO ---
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
    pin = st.text_input("Digite o PIN (Admin ou Aluno):", type="password")
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
    st.sidebar.write("👤 Perfil: Aluno")
    if st.sidebar.button("Sair"):
        st.session_state.perfil = None
        st.rerun()

    st.subheader("📄 Materiais Publicados pelo Professor")
    if not st.session_state.nuvem_pdf:
        st.info("Nenhuma atividade disponível no momento.")
    else:
        for i, item in enumerate(st.session_state.nuvem_pdf):
            with st.container():
                c1, c2 = st.columns([4, 1])
                c1.write(f"📌 **{item['nome']}** | {item['tema']} | 📅 {item['data']}")
                c2.download_button("Download", item['bin'], file_name=f"{item['nome']}.pdf", key=f"dl_{i}")
                st.divider()

# --- ÁREA DO PROFESSOR (ADMIN) ---
elif st.session_state.perfil == "admin":
    st.sidebar.title("🛠 Painel do Professor")
    menu = st.sidebar.radio("Navegação", ["Gerador/Publicador", "Cálculos e Sistemas"])
    if st.sidebar.button("Sair"):
        st.session_state.perfil = None
        st.rerun()

    if menu == "Gerador/Publicador":
        st.header("📝 Criar e Publicar Material para Alunos")
        tema = st.selectbox("Tema:", ["Álgebra (1º/2º Grau)", "Geometria (Pitágoras/Volumes)"])
        nome_doc = st.text_input("Nome da Atividade:", "Lista_Exercicio_01")
        
        if st.button("🚀 Gerar e Publicar"):
            qs, gs = [], []
            for i in range(1, 11):
                if "Álgebra" in tema:
                    a, x = random.randint(2, 5), random.randint(1, 10)
                    qs.append(f"{i}) Encontre x: {a}x + {random.randint(1,10)} = ...")
                    gs.append(f"{i}) x = {x}")
                else:
                    c1, c2 = random.randint(3, 9), random.randint(4, 12)
                    qs.append(f"{i}) Calcule a hipotenusa: Cateto A={c1}, Cateto B={c2}")
                    gs.append(f"{i}) H = {np.sqrt(c1**2 + c2**2):.2f}")
            
            pdf_bin = gerar_material_pdf(tema, qs, gs)
            st.session_state.nuvem_pdf.append({
                "nome": nome_doc, "tema": tema, "bin": pdf_bin, 
                "data": datetime.now().strftime("%d/%m/%Y %H:%M")
            })
            st.success(f"Atividade '{nome_doc}' publicada para os alunos!")

    elif menu == "Cálculos e Sistemas":
        tab1, tab2, tab3 = st.tabs(["Sistemas Ax=B", "Geometria", "Financeiro"])
        
        with tab1:
            st.subheader("Sistemas Lineares")
            
            ordem = st.selectbox("Ordem:", [2, 3])
            mat_A, vec_B = [], []
            for i in range(ordem):
                cols = st.columns(ordem + 1)
                mat_A.append([cols[j].number_input(f"A{i}{j}", value=float(i==j), key=f"A{i}{j}") for j in range(ordem)])
                vec_B.append(cols[ordem].number_input(f"B{i}", value=1.0, key=f"B{i}"))
            if st.button("Resolver"):
                sol = np.linalg.solve(np.array(mat_A), np.array(vec_B))
                st.write("Solução:", sol)
                st.plotly_chart(px.imshow(np.array(mat_A), text_auto=True))

        with tab2:
            st.subheader("Geometria")
            st.latex(r"a^2 + b^2 = c^2")
            

[Image of the Pythagorean theorem diagram]

            cat_a = st.number_input("Cateto 1", 3.0)
            cat_b = st.number_input("Cateto 2", 4.0)
            if st.button("Calcular Hipotenusa"):
                st.success(f"H = {np.sqrt(cat_a**2 + cat_b**2):.2f}")

        with tab3:
            st.subheader("Juros Compostos")
            st.latex(r"M = C(1+i)^t")
            
            c1, c2, c3 = st.columns(3)
            cap = c1.number_input("Capital", 1000.0)
            tax = c2.number_input("Taxa (%)", 1.0)/100
            tmp = c3.number_input("Tempo", 12.0)
            st.metric("Montante Final", f"R$ {cap*(1+tax)**tmp:.2f}")