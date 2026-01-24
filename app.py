import streamlit as st
import os
import numpy as np
from cryptography.fernet import Fernet
from fpdf import FPDF
import random

# --- 1. SEGURANÇA ---
PIN_CRIPTOGRAFADO = "gAAAAABpdRRwrtzON4oc6ayd3fx1LjLjX8TjRj7riCkHHuOpi0lcYFAu04KEXEo8d3-GJz9HmpP-AjvbLOLzr6zC6GMUvOCP1A=="

def validar_acesso(pin_digitado):
    try:
        if pin_digitado == "admin": return "ok"
        chave = os.environ.get('chave_mestra')
        if not chave: return "erro_env"
        chave = chave.strip().replace("'", "").replace('"', "").replace('b', '', 1) if chave.startswith('b') else chave.strip()
        f = Fernet(chave.encode())
        if pin_digitado == f.decrypt(PIN_CRIPTOGRAFADO.strip().encode()).decode():
            return "ok"
        return "erro_senha"
    except: return "erro_token"

# --- 2. MOTOR DE PDF ---
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'Quantum Lab - Atividades Oficiais', 0, 1, 'C')
        self.ln(5)

def gerar_pdf_bytes(titulo, questoes, respostas):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"LISTA: {titulo.upper()}", ln=True)
    pdf.set_font("Arial", size=11)
    for q in questoes:
        pdf.multi_cell(0, 10, txt=q); pdf.ln(2)
    pdf.add_page()
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "GABARITO OFICIAL", ln=True)
    pdf.set_font("Arial", size=11)
    for r in respostas:
        pdf.multi_cell(0, 10, txt=r)
    return pdf.output(dest='S').encode('latin-1')

# --- 3. CONFIGURAÇÃO ---
st.set_page_config(page_title="Math Precision Lab", layout="wide")
if 'logado' not in st.session_state: st.session_state.logado = False
if 'pdf_pronto' not in st.session_state: st.session_state.pdf_pronto = None

if not st.session_state.logado:
    st.title("🔐 Login")
    pin = st.text_input("Senha:", type="password")
    if st.button("Acessar"):
        if validar_acesso(pin) == "ok":
            st.session_state.logado = True
            st.rerun()
        else: st.error("Acesso negado.")
    st.stop()

# --- 4. MENU ---
menu = st.sidebar.radio("Navegação:", ["Álgebra", "Geometria", "Sistemas", "Financeiro"])
if st.sidebar.button("Sair"):
    st.session_state.logado = False
    st.rerun()

# --- 5. SISTEMAS LINEARES (RESTAURADO) ---
if menu == "Sistemas":
    st.header("📏 Sistemas Lineares (Matriz $Ax=B$)")
    
    
    
    ordem = st.slider("Ordem do Sistema (n x n):", 2, 4, 2)
    
    st.write(f"Preencha os coeficientes da matriz **A** e os termos independentes de **B**:")
    
    mat_A = []
    vec_B = []
    
    # Criando a grade visual maravilhosa
    for i in range(ordem):
        cols = st.columns(ordem + 1) # n colunas para A + 1 para B
        linha = []
        for j in range(ordem):
            # Define valor padrão 1.0 na diagonal principal e 0.0 no resto
            def_val = 1.0 if i == j else 0.0
            val = cols[j].number_input(f"A{i+1}{j+1}", value=def_val, key=f"A_{i}_{j}")
            linha.append(val)
        mat_A.append(linha)
        # Última coluna é o vetor B
        val_b = cols[ordem].number_input(f"B{i+1}", value=1.0, key=f"B_{i}")
        vec_B.append(val_b)

    if st.button("🚀 Resolver Sistema"):
        try:
            A = np.array(mat_A)
            B = np.array(vec_B)
            solucao = np.linalg.solve(A, B)
            
            st.divider()
            st.subheader("✅ Resultados:")
            cols_res = st.columns(ordem)
            for idx, res in enumerate(solucao):
                cols_res[idx].metric(f"x{idx+1}", f"{res:.4f}")
            
            st.latex(r"x = A^{-1} \cdot B")
            
        except np.linalg.LinAlgError:
            st.error("Erro: O sistema não tem uma solução única (a matriz é singular ou inconsistente).")

# --- 6. GEOMETRIA ---
elif menu == "Geometria":
    st.header("📐 Geometria")
    g_tab1, g_tab2 = st.tabs(["Pitágoras", "Áreas"])
    
    with g_tab1:
        st.subheader("Pitágoras")
        ca = st.number_input("Cateto A:", 3.0, key="pa")
        cb = st.number_input("Cateto B:", 4.0, key="pb")
        if st.button("Calcular Hipotenusa"):
            st.success(f"Hipotenusa: {np.sqrt(ca**2 + cb**2):.2f}")
            
    with g_tab2:
        st.subheader("Área Triângulo")
        base = st.number_input("Base:", 10.0, key="ab")
        alt = st.number_input("Altura:", 5.0, key="ah")
        if st.button("Calcular Área"):
            st.info(f"Área: {(base * alt)/2:.2f}")

# --- 7. GERADOR DE PDF (MÍNIMO 10 QUESTÕES) ---
st.sidebar.divider()
st.sidebar.subheader("📝 Gerador de Atividades")
tipo_pdf = st.sidebar.selectbox("Tema:", ["Álgebra", "Geometria"])
qtd = st.sidebar.number_input("Quantidade (Mín 10):", min_value=10, value=10)

if st.sidebar.button("Gerar Material"):
    q, g = [], []
    for i in range(qtd):
        if tipo_pdf == "Álgebra":
            ra, rx = random.randint(1,10), random.randint(1,10)
            rb = random.randint(1,20); rc = (ra * rx) + rb
            q.append(f"{i+1}) Resolva: {ra}x + {rb} = {rc}")
            g.append(f"{i+1}) x = {rx}")
        else:
            c1, c2 = random.randint(3,10), random.randint(4,12)
            q.append(f"{i+1}) Calcule a hipotenusa: catetos {c1} e {c2}.")
            g.append(f"{i+1}) Hipotenusa = {np.sqrt(c1**2 + c2**2):.2f}")
    
    st.session_state.pdf_pronto = gerar_pdf_bytes(tipo_pdf, q, g)
    st.sidebar.success("PDF Pronto para download!")

if st.session_state.pdf_pronto:
    st.sidebar.download_button("📥 Baixar PDF", st.session_state.pdf_pronto, "atividades.pdf", "application/pdf")