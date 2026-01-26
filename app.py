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
        # Pega a chave mestra das variáveis de ambiente do Render [cite: 2026-01-23]
        chave = os.environ.get('chave_mestra') # [cite: 2026-01-24]
        if not chave: return "erro_env"
        chave = chave.strip().replace("'", "").replace('"', "").replace('b', '', 1) if chave.startswith('b') else chave.strip()
        f = Fernet(chave.encode())
        # O PIN de acesso deve ter entre 6 e 8 caracteres [cite: 2026-01-21]
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
    # O PIN de acesso é uma senha de 6 dígitos [cite: 2026-01-19]
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
    st.info("Acesse a pasta de atividades no Google Drive abaixo:")
    st.link_button("📂 Abrir Pasta de Exercícios", "COLE_AQUI_O_LINK_DA_PASTA_DOS_ALUNOS")

# --- ÁREA DO PROFESSOR (ADMIN) ---
elif st.session_state.perfil == "admin":
    st.sidebar.title("🛠 Painel Professor")
    menu = st.sidebar.radio("Navegação", ["Gerador de Listas", "Matrizes (Inversa/Sarrus)", "Funções (Divisores)", "Sistemas Lineares", "Álgebra", "Geometria", "Financeiro", "Pasta Professor"])
    st.sidebar.button("Sair", on_click=lambda: st.session_state.update({"perfil": None}))

    if menu == "Matrizes (Inversa/Sarrus)":
        st.header("🧮 Matrizes: Determinante e Inversa")
        ordem = st.selectbox("Ordem da Matriz:", [2, 3], key="ordem_matriz")
        mat_M = []
        for i in range(ordem):
            cols = st.columns(ordem)
            mat_M.append([cols[j].number_input(f"A{i+1}{j+1}", value=float(i==j), key=f"v_mat_{i}{j}") for j in range(ordem)])
        
        if st.button("Calcular"):
            A = np.array(mat_M)
            if ordem == 3:
                st.subheader("📝 Regra de Sarrus")
                d1 = A[0,0]*A[1,1]*A[2,2]; d2 = A[0,1]*A[1,2]*A[2,0]; d3 = A[0,2]*A[1,0]*A[2,1]
                v1 = A[0,2]*A[1,1]*A[2,0]; v2 = A[0,0]*A[1,2]*A[2,1]; v3 = A[0,1]*A[1,0]*A[2,2]
                st.write(f"Principais: {d1+d2+d3:.2f} | Secundárias: {v1+v2+v3:.2f}")
                det = (d1+d2+d3) - (v1+v2+v3)
            else:
                det = A[0,0]*A[1,1] - A[0,1]*A[1,0]
            
            st.success(f"Determinante: {det:.2f}")
            if abs(det) > 0.0001:
                st.write("**Matriz Inversa:**", np.linalg.inv(A))
            else: st.error("Matriz sem inversa.")

    elif menu == "Funções (Divisores)":
        st.header("🔍 Função f(n) - Divisores")
        n_val = st.number_input("Digite n:", min_value=1, value=12)
        if st.button("Calcular f(n)"):
            res = contar_divisores(n_val)
            st.success(f"f({n_val}) = {res} divisores.")

    elif menu == "Gerador de Listas":
        st.header("📝 Gerador de Exercícios")
        tema = st.selectbox("Tema:", ["Matriz Inversa", "Funções (Divisores)", "Pitágoras", "Equações 1º Grau"])
        if st.button("🚀 Gerar 10 Questões"):
            qs, gs = [], []
            for i in range(1, 11):
                if tema == "Matriz Inversa":
                    v = random.randint(1, 4)
                    qs.append(f"{i}) Inversa da matriz diagonal A = [[{v}, 0, 0], [0, {v+1}, 0], [0, 0, 1]].")
                    gs.append(f"{i}) A^-1 = [[{1/v:.2f}, 0, 0], [0, {1/(v+1):.2f}, 0], [0, 0, 1.0]]")
                elif tema == "Funções (Divisores)":
                    n = random.randint(10, 80)
                    qs.append(f"{i}) Calcule f({n}), o numero de divisores de n.")
                    gs.append(f"{i}) f({n}) = {contar_divisores(n)}")
                elif tema == "Pitágoras":
                    ca, cb = random.randint(3, 12), random.randint(4, 15)
                    qs.append(f"{i}) Catetos {ca} e {cb}. Hipotenusa?")
                    gs.append(f"{i}) H = {np.sqrt(ca**2+cb**2):.2f}")
                elif tema == "Equações 1º Grau":
                    a, x, b = random.randint(2, 6), random.randint(1, 15), random.randint(1, 20)
                    qs.append(f"{i}) Resolva: {a}x + {b} = {(a*x)+b}")
                    gs.append(f"{i}) x = {x}")
            
            pdf_data = gerar_material_pdf(tema, qs, gs)
            st.download_button("📥 Baixar PDF", pdf_data, f"atividade_{tema.lower()}.pdf")

    elif menu == "Álgebra":
        st.header("🔍 Bhaskara")
        c1, c2, c3 = st.columns(3)
        va, vb, vc = c1.number_input("a", 1.0), c2.number_input("b", -5.0), c3.number_input("c", 6.0)
        if st.button("Calcular Raízes"):
            delta = vb**2 - 4*va*vc
            if delta >= 0: st.success(f"x1={(-vb+np.sqrt(delta))/(2*va):.2f}, x2={(-vb-np.sqrt(delta))/(2*va):.2f}")
            else: st.error("Raízes Complexas.")

    elif menu == "Pasta Professor":
        st.header("📂 Gerenciador Drive")
        st.link_button("🚀 Abrir Meu Drive", "COLE_AQUI_O_LINK_DA_PASTA_PROFESSOR")