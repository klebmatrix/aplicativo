import streamlit as st
import math
import numpy as np
import os
import random
import re
from fpdf import FPDF

# --- CONFIGURAÇÃO ÚNICA DA PÁGINA ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

# --- 1. SEGURANÇA ---
def validar_acesso(pin_digitado):
    try:
        senha_aluno = str(st.secrets.get("acesso_aluno", "123456")).strip()
        senha_professor = str(st.secrets.get("chave_mestra", "admin123")).strip()
        if pin_digitado == senha_aluno: return "aluno"
        elif pin_digitado == senha_professor: return "admin"
    except: pass
    return "negado"

if 'perfil' not in st.session_state:
    st.session_state.perfil = None

# --- 2. LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Quantum Math Lab - Acesso")
    pin = st.text_input("PIN de Acesso:", type="password", key="login_pass")
    if st.button("Entrar"):
        acesso = validar_acesso(pin)
        if acesso != "negado":
            st.session_state.perfil = acesso
            st.rerun()
        else: st.error("Acesso negado.")
    st.stop()

# --- 3. BANCO DE QUESTÕES ALEATÓRIAS (GERADOR AUTO) ---
def gerar_questoes_auto(tema):
    q = []
    for _ in range(10):
        if tema == "Operações Básicas":
            op = random.choice(['+', '-', 'x', '/'])
            n1, n2 = random.randint(10, 99), random.randint(2, 12)
            if op == '+': q.append(f"{n1} + {n2} = ")
            elif op == '-': q.append(f"{n1+n2} - {n1} = ")
            elif op == 'x': q.append(f"{n1} x {n2} = ")
            else: q.append(f"{n1*n2} ÷ {n2} = ")
        elif tema == "Equação 1º Grau":
            a = random.randint(2, 9)
            res = a * random.randint(2, 10)
            q.append(f"{a}x = {res}")
        elif tema == "Equação 2º Grau":
            x1, x2 = random.randint(1, 5), random.randint(1, 5)
            q.append(f"x² - {x1+x2}x + {x1*x2} = 0")
    return q

# --- 4. INTERFACE PRINCIPAL ---
perfil = st.session_state.perfil
st.sidebar.title(f"🚀 {'Professor' if perfil == 'admin' else 'Estudante'}")

# Itens base (Aluno)
itens = ["Atividades (Drive)", "Expressões (PEMDAS)", "Equações (1º e 2º Grau)", "Cálculo de Funções", "Logaritmos", "Funções Aritméticas"]

# Adiciona itens do Professor ao topo
if perfil == "admin":
    itens = ["GERADOR AUTO (4x1)", "Gerador de Atividades (Manual)"] + itens + ["Sistemas Lineares", "Matrizes", "Financeiro"]

menu = st.sidebar.radio("Navegação:", itens)

if st.sidebar.button("Sair"):
    st.session_state.perfil = None
    st.rerun()

# --- MÓDULO: GERADOR AUTOMÁTICO 4x1 ---
if menu == "GERADOR AUTO (4x1)":
    st.header("🖨️ Gerador Instantâneo (4 por página)")
    tema_sel = st.selectbox("Tema:", ["Operações Básicas", "Equação 1º Grau", "Equação 2º Grau"])
    if st.button("Gerar PDF 4x1"):
        questoes = gerar_questoes_auto(tema_sel)
        pdf = FPDF()
        pdf.add_page()
        pos = [(10, 10), (110, 10), (10, 150), (110, 150)]
        for px, py in pos:
            pdf.rect(px, py, 95, 138)
            if os.path.exists("cabecalho.png"):
                pdf.image("cabecalho.png", x=px+2.5, y=py+2, w=90, h=0)
            pdf.set_font("Arial", 'B', 10); pdf.set_xy(px, py + 30)
            pdf.cell(95, 10, tema_sel.upper(), ln=True, align='C')
            pdf.set_font("Arial", size=9)
            for i in range(10):
                col, row = (0 if i < 5 else 48), (i % 5) * 16
                pdf.set_xy(px + 5 + col, py + 42 + row)
                pdf.cell(45, 10, f"{'abcdefghij'[i]}) {questoes[i]}")
        st.download_button("📥 Baixar PDF 4x1", pdf.output(dest='S').encode('latin-1', 'replace'), "4x1.pdf")

