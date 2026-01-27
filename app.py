import streamlit as st
import math
import numpy as np
import os
import re
from fpdf import FPDF

# --- 1. SEGURANÇA ---
def validar_acesso(pin_digitado):
    try:
        senha_aluno = str(st.secrets["acesso_aluno"]).strip()
        senha_professor = str(st.secrets["chave_mestra"]).strip()
        if pin_digitado == senha_aluno: return "aluno"
        elif pin_digitado == senha_professor: return "admin"
    except: return "negado"
    return "negado"

st.set_page_config(page_title="Quantum Math Lab", layout="wide")
if 'perfil' not in st.session_state: st.session_state.perfil = None

# --- 2. LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Quantum Math Lab")
    pin = st.text_input("PIN de Acesso:", type="password", key="login_pass")
    if st.button("Entrar"):
        acesso = validar_acesso(pin)
        if acesso != "negado":
            st.session_state.perfil = acesso
            st.rerun()
        else: st.error("Acesso negado.")
    st.stop()

# --- 3. INTERFACE ---
else:
    perfil = st.session_state.perfil
    st.sidebar.title(f"🚀 {'Professor' if perfil == 'admin' else 'Estudante'}")
    
    itens = ["Atividades (Drive)", "Expressões (PEMDAS)", "Equações (1º e 2º Grau)", "Cálculo de Funções", "Logaritmos", "Funções Aritméticas"]
    if perfil == "admin":
        itens += ["Gerador de Atividades", "Sistemas Lineares", "Matrizes", "Financeiro"]
        
    menu = st.sidebar.radio("Navegação:", itens)
    
    if st.sidebar.button("Sair"):
        st.session_state.perfil = None
        st.rerun()

    # --- ATIVIDADES DRIVE ---
    if menu == "Atividades (Drive)":
        st.header("📝 Pasta de Atividades")
        st.link_button("📂 Abrir Google Drive", "https://drive.google.com/drive/folders/1NkFeom_k3LUJYAFVBBDu4GD5aYVeNEZc?usp=drive_link")

    # --- EXPRESSÕES ---
    elif menu == "Expressões (PEMDAS)":
        st.header("🧮 Calculadora de Expressões")
        exp = st.text_input("Digite a expressão:")
        if st.button("Resolver"):
            try:
                res = eval(exp.replace('^', '**'), {"__builtins__": None}, {"math": math, "sqrt": math.sqrt})
                st.success(f"Resultado: {res}")
            except: st.error("Erro na expressão.")

    # --- EQUAÇÕES ---
    elif menu == "Equações (1º e 2º Grau)":
        st.header("📐 Resolução de Equações")
        grau = st.selectbox("Grau:", ["1º Grau", "2º Grau"])
        if grau == "1º Grau":
            a1 = st.number_input("a:", value=1.0); b1 = st.number_input("b:", value=0.0)
            if st.button("Calcular"): st.success(f"x = {-b1/a1:.2f}") if a1 != 0 else st.error("a=0")
        else:
            a2 = st.number_input("a", value=1.0); b2 = st.number_input("b"); c2 = st.number_input("c")
            if st.button("Calcular"):
                delta = b2**2 - 4*a2*c2
                if delta >= 0:
                    st.success(f"x1 = {(-b2 + math.sqrt(delta))/(2*a2):.2f}, x2 = {(-b2 - math.sqrt(delta))/(2*a2):.2f}")
                else: st.error("Sem raízes reais.")

    # --- LOGARITMOS ---
    elif menu == "Logaritmos":
        st.header("🔢 Logaritmos")
        num = st.number_input("Logaritmando:", value=100.0); base = st.number_input("Base:", value=10.0)
        if st.button("Calcular"):
            try: st.success(f"Resultado: {math.log(num, base):.4f}")
            except: st.error("Erro no cálculo.")

    # --- FUNÇÕES ARITMÉTICAS ---
    elif menu == "Funções Aritméticas":
        st.header("🔍 Divisores")
        n = st.number_input("Número n:", min_value=1, value=12)
        if st.button("Ver Divisores"):
            divs = [d for d in range(1, n+1) if n % d == 0]
            st.write(f"Divisores: {divs}")

