import streamlit as st
import math
import numpy as np
import os
import random
import re
from fpdf import FPDF

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

# --- 1. SEGURANÇA ---
def validar_acesso(pin_digitado):
    try:
        senha_aluno = str(st.secrets["acesso_aluno"]).strip()
        senha_professor = str(st.secrets["chave_mestra"]).strip()
        if pin_digitado == senha_aluno: return "aluno"
        elif pin_digitado == senha_professor: return "admin"
    except:
        # Fallback para desenvolvimento local
        if pin_digitado == "123456": return "aluno"
        elif pin_digitado == "12345678": return "admin"
    return "negado"

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

# --- 3. INTERFACE PRINCIPAL ---
else:
    perfil = st.session_state.perfil
    st.sidebar.title(f"🚀 {'Professor' if perfil == 'admin' else 'Estudante'}")
    
    # Definição dos Itens do Menu
    itens = ["Atividades (Drive)", "Expressões (PEMDAS)", "Equações (1º e 2º Grau)", "Cálculo de Funções", "Logaritmos", "Funções Aritméticas"]
    if perfil == "admin":
        # OS 4 GERADORES NO TOPO PARA O PROFESSOR
        geradores = ["GERADOR: Operações Básicas", "GERADOR: Nível Colegial", "GERADOR: Matrizes e Sistemas", "GERADOR: Manual (Colunas)"]
        itens = geradores + itens + ["Sistemas Lineares", "Matrizes", "Financeiro"]
        
    menu = st.sidebar.radio("Navegação:", itens)
    
    if st.sidebar.button("Sair"):
        st.session_state.perfil = None
        st.rerun()

    # --- FUNÇÃO AUXILIAR PARA PDF ---
    def gerar_pdf_base(titulo):
        pdf = FPDF()
        pdf.add_page()
        if os.path.exists("cabecalho.png"):
            pdf.image("cabecalho.png", x=12.5, y=8, w=185) 
            pdf.set_y(46)
        else: pdf.set_y(15)
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, txt=titulo, ln=True, align='C')
        pdf.ln(5)
        return pdf

    # --- MÓDULOS DOS GERADORES (ADMIN) ---
    
    if menu == "GERADOR: Operações Básicas":
        st.header("🔢 Gerador de Contas (Armar e Efetuar)")
        qtd = st.slider("Quantidade de questões:", 4, 20, 12)
        if st.button("Gerar PDF de Operações"):
            pdf = gerar_pdf_base("Atividade de Operações Fundamentais")
            pdf.set_font("Arial", size=11)
            letras = "abcdefghijklmnopqrstuvwxyz"
            for i in range(qtd):
                n1, n2 = random.randint(100, 999), random.randint(10, 99)
                op = random.choice(["+", "-", "x", "÷"])
                if op == "+": txt = f"{n1} + {n2} ="
                elif op == "-": txt = f"{n1+n2} - {n1} ="
                elif op == "x": txt = f"{random.randint(10,50)} x {random.randint(2,9)} ="
                else: 
                    d = random.randint(2,12)
                    txt = f"{d * random.randint(10,30)} ÷ {d} ="
                pdf.cell(0, 10, txt=f"{letras[i%26]}) {txt}", ln=True)
            st.download_button("📥 Baixar PDF", pdf.output(dest='S').encode('latin-1'), "operacoes.pdf")

    elif menu == "GERADOR: Nível Colegial":
        st.header("📚 Gerador: Funções, Potências e Razão")
        if st.button("Gerar PDF Colegial"):
            pdf = gerar_pdf_base("Lista de Exercícios: Nível Colegial")
            pdf.set_font("Arial", size=11)
            for i in range(10):
                tema = random.choice(["Função", "Potência", "Razão"])
                char = chr(97+i)
                if tema == "Função": q = f"Dada f(x) = {random.randint(2,5)}x + {random.randint(1,10)}, calcule f({random.randint(1,5)})"
                elif tema == "Potência": q = f"Calcule o valor de: {random.randint(2,9)}^2 + √{random.choice([16,25,36,64,100])}"
                else: q = f"Determine x na proporção: {random.randint(1,5)} / {random.randint(6,10)} = x / {random.randint(20,50)}"
                pdf.cell(0, 10, txt=f"{char}) {q}", ln=True)
            st.download_button("📥 Baixar PDF", pdf.output(dest='S').encode('latin-1'), "colegial.pdf")

    elif menu == "GERADOR: Matrizes e Sistemas":
        st.header("📊 Gerador: Álgebra Linear")
        if st.button("Gerar PDF de Álgebra"):
            pdf = gerar_pdf_base("Atividade: Matrizes e Sistemas")
            pdf.set_font("Arial", size=11)
            for i in range(8):
                char = chr(97+i)
                if i % 2 == 0: q = f"Calcule o determinante da matriz: [{random.randint(1,5)}, {random.randint(0,3)} | {random.randint(0,3)}, {random.randint(1,5)}]"
                else: q = f"Resolva o sistema: {random.randint(1,3)}x + y = {random.randint(5,10)} e x - y = {random.randint(1,4)}"
                pdf.cell(0, 10, txt=f"{char}) {q}", ln=True)
            st.download_button("📥 Baixar PDF", pdf.output(dest='S').encode('latin-1'), "algebra.pdf")

    elif menu == "GERADOR: Manual (Colunas)":
        st.header("📄 Gerador Manual (Lógica de Pontos)")
        titulo_pdf = st.text_input("Título:", "Atividade Personalizada")
        conteudo = st.text_area("Conteúdo (Use . para colunas):", height=300)
        if st.button("Gerar PDF Manual"):
            pdf = FPDF()
            pdf.add_page()
            if os.path.exists("cabecalho.png"):
                pdf.image("cabecalho.png", x=12.5, y=8, w=185) 
                pdf.set_y(46)
            else: pdf.set_y(15)
            pdf.set_font("Arial", 'B', 12); pdf.cell(0, 10, txt=titulo_pdf, ln=True, align='C'); pdf.ln(2)
            pdf.set_font("Arial", size=10); letras = "abcdefghijklmnopqrstuvwxyz"; letra_idx = 0
            for linha in conteudo.split('\n'):
                txt = linha.strip()
                if not txt: continue
                match = re.match(r'^(\.+)', txt)
                num_p = len(match.group(1)) if match else 0
                if re.match(r'^\d+', txt): # Questão numerada
                    pdf.ln(4); pdf.set_font("Arial", 'B', 11); pdf.set_x(10); pdf.multi_cell(0, 8, txt=txt); pdf.set_font("Arial", size=10); letra_idx = 0 
                elif num_p > 0: # Colunas
                    item = txt[num_p:].strip()
                    if num_p > 1: pdf.set_y(pdf.get_y() - 8)
                    pdf.set_x(10 + (num_p - 1) * 32); pdf.cell(32, 8, txt=f"{letras[letra_idx%26]}) {item}", ln=True); letra_idx += 1
                else: pdf.set_x(10); pdf.multi_cell(0, 8, txt=txt)
            st.download_button("📥 Baixar PDF", pdf.output(dest='S').encode('latin-1'), "manual.pdf")

    # --- MÓDULOS DE CÁLCULO (ATIVOS E FUNCIONAIS) ---

    elif menu == "Cálculo de Funções":
        st.header("𝑓(x) Cálculo de Valores")
        func_input = st.text_input("Função f(x):", value="x**2 - 4")
        val_x = st.number_input("Valor de x:", value=2.0)
        if st.button("Calcular"):
            try:
                res = eval(func_input.replace('x', f'({val_x})').replace('^', '**'))
                st.metric(f"f({val_x})", f"{res:.2f}")
            except: st.error("Erro na fórmula.")

    elif menu == "Matrizes":
        st.header("📊 Determinante 2x2")
        m11 = st.number_input("M11", value=1.0); m12 = st.number_input("M12", value=2.0)
        m21 = st.number_input("M21", value=3.0); m22 = st.number_input("M22", value=4.0)
        if st.button("Calcular Det"):
            st.success(f"Determinante: {(m11*m22) - (m12*m21)}")

    elif menu == "Sistemas Lineares":
        st.header("⚖️ Sistema 2x2")
        a1, b1, c1 = st.number_input("a1"), st.number_input("b1"), st.number_input("c1")
        a2, b2, c2 = st.number_input("a2"), st.number_input("b2"), st.number_input("c2")
        if st.button("Resolver"):
            try:
                res = np.linalg.solve(np.array([[a1, b1], [a2, b2]]), np.array([c1, c2]))
                st.success(f"x = {res[0]:.2f}, y = {res[1]:.2f}")
            except: st.error("Erro no cálculo.")

    elif menu == "Logaritmos":
        st.header("🔢 Logaritmo")
        n, b = st.number_input("Número", value=100.0), st.number_input("Base", value=10.0)
        if st.button("Calcular"): st.success(f"Resultado: {math.log(n, b):.4f}")

    elif menu == "Financeiro":
        st.header("💰 Juros Compostos")
        c, i, t = st.number_input("Capital"), st.number_input("Taxa (%)")/100, st.number_input("Tempo")
        if st.button("Calcular"): st.success(f"Montante: R$ {c * (1+i)**t:.2f}")
    
    # Adicione aqui os demais módulos (Expressões, Equações) seguindo o mesmo padrão.