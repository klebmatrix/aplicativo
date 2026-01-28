import streamlit as st
import math
import numpy as np
import os
import random
import re
from fpdf import FPDF

# --- 1. CONFIGURAÇÃO ÚNICA DA PÁGINA ---
# Evita erro de duplicidade e define o layout largo para melhor visualização
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

# --- 2. SEGURANÇA E ACESSO ---
def validar_acesso(pin_digitado):
    # Senhas padrão para acesso local (Fallback)
    SENHA_ALUNO_LOCAL = "123456"
    SENHA_PROF_LOCAL = "12345678"

    try:
        # Tenta buscar dos Secrets (Render/Streamlit Cloud)
        senha_aluno = str(st.secrets.get("acesso_aluno", SENHA_ALUNO_LOCAL)).strip()
        senha_professor = str(st.secrets.get("chave_mestra", SENHA_PROF_LOCAL)).strip()
    except:
        senha_aluno = SENHA_ALUNO_LOCAL
        senha_professor = SENHA_PROF_LOCAL
        
    if pin_digitado == senha_aluno: return "aluno"
    elif pin_digitado == senha_professor: return "admin"
    return "negado"

if 'perfil' not in st.session_state:
    st.session_state.perfil = None

# --- 3. TELA DE LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Quantum Math Lab - Login")
    pin = st.text_input("PIN de Acesso:", type="password", key="login_pass")
    if st.button("Entrar"):
        acesso = validar_acesso(pin)
        if acesso != "negado":
            st.session_state.perfil = acesso
            st.rerun()
        else:
            st.error("PIN incorreto.")
    st.stop()

# --- 4. FUNÇÕES DE APOIO (GERADOR) ---
def gerar_exercicios_aleatorios(tema):
    questoes = []
    for _ in range(10):
        if tema == "Operações Básicas":
            op = random.choice(['+', '-', 'x', '÷'])
            n1, n2 = random.randint(10, 99), random.randint(2, 12)
            if op == '+': questoes.append(f"{n1} + {n2} = ")
            elif op == '-': questoes.append(f"{n1+n2} - {n1} = ")
            elif op == 'x': questoes.append(f"{n1} x {n2} = ")
            else: questoes.append(f"{n1*n2} ÷ {n2} = ")
        elif tema == "Equação 1º Grau":
            a = random.randint(2, 9)
            res = a * random.randint(2, 10)
            questoes.append(f"{a}x = {res}")
        elif tema == "Equação 2º Grau":
            x1, x2 = random.randint(1, 5), random.randint(1, 5)
            questoes.append(f"x² - {x1+x2}x + {x1*x2} = 0")
    return questoes

# --- 5. INTERFACE PRINCIPAL ---
perfil = st.session_state.perfil
st.sidebar.title(f"🚀 {'Professor' if perfil == 'admin' else 'Estudante'}")

# Organização do Menu Lateral
if perfil == "admin":
    itens_menu = [
        "GERADOR AUTO (4x1)", 
        "Gerador Manual (Atividades)", 
        "Sistemas Lineares", 
        "Matrizes", 
        "Financeiro",
        "Atividades (Drive)", 
        "Expressões (PEMDAS)", 
        "Equações", 
        "Cálculo de Funções", 
        "Logaritmos"
    ]
else:
    itens_menu = [
        "Atividades (Drive)", 
        "Expressões (PEMDAS)", 
        "Equações", 
        "Cálculo de Funções", 
        "Logaritmos"
    ]

menu = st.sidebar.radio("Navegação:", itens_menu)

if st.sidebar.button("Sair"):
    st.session_state.perfil = None
    st.rerun()

