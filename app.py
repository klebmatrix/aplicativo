import streamlit as st
import os
import numpy as np
import plotly.express as px
from cryptography.fernet import Fernet
from fpdf import FPDF
import random
from datetime import datetime

# Criar pasta de atividades se não existir
if not os.path.exists("atividades"):
    os.makedirs("atividades")

# --- 1. SEGURANÇA (VARIÁVEIS DE AMBIENTE) ---
PIN_CRIPTOGRAFADO = "gAAAAABpdRRwrtzON4oc6ayd3fx1LjLjX8TjRj7riCkHHuOpi0lcYFAu04KEXEo8d3-GJz9HmpP-AjvbLOLzr6zC6GMUvOCP1A=="

def validar_acesso(pin_digitado):
    # Busca a senha do aluno na variável de ambiente
    senha_aluno_env = os.environ.get('acesso_aluno')
    if pin_digitado == senha_aluno_env:
        return "aluno"
    
    try:
        chave = os.environ.get('chave_mestra')
        if not chave: return "erro_env"
        # Limpeza da chave mestra
        chave = chave.strip().replace("'", "").replace('"', "").replace('b', '', 1) if chave.startswith('b') else chave.strip()
        f = Fernet(chave.encode())
        # Validação do Admin
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

# --- TELA DE LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Quantum Math Lab")
    pin = st.text_input("Digite o PIN de acesso:", type="password")
    if st.button("Entrar"):
        if not os.environ.get('acesso_aluno'):
            st.warning("Aviso: Variável 'acesso_aluno' não configurada no Render.")
        
        acesso = validar_acesso(pin)
        if acesso != "negado":
            st.session_state.perfil = acesso
            st.rerun()
        else:
            st.error("PIN incorreto ou não configurado.")
    st.stop()

# --- ÁREA DO ALUNO ---
if st.session_state.perfil == "aluno":
    st.title("🎓 Portal do Aluno")
    if st.sidebar.button("Sair"):
        st.session_state.perfil = None
        st.rerun()

    st.subheader("📄 Atividades Publicadas")
    if not st.session_state.nuvem_pdf:
        st.info("Nenhuma atividade liberada no momento.")
    else:
        for i, item in enumerate(st.session_state.nuvem_pdf):
            c1, c2 = st.columns([4, 1])
            c1.write(f"📌 **{item['nome']}** | {item['tema']}")
            c2.download_button("Baixar", item['bin'], file_name=f"{item['nome']}.pdf", key=f"al_{i}")
            st.divider()

# --- ÁREA DO PROFESSOR (ADMIN) ---
elif st.session_state.perfil == "admin":
    st.sidebar.title("🛠 Painel Admin")
    menu = st.sidebar.radio("Navegação", ["Gerar e Revisar", "Nuvem Aluno", "Cálculos"])
    if st.sidebar.button("Sair"):
        st.session_state.perfil = None
        st.rerun()

    if menu == "Gerar e Revisar":
        st.header("📝 Criar Material")
        tema = st.selectbox("Escolha o Tema:", ["Álgebra", "Geometria"])
        nome_doc = st.text_input("Nome do Arquivo:", "Atividade_Quantum")
        
        if st.button("👁️ Gerar Prévia"):
            qs, gs = [], []
            for i in range(1, 11):
                if tema == "Álgebra":
                    a, x = random.randint(2, 5), random.randint(1, 10)
                    qs.append(f"{i}) Resolva a equacao: {a}x + {random.randint(1,10)} = ...")
                    gs.append(f"{i}) x = {x}")
                else:
                    c1, c2 = random.randint(3, 9), random.randint(4, 12)
                    qs.append(f"{i}) Calcule a hipotenusa: Cateto A={c1}, Cateto B={c2}")
                    gs.append(f"{i}) H = {np.sqrt(c1**2 + c2**2):.2f}")
            
            st.session_state.preview_pdf = {
                "nome": nome_doc, "tema": tema, 
                "bin": gerar_material_pdf(tema, qs, gs),
                "data": datetime.now().strftime("%d/%m %H:%M")
            }

        if st.session_state.preview_pdf:
            st.divider()
            st.warning(f"Revisando: **{st.session_state.preview_pdf['nome']}**")
            st.download_button("📥 Baixar para Conferir", st.session_state.preview_pdf['bin'], "conferir.pdf")
            
            if st.button("✅ Publicar para Alunos"):
                st.session_state.nuvem_pdf.append(st.session_state.preview_pdf)
                st.session_state.preview_pdf = None
                st.success("Atividade publicada!")
                st.rerun()

    elif menu == "Cálculos":
        st.header("Calculadora de Apoio")
        st.latex(r"ax^2 + bx + c = 0")
        

[Image of the quadratic formula]

        st.latex(r"a^2 + b^2 = c^2")
        

[Image of the Pythagorean theorem diagram]