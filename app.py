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
        chave = os.environ.get('chave_mestra')
        if not chave: return "erro_env"
        chave = chave.strip().replace("'", "").replace('"', "").replace('b', '', 1) if chave.startswith('b') else chave.strip()
        f = Fernet(chave.encode())
        return "ok" if pin_digitado == f.decrypt(PIN_CRIPTOGRAFADO.strip().encode()).decode() else "erro_senha"
    except: return "erro_token"

# --- 2. CLASSE PDF ---
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'Quantum Math Lab - Relatorio Cientifico', 0, 1, 'C')
        self.ln(5)

def gerar_pdf_simples(titulo, linhas):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, titulo.upper(), ln=True)
    pdf.set_font("Arial", size=11)
    for l in linhas:
        pdf.multi_cell(0, 10, txt=l)
    return pdf.output(dest='S').encode('latin-1')

def gerar_pdf_atividades(questoes, respostas):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "LISTA DE EXERCICIOS", ln=True)
    pdf.set_font("Arial", size=11)
    for q in questoes:
        pdf.multi_cell(0, 10, txt=q); pdf.ln(2)
    pdf.add_page()
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "GABARITO", ln=True)
    pdf.set_font("Arial", size=11)
    for r in respostas:
        pdf.multi_cell(0, 10, txt=r)
    return pdf.output(dest='S').encode('latin-1')

# --- 3. CONFIGURAÇÃO ---
st.set_page_config(page_title="Math Precision Lab", layout="wide")
if 'logado' not in st.session_state: st.session_state.logado = False

if not st.session_state.logado:
    st.title("🔐 Acesso ao Laboratorio")
    pin = st.text_input("Senha:", type="password")
    if st.button("Entrar"):
        res = validar_acesso(pin)
        if res == "ok": st.session_state.logado = True; st.rerun()
        else: st.error(f"Erro: {res}")
    st.stop()

# --- 4. MENU LATERAL ---
menu = st.sidebar.radio("Categorias:", ["Algebra", "Geometria", "Sistemas", "Financeiro", "Gerador de Atividades"])
if st.sidebar.button("Logoff"): st.session_state.logado = False; st.rerun()

# --- ÁLGEBRA ---
if menu == "Algebra":
    st.header("🔍 Equacoes de 1º e 2º Grau")
    grau = st.selectbox("Tipo:", ["1º Grau (ax + b = c)", "2º Grau (ax² + bx + c = 0)"])
    
    if grau == "1º Grau (ax + b = c)":
        c1, c2, c3 = st.columns(3)
        a = c1.number_input("a (≠ 0):", value=2, step=1)
        b = c2.number_input("b:", value=40, step=1)
        c_eq = c3.number_input("Igual a c:", value=50, step=1)
        if a == 0: st.error("a deve ser diferente de zero.")
        elif st.button("Resolver"):
            x = (c_eq - b) / a
            txt = f"Equacao: {a}x + {b} = {c_eq} | Resultado: x = {x}"
            st.success(txt)
            st.download_button("Baixar PDF", gerar_pdf_simples("Algebra", [txt]), "algebra.pdf")

# --- GEOMETRIA ---
elif menu == "Geometria":
    st.header("📐 Geometria Espacial")
    fig = st.selectbox("Figura:", ["Esfera", "Cilindro", "Cubo"])
    r = st.number_input("Medida Principal (Raio/Lado):", value=10, step=1)
    if fig == "Esfera":
        vol = (4/3) * np.pi * (r**3)
        st.metric("Volume", f"{vol:.4f}")
    elif fig == "Cubo":
        vol = r**3
        st.metric("Volume", f"{vol}")
    if st.button("Gerar PDF"):
        st.download_button("Baixar", gerar_pdf_simples("Geometria", [f"Figura: {fig}", f"Medida: {r}"]), "geo.pdf")

# --- SISTEMAS ---
elif menu == "Sistemas":
    st.header("📏 Sistemas Ax = B")
    n = st.slider("Incognitas:", 2, 5, 2)
    mat_A = []
    vec_B = []
    for i in range(n):
        cols = st.columns(n+1)
        mat_A.append([cols[j].number_input(f"A{i}{j}", value=1.0 if i==j else 0.0) for j in range(n)])
        vec_B.append(cols[n].number_input(f"B{i}", value=1.0))
    if st.button("Resolver Sistema"):
        try:
            sol = np.linalg.solve(np.array(mat_A), np.array(vec_B))
            st.success(f"Solucoes: {sol}")
        except: st.error("Sistema sem solucao unica.")

# --- FINANCEIRO ---
elif menu == "Financeiro":
    st.header("💰 Matematica Financeira")
    capital = st.number_input("Capital Inicial:", value=1000, step=1)
    taxa = st.number_input("Taxa (%):", value=1.0) / 100
    tempo = st.number_input("Meses:", value=12, step=1)
    montante = capital * (1 + taxa)**tempo
    st.metric("Montante Final", f"R$ {montante:.2f}")

# --- GERADOR DE ATIVIDADES ---
elif menu == "Gerador de Atividades":
    st.header("📝 Atividades com Gabarito")
    qtd = st.slider("Quantidade:", 1, 15, 5)
    if st.button("Gerar Lista"):
        q, g = [], []
        for i in range(qtd):
            if random.choice(["alg", "geo"]) == "alg":
                ra, rx = random.randint(1, 10), random.randint(1, 10)
                rb = random.randint(1, 20); rc = (ra * rx) + rb
                q.append(f"{i+1}) Resolva: {ra}x + {rb} = {rc}")
                g.append(f"{i+1}) x = {rx}")
            else:
                l = random.randint(2, 10)
                q.append(f"{i+1}) Qual o volume de um cubo de lado {l}?")
                g.append(f"{i+1}) Volume = {l**3}")
        st.session_state.q, st.session_state.g = q, g
    if 'q' in st.session_state:
        for ex in st.session_state.q: st.write(ex)
        pdf = gerar_pdf_atividades(st.session_state.q, st.session_state.g)
        st.download_button("Baixar Lista + Gabarito", pdf, "atividades.pdf")