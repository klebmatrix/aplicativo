
import streamlit as st
import math
import numpy as np
import os
import random
from fpdf import FPDF
import re

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

# --- 1. SEGURANÇA (PIN) ---
def validar_acesso(pin_digitado):
    # Tenta buscar nos Secrets (Render/Streamlit Cloud)
    senha_aluno = str(st.secrets.get("acesso_aluno", "123456")).strip()
    senha_professor = str(st.secrets.get("chave_mestra", "admin123")).strip()
    
    if pin_digitado == senha_aluno:
        return "aluno"
    elif pin_digitado == senha_professor:
        return "admin"
    return "negado"

if 'perfil' not in st.session_state:
    st.session_state.perfil = None

# --- 2. TELA DE LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Quantum Math Lab - Acesso")
    pin = st.text_input("Digite seu PIN:", type="password")
    if st.button("Entrar"):
        acesso = validar_acesso(pin)
        if acesso != "negado":
            st.session_state.perfil = acesso
            st.rerun()
        else:
            st.error("PIN incorreto!")
    st.stop()

# --- 3. FUNÇÕES DE APOIO (GERAÇÃO ALEATÓRIA) ---
def criar_questoes(tema):
    q = []
    for _ in range(10):
        if tema == "Equação 1º Grau":
            a, b = random.randint(2, 9), random.randint(1, 20)
            q.append(f"{a}x + {b} = {a*random.randint(2,6) + b}")
        elif tema == "Equação 2º Grau":
            x1, x2 = random.randint(1, 4), random.randint(1, 5)
            q.append(f"x² - {x1+x2}x + {x1*x2} = 0")
        elif tema == "Expressões Numéricas":
            q.append(f"({random.randint(2,10)} * {random.randint(2,5)}) + {random.randint(10,30)} / 2")
        elif tema == "Potência e Raízes":
            q.append(f"{random.randint(2,5)}^{random.randint(2,3)} + √{random.choice([16,25,36,49,64,81,100])}")
        elif tema == "Sistemas":
            s = random.randint(10, 20); d = random.randint(2, 6)
            q.append(f"x+y={s}; x-y={d}")
        elif tema == "Matrizes":
            q.append(f"Det [{random.randint(1,5)},{random.randint(1,5)};{random.randint(1,5)},{random.randint(1,5)}]")
    return q

# --- 4. INTERFACE PRINCIPAL ---
perfil = st.session_state.perfil
st.sidebar.title(f"🚀 {'PROFESSOR' if perfil == 'admin' else 'ALUNO'}")

# MENU DINÂMICO
itens_menu = ["Atividades (Drive)", "Expressões (PEMDAS)", "Equações", "Cálculo de Funções", "Logaritmos", "Funções Aritméticas"]

if perfil == "admin":
    # Colocando os geradores de volta no topo para o professor
    itens_menu = ["GERADOR AUTOMÁTICO (4x1)", "Gerador de Listas (PDF)"] + itens_menu + ["Sistemas Lineares", "Matrizes", "Financeiro"]

escolha = st.sidebar.radio("Navegação:", itens_menu)

if st.sidebar.button("Encerrar Sessão"):
    st.session_state.perfil = None
    st.rerun()

# --- MÓDULO: GERADOR AUTOMÁTICO 4x1 ---
if escolha == "GERADOR AUTOMÁTICO (4x1)":
    st.header("🖨️ Gerador Instantâneo (4 por folha)")
    st.info("Gera 4 blocos idênticos com questões aleatórias e o cabeçalho oficial.")
    
    tema_sel = st.selectbox("Selecione o Tema:", ["Equação 1º Grau", "Equação 2º Grau", "Expressões Numéricas", "Potência e Raízes", "Sistemas", "Matrizes"])
    
    if st.button("Gerar e Visualizar PDF"):
        questoes = criar_questoes(tema_sel)
        pdf = FPDF()
        pdf.add_page()
        
        # Coordenadas dos 4 blocos (x, y)
        posicoes = [(10, 10), (110, 10), (10, 150), (110, 150)]
        
        for px, py in posicoes:
            pdf.rect(px, py, 95, 138) # Borda do quadrante
            
            # Cabeçalho Proporcional (h=0 evita distorção)
            if os.path.exists("cabecalho.png"):
                pdf.image("cabecalho.png", x=px+2.5, y=py+2, w=90, h=0)
            
            pdf.set_font("Arial", 'B', 10)
            pdf.set_xy(px, py + 30) # Ajustado para não sobrepor imagem
            pdf.cell(95, 8, tema_sel.upper(), ln=True, align='C')
            
            pdf.set_font("Arial", size=9)
            letras = "abcdefghij"
            for i in range(10):
                coluna = 0 if i < 5 else 48
                linha = (i % 5) * 16
                pdf.set_xy(px + 5 + coluna, py + 42 + linha)
                pdf.cell(45, 10, f"{letras[i]}) {questoes[i]}")

        pdf_bytes = pdf.output(dest='S').encode('latin-1', 'replace')
        st.download_button("📥 Baixar PDF 4x1", data=pdf_bytes, file_name="atividade_4x1.pdf")

# --- MÓDULO: GERADOR DE LISTAS PDF (CUSTOMIZADO) ---
elif escolha == "Gerador de Listas (PDF)":
    st.header("📄 Criador de Listas Customizadas")
    titulo = st.text_input("Título da Atividade:", "Lista de Exercícios")
    conteudo = st.text_area("Digite as questões (Use . para colunas):", height=250)
    
    if st.button("Gerar PDF da Lista"):
        pdf = FPDF()
        pdf.add_page()
        if os.path.exists("cabecalho.png"):
            pdf.image("cabecalho.png", x=12.5, y=8, w=185, h=0)
            pdf.set_y(50)
        else: pdf.set_y(15)
        
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, txt=titulo, ln=True, align='C')
        pdf.set_font("Arial", size=10)
        
        letra_idx = 0
        for linha in conteudo.split('\n'):
            txt = linha.strip()
            if not txt: continue
            match = re.match(r'^(\.+)', txt)
            
            if re.match(r'^\d+', txt): # Início com número (Questão)
                pdf.ln(2); pdf.set_font("Arial", 'B', 11)
                pdf.multi_cell(0, 7, txt=txt)
                pdf.set_font("Arial", size=10); letra_idx = 0
            elif match: # Colunas (Regra das letras a, b, c)
                n_p = len(match.group(1))
                if n_p > 1: pdf.set_y(pdf.get_y() - 7)
                pdf.set_x(10 + (n_p - 1) * 32)
                pdf.cell(32, 7, txt=f"{'abcdefghij'[letra_idx%10]}) {txt[n_p:].strip()}", ln=True)
                letra_idx += 1
            else:
                pdf.multi_cell(0, 7, txt=txt)
        
        st.download_button("📥 Baixar Lista", pdf.output(dest='S').encode('latin-1'), "lista_exercicios.pdf")

# --- MANTENDO OS OUTROS MÓDULOS DE CÁLCULO ---
elif escolha == "Atividades (Drive)":
    st.header("📂 Google Drive")
    st.link_button("Abrir Pasta de Atividades", "https://drive.google.com/drive/folders/1NkFeom_k3LUJYAFVBBDu4GD5aYVeNEZc")

elif escolha == "Equações":
    st.header("📐 Calculadora de Equações")
    # ... (lógica de cálculo de 1º e 2º grau)
    st.write("Módulo de cálculo ativo.")

# (Restante dos módulos como Matrizes, Sistemas e Financeiro seguem a mesma lógica)