# --- MÓDULO: GERADOR DE ATIVIDADES (MANUAL) ---
elif menu == "Gerador de Atividades (Manual)":
    st.header("📄 Gerador Manual")
    titulo_pdf = st.text_input("Título:", "Atividade de Matemática")
    conteudo = st.text_area("Conteúdo (Use . para colunas):", height=300)
    if st.button("Gerar PDF"):
        pdf = FPDF()
        pdf.add_page()
        if os.path.exists("cabecalho.png"):
            pdf.image("cabecalho.png", x=12.5, y=8, w=185, h=0)
            pdf.set_y(52)
        else: pdf.set_y(15)
        pdf.set_font("Arial", 'B', 12); pdf.cell(0, 10, txt=titulo_pdf, ln=True, align='C'); pdf.ln(2)
        pdf.set_font("Arial", size=10); letra_idx = 0
        for linha in conteudo.split('\n'):
            txt = linha.strip()
            if not txt: continue
            match = re.match(r'^(\.+)', txt)
            if re.match(r'^\d+', txt): # Se começar com número, a próxima será letra
                pdf.ln(4); pdf.set_font("Arial", 'B', 11); pdf.multi_cell(0, 8, txt=txt); pdf.set_font("Arial", size=10); letra_idx = 0 
            elif match:
                num_p = len(match.group(1))
                if num_p > 1: pdf.set_y(pdf.get_y() - 8)
                pdf.set_x(10 + (num_p - 1) * 32)
                pdf.cell(32, 8, txt=f"{'abcdefghij'[letra_idx%10]}) {txt[num_p:].strip()}", ln=True)
                letra_idx += 1
            else: pdf.multi_cell(0, 8, txt=txt)
        st.download_button("📥 Baixar Lista", pdf.output(dest='S').encode('latin-1', 'replace'), "atividade.pdf")

# --- MÓDULOS DE CÁLCULO ---
elif menu == "Expressões (PEMDAS)":
    st.header("🧮 Calculadora PEMDAS")
    exp = st.text_input("Expressão:")
    if st.button("Resolver"):
        try: res = eval(exp.replace('^', '**'), {"math": math, "sqrt": math.sqrt})
        except: res = "Erro"
        st.success(f"Resultado: {res}")

elif menu == "Sistemas Lineares":
    st.header("⚖️ Sistemas 2x2")
    a1, b1, c1 = st.number_input("a1"), st.number_input("b1"), st.number_input("c1")
    a2, b2, c2 = st.number_input("a2"), st.number_input("b2"), st.number_input("c2")
    if st.button("Resolver Sistema"):
        try:
            res = np.linalg.solve(np.array([[a1, b1], [a2, b2]]), np.array([c1, c2]))
            st.success(f"x = {res[0]:.2f}, y = {res[1]:.2f}")
        except: st.error("Sem solução.")

elif menu == "Matrizes":
    st.header("📊 Determinante 2x2")
    m = [st.number_input(f"M{i}", value=0.0) for i in range(4)]
    if st.button("Calcular"):
        st.metric("Det", (m[0]*m[3]) - (m[1]*m[2]))

elif menu == "Financeiro":
    st.header("💰 Juros Compostos")
    c, i, t = st.number_input("Capital"), st.number_input("Taxa %")/100, st.number_input("Tempo")
    if st.button("Calcular"):
        st.success(f"Montante: R$ {c * (1+i)**t:.2f}")

elif menu == "Atividades (Drive)":
    st.link_button("📂 Abrir Drive", "https://drive.google.com/drive/folders/1NkFeom_k3LUJYAFVBBDu4GD5aYVeNEZc")