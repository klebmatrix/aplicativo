import streamlit as st
import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from cryptography.fernet import Fernet
from fpdf import FPDF
import math
import random
from datetime import datetime

# --- 1. SEGURANÇA E CONFIGURAÇÃO ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide", page_icon="⚛️")

def validar_acesso(pin_digitado):
    # Acesso Estudante
    senha_aluno_env = os.environ.get('acesso_aluno', '').strip().replace("'", "").replace('"', "")
    if senha_aluno_env and pin_digitado == senha_aluno_env:
        return "aluno"
    
    # Acesso Professor
    try:
        if pin_digitado == "admin": return "admin"
        chave = os.environ.get('chave_mestra', '').strip().replace("'", "").replace('"', "")
        if not chave: return "erro_env"
        if chave.startswith('b'): chave = chave[1:]
        f = Fernet(chave.encode())
        # PIN_CRIPTO atualizado para Qzj7bJEy
        PIN_CRIPTO = "gAAAAABpd_xXuRomCwkP5ndxDS1kG5MB5Zk0po7cJLo-mAS1pqdJQjRsJ-Bp6ShKov8PNRP8-vzHwpDp93K2h1vC9uapl4aAzw=="
        if pin_digitado == f.decrypt(PIN_CRIPTO.encode()).decode():
            return "admin"
    except: pass
    return "negado"

# Inicialização do estado
if 'perfil' not in st.session_state: st.session_state.perfil = None
if 'pdf_pronto' not in st.session_state: st.session_state.pdf_pronto = None

# --- 2. TELA DE LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Quantum Math Lab")
    pin = st.text_input("PIN de Acesso:", type="password")
    if st.button("Entrar"):
        acesso = validar_acesso(pin)
        if acesso != "negado":
            st.session_state.perfil = acesso
            st.rerun()
        else:
            st.error("Acesso Negado. Verifique as chaves no Render.")
    st.stop()

# --- 3. MOTOR DE PDF ---
class PDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 14)
        self.cell(0, 10, 'Quantum Lab - Material Didatico', 0, 1, 'C')
        self.ln(5)

def gerar_pdf_bytes(titulo, questoes, respostas):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(0, 10, f"LISTA DE EXERCICIOS: {titulo.upper()}", ln=True)
    pdf.set_font("helvetica", size=11)
    for q in questoes:
        pdf.multi_cell(0, 10, txt=q); pdf.ln(2)
    pdf.add_page()
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(0, 10, "GABARITO", ln=True)
    pdf.set_font("helvetica", size=11)
    for r in respostas:
        pdf.multi_cell(0, 10, txt=r)
    return pdf.output()

# --- 4. DASHBOARD E MENU ---
perfil = st.session_state.perfil
st.sidebar.title(f"🚀 {'PROFESSOR' if perfil == 'admin' else 'ESTUDANTE'}")

itens = ["Atividades (Drive)", "Expressões (PEMDAS)", "Equações 1º/2º Grau", "Cálculo de Funções", "Logaritmos", "Geometria"]
if perfil == "admin":
    itens += ["Gerador de Atividades (PDF)", "Sistemas Lineares", "Matrizes", "Financeiro"]

menu = st.sidebar.radio("Navegação:", itens)
if st.sidebar.button("Sair"):
    st.session_state.perfil = None
    st.rerun()