# --- 6. MÓDULO: GERADOR AUTOMÁTICO 4x1 ---
if menu == "GERADOR AUTO (4x1)":
    st.header("🖨️ Gerador Instantâneo (4 blocos)")
    tema_sel = st.selectbox("Selecione o Conteúdo:", ["Operações Básicas", "Equação 1º Grau", "Equação 2º Grau"])
    
    if st.button("Gerar PDF 4x1"):
        questoes = gerar_exercicios_aleatorios(tema_sel)
        pdf = FPDF()
        pdf.add_page()
        # Define os quadrantes (x, y)
        posicoes = [(10, 10), (110, 10), (10, 150), (110, 150)]
        
        for px, py in posicoes:
            pdf.rect(px, py, 95, 138) # Borda do bloco
            if os.path.exists("cabecalho.png"):
                pdf.image("cabecalho.png", x=px+2.5, y=py+2, w=90, h=0)
            
            pdf.set_font("Arial", 'B', 10)
            pdf.set_xy(px, py + 30)
            pdf.cell(95, 10, tema_sel.upper(), ln=True, align='C')
            
            pdf.set_font("Arial", size=9)
            for i in range(10):
                col, row = (0 if i < 5 else 48), (i % 5) * 16
                pdf.set_xy(px + 5 + col, py + 42 + row)
                pdf.cell(45, 10, f"{'abcdefghij'[i]}) {questoes[i]}")
        
        st.download_button("📥 Baixar Atividade 4x1", pdf.output(dest='S').encode('latin-1', 'replace'), "4x1_auto.pdf")

# --- 7. MÓDULO: GERADOR MANUAL ---
elif menu == "Gerador Manual (Atividades)":
    st.header("📄 Criar Atividade Personalizada")
    titulo_pdf = st.text_input("Título:", "Atividade de Matemática")
    conteudo = st.text_area("Digite o conteúdo (Use . para colunas):", height=300)
    
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
            
            match_pontos = re.match(r'^(\.+)', txt)
            if re.match(r'^\d+', txt): # Inicia com número
                pdf.ln(4); pdf.set_font("Arial", 'B', 11); pdf.multi_cell(0, 8, txt=txt)
                pdf.set_font("Arial", size=10); letra_idx = 0 
            elif match_pontos: # Inicia com pontos (coluna)
                num_p = len(match_pontos.group(1))
                if num_p > 1: pdf.set_y(pdf.get_y() - 8)
                pdf.set_x(10 + (num_p - 1) * 32)
                pdf.cell(32, 8, txt=f"{'abcdefghij'[letra_idx%10]}) {txt[num_p:].strip()}", ln=True)
                letra_idx += 1
            else: pdf.multi_cell(0, 8, txt=txt)
        st.download_button("📥 Baixar PDF Customizado", pdf.output(dest='S').encode('latin-1', 'replace'), "atividade.pdf")

# --- 8. OUTROS MÓDULOS ---
elif menu == "Sistemas Lineares":
    st.header("⚖️ Sistemas 2x2")
    a1 = st.number_input("a1", value=1.0); b1 = st.number_input("b1", value=1.0); c1 = st.number_input("c1", value=5.0)
    a2 = st.number_input("a2", value=1.0); b2 = st.number_input("b2", value=-1.0); c2 = st.number_input("c2", value=1.0)
    if st.button("Resolver"):
        try:
            res = np.linalg.solve(np.array([[a1, b1], [a2, b2]]), np.array([c1, c2]))
            st.success(f"Solução: x = {res[0]:.2f}, y = {res[1]:.2f}")
        except: st.error("Erro no sistema.")

elif menu == "Financeiro":
    st.header("💰 Juros Compostos")
    cap = st.number_input("Capital Inicial:", value=1000.0)
    tax = st.number_input("Taxa (%):", value=5.0) / 100
    tem = st.number_input("Tempo (meses):", value=12.0)
    if st.button("Calcular"):
        m = cap * (1 + tax)**tem
        st.success(f"Montante Final: R$ {m:.2f}")

elif menu == "Atividades (Drive)":
    st.link_button("📂 Abrir Drive", "https://drive.google.com/drive/folders/1NkFeom_k3LUJYAFVBBDu4GD5aYVeNEZc")