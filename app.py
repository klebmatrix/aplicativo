import streamlit as st
import math
import numpy as np
import os
import random
import re
from fpdf import FPDF

# --- CONFIGURAÇÃO DA PÁGINA (CHAMADA ÚNICA) ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

# --- 1. SEGURANÇA ---
def validar_acesso(pin_digitado):
    try:
        # Tenta buscar dos Secrets (Fallback para local se não houver secrets)
        senha_aluno = str(st.secrets.get("acesso_aluno", "123456")).strip()
        senha_professor = str(st.secrets.get("chave_mestra", "12345678")).strip()
        
        if pin_digitado == senha_aluno: return "aluno"
        elif pin_digitado == senha_professor: return "admin"
    except:
        # Se estiver rodando puramente local sem secrets.toml
        if pin_digitado == "123456": return "aluno"
        elif pin_digitado == "12345678": return "admin"
    return "negado"

if 'perfil' not in st.session_state: 
    st.session_state.perfil = None

# --- 2. LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Quantum Math Lab")
    pin = st.text_input("PIN de Acesso:", type="password", key="login_pass")
    if st.button("Entrar"):
        acesso = validar_acesso(pin)
        if acesso != "negado":
            st.session_state.perfil = acesso
            st.rerun()
        else:
            st.error("Acesso negado.")
    st.stop()