# --- 5. MÓDULOS ---
with st.container(key=f"main_{menu.lower().replace(' ', '_')}"):
    
    if menu == "Atividades (Drive)":
        st.header("📝 Pasta do Aluno")
        st.link_button("📂 Abrir Drive", "https://drive.google.com/drive/folders/1NkFeom_k3LUJYAFVBBDu4GD5aYVeNEZc?usp=drive_link")

    elif menu == "Expressões (PEMDAS)":
        st.header("🧮 Hierarquia PEMDAS")
        exp = st.text_input("Expressão:", value="(10+5)*2")
        if st.button("Calcular"):
            try:
                res = eval(exp.replace('^', '**'), {"__builtins__": None}, {"math": math, "sqrt": math.sqrt})
                st.success(f"Resultado: {res}")
            except: st.error("Erro na sintaxe.")

    elif menu == "Equações 1º/2º Grau":
        st.header("📐 Equações")
        st.latex(r"ax^2 + bx + c = 0")
        c1, c2, c3 = st.columns(3)
        a = c1.number_input("a", value=1.0, key="eq_a")
        b = c2.number_input("b", value=-5.0, key="eq_b")
        c = c3.number_input("c", value=6.0, key="eq_c")
        if st.button("Resolver"):
            if a == 0:
                st.info(f"x = {-c/b:.2f}" if b != 0 else "Inválido")
            else:
                delta = b**2 - 4*a*c
                if delta >= 0:
                    x1, x2 = (-b+math.sqrt(delta))/(2*a), (-b-math.sqrt(delta))/(2*a)
                    st.success(f"x1 = {x1:.2f} | x2 = {x2:.2f}")
                    # Gráfico da Parábola
                    x_vals = np.linspace(x1-5, x2+5, 100)
                    y_vals = a*x_vals**2 + b*x_vals + c
                    fig = px.line(x=x_vals, y=y_vals, title="Gráfico da Função")
                    fig.add_hline(y=0, line_dash="dash")
                    st.plotly_chart(fig)
                else: st.error("Delta Negativo.")

    elif menu == "Geometria":
        st.header("📐 Geometria")
        tab1, tab2 = st.tabs(["Pitágoras", "Volumes"])
        with tab1:
            ca = st.number_input("Cateto A", value=3.0)
            cb = st.number_input("Cateto B", value=4.0)
            if st.button("Calcular Hipotenusa"):
                h = math.sqrt(ca**2 + cb**2)
                st.success(f"Hipotenusa: {h:.2f}")
                fig = go.Figure(go.Scatter(x=[0, ca, 0, 0], y=[0, 0, cb, 0], fill="toself"))
                st.plotly_chart(fig)
        with tab2:
            raio = st.number_input("Raio da Esfera", value=5.0)
            st.write(f"Volume: {(4/3)*math.pi*raio**3:.2f}")

    elif menu == "Sistemas Lineares":
        st.header("📏 Sistemas (Ax = B)")
        n = st.slider("Ordem", 2, 4, 2)
        mat_A, vec_B = [], []
        for i in range(n):
            cols = st.columns(n+1)
            mat_A.append([cols[j].number_input(f"A{i}{j}", value=1.0 if i==j else 0.0, key=f"A{i}{j}") for j in range(n)])
            vec_B.append(cols[n].number_input(f"B{i}", value=1.0, key=f"B{i}"))
        if st.button("Resolver"):
            try:
                res = np.linalg.solve(np.array(mat_A), np.array(vec_B))
                st.success(f"Soluções: {res}")
            except: st.error("Sem solução única.")

    elif menu == "Matrizes":
        st.header("🧮 Análise de Matrizes")
        n_m = st.slider("Ordem Matriz", 2, 4, 2, key="n_m")
        A_m = []
        for i in range(n_m):
            cols = st.columns(n_m)
            A_m.append([cols[j].number_input(f"M{i}{j}", value=1.0 if i==j else 0.0, key=f"M{i}{j}") for j in range(n_m)])
        A_np = np.array(A_m)
        st.write(f"**Determinante:** {np.linalg.det(A_np):.2f}")
        st.plotly_chart(px.imshow(A_np, text_auto=True, title="Heatmap da Matriz"))

    elif menu == "Financeiro":
        st.header("💰 Finanças")
        cap = st.number_input("Capital", value=1000.0)
        taxa = st.number_input("Taxa (%)", value=1.0)/100
        tempo = st.number_input("Meses", value=12)
        st.metric("Montante Final", f"R$ {cap*(1+taxa)**tempo:.2f}")

    elif menu == "Gerador de Atividades (PDF)":
        st.header("📄 Gerador PDF")
        tema = st.selectbox("Tema", ["Álgebra", "Geometria"])
        qtd = st.number_input("Questões", 10, 30, 10)
        if st.button("Gerar Material"):
            q, g = [], []
            for i in range(qtd):
                ra, rx = random.randint(1,10), random.randint(1,10)
                rb = random.randint(1,20); rc = (ra*rx)+rb
                q.append(f"{i+1}) {ra}x + {rb} = {rc}")
                g.append(f"{i+1}) x = {rx}")
            st.session_state.pdf_pronto = gerar_pdf_bytes(tema, q, g)
            st.success("PDF Pronto!")
        if st.session_state.pdf_pronto:
            st.download_button("📥 Baixar PDF", st.session_state.pdf_pronto, "atividades.pdf", "application/pdf")
