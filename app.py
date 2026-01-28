import streamlit as st
import math
import numpy as np
import os
import random
import re
from fpdf import FPDF

# --- CONFIGURAÇÃO ÚNICA (Evita o erro de desativação) ---
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
    pin = st.text_input("PIN de Acesso:", type="password")
    if st.button("Entrar"):
        acesso = validar_acesso(pin)
        if acesso != "negado":
            st.session_state.perfil = acesso
            st.rerun()
        else: st.error("Acesso negado.")
    st.stop()

# --- 3. BANCO DE QUESTÕES ALEATÓRIAS ---
def gerar_exercicios(tema):
    questoes = []
    for _ in range(10):
        if tema == "Equação 1º Grau":
            a = random.randint(2, 10); b = random.randint(1, 20)
            questoes.append(f"{a}x + {b} = {a * random.randint(1, 10) + b}")
        elif tema == "Equação 2º Grau":
            x1, x2 = random.randint(1, 5), random.randint(1, 5)
            questoes.append(f"x² - {x1+x2}x + {x1*x2} = 0")
        elif tema == "Expressões":
            questoes.append(f"({random.randint(2,10)} * {random.randint(2,5)}) + {random.randint(5,20)}")
        elif tema == "Matrizes/Sistemas":
            questoes.append(f"x+y={random.randint(5,15)}; x-y={random.randint(1,5)}")
    return questoes

# --- 4. INTERFACE E MENU ---
perfil = st.session_state.perfil
st.sidebar.title(f"🚀 {'Professor' if perfil == 'admin' else 'Estudante'}")

# Itens base para todos
itens = ["Atividades (Drive)", "Expressões (PEMDAS)", "Equações (1º e 2º Grau)", "Cálculo de Funções", "Logaritmos", "Funções Aritméticas"]

# Itens exclusivos do Professor
if perfil == "admin":
    itens = ["GERADOR AUTOMÁTICO (4x1)", "Gerador de Atividades (Manual)"] + itens + ["Sistemas Lineares", "Matrizes", "Financeiro"]

menu = st.sidebar.radio("Navegação:", itens)

if st.sidebar.button("Sair"):
    st.session_state.perfil = None
    st.rerun()

# --- MÓDULO: GERADOR AUTOMÁTICO 4x1 ---
if menu == "GERADOR AUTOMÁTICO (4x1)":
    st.header("🖨️ Gerador Instantâneo 4x1")
    tema_sel = st.selectbox("Tema:", ["Equação 1º Grau", "Equação 2º Grau", "Expressões", "Matrizes/Sistemas"])
    
    if st.button("Gerar PDF 4x1"):
        questoes = gerar_exercicios(tema_sel)
        pdf = FPDF()
        pdf.add_page()
        posicoes = [(10, 10), (110, 10), (10, 150), (110, 150)]
        
        for px, py in posicoes:
            pdf.rect(px, py, 95, 138)
            if os.path.exists("cabecalho.png"):
                # h=0 mantém a proporção original da imagem
                pdf.image("cabecalho.png", x=px+2.5, y=py+2, w=90, h=0)
            
            pdf.set_font("Arial", 'B', 10)
            pdf.set_xy(px, py + 30)
            pdf.cell(95, 10, tema_sel.upper(), ln=True, align='C')
            
            pdf.set_font("Arial", size=9)
            for i in range(10):
                col = 0 if i < 5 else 48
                row = (i % 5) * 16
                pdf.set_xy(px + 5 + col, py + 42 + row)
                pdf.cell(45, 10, f"{'abcdefghij'[i]}) {questoes[i]}")
        
        st.download_button("📥 Baixar PDF 4x1", pdf.output(dest='S').encode('latin-1', 'replace'), "4x1.pdf")

# --- MÓDULO: GERADOR MANUAL ---
elif menu == "Gerador de Atividades (Manual)":
    st.header("📄 Criador de Listas Customizadas")
    titulo = st.text_input("Título:", "Atividade")
    conteudo = st.text_area("Conteúdo (Use . para colunas):", height=200)
    
    if st.button("Gerar PDF"):
        pdf = FPDF()
        pdf.add_page()
        if os.path.exists("cabecalho.png"):
            pdf.image("cabecalho.png", x=12.5, y=8, w=185, h=0)
            pdf.set_y(50)
        else: pdf.set_y(15)
        
        pdf.set_font("Arial", 'B', 12); pdf.cell(0, 10, txt=titulo, ln=True, align='C')
        pdf.set_font("Arial", size=10); letra_idx = 0
        
        for linha in conteudo.split('\n'):
            txt = linha.strip()
            if not txt: continue
            match = re.match(r'^(\.+)', txt)
            if re.match(r'^\d+', txt): # Se começar com número
                pdf.ln(2); pdf.set_font("Arial", 'B', 11); pdf.multi_cell(0, 7, txt=txt)
                pdf.set_font("Arial", size=10); letra_idx = 0
            elif match: # Colunas
                n_p = len(match.group(1))
                if n_p > 1: pdf.set_y(pdf.get_y() - 7)
                pdf.set_x(10 + (n_p - 1) * 32)
                pdf.cell(32, 7, txt=f"{'abcdefghij'[letra_idx%10]}) {txt[n_p:].strip()}", ln=True)
                letra_idx += 1
            else: pdf.multi_cell(0, 7, txt=txt)
        st.download_button("📥 Baixar Lista", pdf.output(dest='S').encode('latin-1'), "lista.pdf")

# --- REATIVAÇÃO DOS MÓDULOS DE CÁLCULO ---
elif menu == "Sistemas Lineares":
    st.header("⚖️ Sistema 2x2")
    a1 = st.number_input("a1", value=1.0); b1 = st.number_input("b1", value=1.0); c1 = st.number_input("c1", value=5.0)
    a2 = st.number_input("a2", value=1.0); b2 = st.number_input("b2", value=-1.0); c2 = st.number_input("c2", value=1.0)
    if st.button("Resolver"):
        try:
            res = np.linalg.solve(np.array([[a1, b1], [a2, b2]]), np.array([c1, c2]))
            st.success(f"x = {res[0]:.2f}, y = {res[1]:.2f}")
        except: st.error("Erro no sistema.")

elif menu == "Matrizes":
    st.header("📊 Determinante 2x2")
    m = [st.number_input(f"M{i}", value=float(i)) for i in range(4)]
    if st.button("Calcular"):
        st.metric("Det", (m[0]*m[3]) - (m[1]*m[2]))

elif menu == "Equações (1º e 2º Grau)":
    st.header("📐 Resolução de Equações")
    # (Lógica de cálculo simplificada para reativação rápida)
    st.write("Insira os coeficientes para calcular.")

elif menu == "Financeiro":
    st.header("💰 Juros Compostos")
    cap = st.number_input("Capital", 1000.0); tx = st.number_input("Taxa %", 5.0)/100; t = st.number_input("Tempo", 12.0)
    if st.button("Calcular Montante"):
        st.success(f"R$ {cap * (1+tx)**t:.2f}")

elif menu == "Atividades (Drive)":
    st.link_button("📂 Abrir Drive", "https://drive.google.com/drive/folders/1NkFeom_k3LUJYAFVBBDu4GD5aYVeNEZc")