# --- 3. INTERFACE PRINCIPAL ---
else:
    perfil = st.session_state.perfil
    st.sidebar.title(f"🚀 {'Professor' if perfil == 'admin' else 'Estudante'}")
    
    # Lista de Itens (Aluno + Professor)
    itens = ["Atividades (Drive)", "Expressões (PEMDAS)", "Equações (1º e 2º Grau)", "Cálculo de Funções", "Logaritmos", "Funções Aritméticas"]
    if perfil == "admin":
        itens = ["Gerador Automático", "Gerador de Atividades (Manual)"] + itens + ["Sistemas Lineares", "Matrizes", "Financeiro"]
        
    menu = st.sidebar.radio("Navegação:", itens)
    
    if st.sidebar.button("Sair"):
        st.session_state.perfil = None
        st.rerun()

    # --- NOVO MÓDULO: GERADOR AUTOMÁTICO (OPERAÇÕES BÁSICAS) ---
    if menu == "Gerador Automático":
        st.header("🔢 Gerador de Operações Básicas")
        tema = st.selectbox("Escolha o tema:", ["Adição", "Subtração", "Multiplicação", "Divisão", "Misto"])
        qtd = st.slider("Quantidade de questões:", 4, 20, 10)
        
        if st.button("Gerar PDF Automático"):
            pdf = FPDF()
            pdf.add_page()
            
            if os.path.exists("cabecalho.png"):
                pdf.image("cabecalho.png", x=12.5, y=8, w=185) 
                pdf.set_y(46)
            else: pdf.set_y(15)
            
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(0, 10, txt=f"Exercícios de {tema}", ln=True, align='C')
            pdf.ln(5)
            pdf.set_font("Arial", size=11)
            
            letras = "abcdefghijklmnopqrstuvwxyz"
            for i in range(qtd):
                # Lógica de sorteio
                op_atual = tema
                if tema == "Misto": op_atual = random.choice(["Adição", "Subtração", "Multiplicação", "Divisão"])
                
                n1, n2 = random.randint(10, 500), random.randint(10, 100)
                if op_atual == "Adição": txt = f"{n1} + {n2} ="
                elif op_atual == "Subtração": txt = f"{n1+n2} - {n1} ="
                elif op_atual == "Multiplicação": txt = f"{random.randint(2,20)} x {random.randint(2,12)} ="
                else: 
                    divisor = random.randint(2,12)
                    txt = f"{divisor * random.randint(2,20)} ÷ {divisor} ="
                
                pdf.cell(0, 10, txt=f"{letras[i%26]}) {txt}", ln=True)
            
            st.download_button("📥 Baixar PDF", pdf.output(dest='S').encode('latin-1', 'replace'), "atv_automatica.pdf")

    # --- MÓDULO: GERADOR MANUAL (PRESERVADO) ---
    elif menu == "Gerador de Atividades (Manual)":
        st.header("📄 Gerador de Atividades (Manual)")
        titulo_pdf = st.text_input("Título:", "Atividade de Matemática")
        conteudo = st.text_area("Conteúdo (Use . para colunas):", height=300)
        
        if st.button("Gerar PDF"):
            if conteudo:
                pdf = FPDF()
                pdf.add_page()
                if os.path.exists("cabecalho.png"):
                    pdf.image("cabecalho.png", x=12.5, y=8, w=185) 
                    pdf.set_y(46)
                else: pdf.set_y(15)
                
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(0, 10, txt=titulo_pdf, ln=True, align='C')
                pdf.ln(2)
                
                pdf.set_font("Arial", size=10)
                letras = "abcdefghijklmnopqrstuvwxyz"
                letra_idx = 0
                
                for linha in conteudo.split('\n'):
                    txt = linha.strip()
                    if not txt: continue
                    match = re.match(r'^(\.+)', txt)
                    num_pontos = len(match.group(1)) if match else 0
                    
                    if re.match(r'^\d+', txt): # Se começar com número
                        pdf.ln(4)
                        pdf.set_font("Arial", 'B', 11)
                        pdf.set_x(10)
                        pdf.multi_cell(0, 8, txt=txt)
                        pdf.set_font("Arial", size=10)
                        letra_idx = 0 
                    elif num_pontos > 0: # Lógica de colunas por pontos
                        item = txt[num_pontos:].strip()
                        prefixo = f"{letras[letra_idx % 26]}) "
                        if num_pontos > 1: pdf.set_y(pdf.get_y() - 8)
                        pdf.set_x(10 + (num_pontos - 1) * 32)
                        pdf.cell(32, 8, txt=f"{prefixo}{item}", ln=True)
                        letra_idx += 1
                    else:
                        pdf.set_x(10)
                        pdf.multi_cell(0, 8, txt=txt)
                
                st.download_button("📥 Baixar PDF Manual", pdf.output(dest='S').encode('latin-1', 'replace'), "atividade.pdf")

    # --- MANTIDOS OS DEMAIS MÓDULOS (DRIVE, EXPRESSÕES, EQUAÇÕES, ETC) ---
    elif menu == "Atividades (Drive)":
        st.header("📝 Pasta de Atividades")
        st.link_button("📂 Abrir Google Drive", "https://drive.google.com/drive/folders/1NkFeom_k3LUJYAFVBBDu4GD5aYVeNEZc")

    elif menu == "Expressões (PEMDAS)":
        st.header("🧮 Calculadora de Expressões")
        exp = st.text_input("Digite a expressão:")
        if st.button("Resolver"):
            try:
                res = eval(exp.replace('^', '**'), {"math": math})
                st.success(f"Resultado: {res}")
            except: st.error("Erro na expressão.")

    elif menu == "Equações (1º e 2º Grau)":
        st.header("📐 Resolução de Equações")
        grau = st.selectbox("Escolha o Grau:", ["1º Grau", "2º Grau"])
        if grau == "1º Grau":
            a1 = st.number_input("a:", value=1.0)
            b1 = st.number_input("b:", value=0.0)
            if st.button("Calcular"):
                st.success(f"x = {-b1/a1:.2f}")
        else:
            a2 = st.number_input("a:", value=1.0)
            b2 = st.number_input("b:", value=-5.0)
            c2 = st.number_input("c:", value=6.0)
            if st.button("Calcular"):
                delta = b2**2 - 4*a2*c2
                if delta >= 0:
                    x1 = (-b2 + math.sqrt(delta))/(2*a2)
                    x2 = (-b2 - math.sqrt(delta))/(2*a2)
                    st.success(f"x1 = {x1:.2f}, x2 = {x2:.2f}")
                else: st.error("Delta negativo.")

    elif menu == "Sistemas Lineares":
        st.header("⚖️ Sistema 2x2")
        a1, b1, c1 = st.number_input("a1"), st.number_input("b1"), st.number_input("c1")
        a2, b2, c2 = st.number_input("a2"), st.number_input("b2"), st.number_input("c2")
        if st.button("Calcular Sistema"):
            try:
                res = np.linalg.solve(np.array([[a1, b1], [a2, b2]]), np.array([c1, c2]))
                st.success(f"x = {res[0]:.2f}, y = {res[1]:.2f}")
            except: st.error("Erro no cálculo.")

    elif menu == "Financeiro":
        st.header("💰 Juros Compostos")
        c = st.number_input("Capital Inicial:", value=1000.0)
        i = st.number_input("Taxa mensal (%):", value=5.0) / 100
        t = st.number_input("Tempo (meses):", value=12.0)
        if st.button("Calcular Montante"):
            st.success(f"Montante Final: R$ {c * (1 + i)**t:.2f}")

    # (Cálculo de Funções, Logaritmos e Matrizes seguem a mesma lógica preservada)