# --- GERADOR DE ATIVIDADES (CABEÇALHO AJUSTADO E 6 COLUNAS) ---
    elif menu == "Gerador de Atividades":
        st.header("📄 Gerador de Atividades")
        
        titulo_pdf = st.text_input("Título:", "Atividade de Matemática")
        conteudo = st.text_area("Conteúdo:", height=300)
        
        if st.button("Gerar PDF"):
            if conteudo:
                pdf = FPDF()
                pdf.add_page()
                
                # 1. CABEÇALHO (Tamanho equilibrado: 170)
                if os.path.exists("cabecalho.png"):
                    # Centralizado: (210mm folha - 170mm imagem) / 2 = 20mm de margem x
                    pdf.image("cabecalho.png", x=20, y=8, w=170) 
                    pdf.set_y(42) # Espaço ajustado para o título não bater na imagem
                else:
                    pdf.set_y(15)
                
                # 2. TÍTULO
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(0, 10, txt=titulo_pdf, ln=True, align='C')
                pdf.ln(2)
                
                # 3. LÓGICA DE 1 A 6 COLUNAS (ALINHADO À ESQUERDA)
                pdf.set_font("Arial", size=10)
                letras = "abcdefghijklmnopqrstuvwxyz"
                letra_idx = 0
                
                for linha in conteudo.split('\n'):
                    txt = linha.strip()
                    if not txt: continue
                    
                    # Detecta pontos no início
                    match = re.match(r'^(\.+)', txt)
                    num_pontos = len(match.group(1)) if match else 0
                    
                    # QUESTÃO (Número) - SEM RECUO
                    if re.match(r'^\d+', txt):
                        pdf.ln(4)
                        pdf.set_font("Arial", 'B', 11)
                        pdf.set_x(10) # Margem esquerda total
                        pdf.multi_cell(0, 8, txt=txt)
                        pdf.set_font("Arial", size=10)
                        letra_idx = 0 
                    
                    # COLUNAS (1 a 6)
                    elif num_pontos > 0:
                        item = txt[num_pontos:].strip()
                        prefixo = f"{letras[letra_idx % 26]}) "
                        
                        if num_pontos > 1:
                            pdf.set_y(pdf.get_y() - 8)
                        
                        # Cada coluna tem 32mm de largura
                        pos_x = 10 + (num_pontos - 1) * 32
                        pdf.set_x(pos_x)
                        pdf.cell(32, 8, txt=f"{prefixo}{item}", ln=True)
                        letra_idx += 1
                    
                    # TEXTO NORMAL
                    else:
                        pdf.set_x(10)
                        pdf.multi_cell(0, 8, txt=txt)
                
                pdf_bytes = pdf.output(dest='S').encode('latin-1', 'replace')
                st.download_button("📥 Baixar PDF", data=pdf_bytes, file_name="atividade.pdf")
    # --- FINANCEIRO ---
    elif menu == "Financeiro":
        st.header("💰 Financeiro")
        c = st.number_input("Capital:", value=1000.0); tx = st.number_input("Taxa %:", value=5.0); t = st.number_input("Meses:", value=12.0)
        if st.button("Calcular"): st.success(f"Montante: R$ {c * (1 + (tx/100))**t:.2f}")

    # --- MATRIZES ---
    elif menu == "Matrizes":
        st.header("📊 Determinante 2x2")
        m11 = st.number_input("M11", value=1.0); m12 = st.number_input("M12", value=0.0)
        m21 = st.number_input("M21", value=0.0); m22 = st.number_input("M22", value=1.0)
        if st.button("Calcular Det"): st.metric("Det", (m11*m22) - (m12*m21))