import streamlit as st
import math
import numpy as np
import os
import random
import re
from fpdf import FPDF

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

# --- 1. SEGURANÇA ---
def validar_acesso(pin_digitado):
    try:
        senha_aluno = str(st.secrets.get("acesso_aluno", "123456")).strip()
        senha_professor = str(st.secrets.get("chave_mestra", "12345678")).strip()
        if pin_digitado == senha_aluno: return "aluno"
        elif pin_digitado == senha_professor: return "admin"
    except:
        if pin_digitado == "123456": return "aluno"
        elif pin_digitado == "12345678": return "admin"
    return "negado"

if 'perfil' not in st.session_state: st.session_state.perfil = None

# --- 2. LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Quantum Math Lab")
    pin = st.text_input("PIN de Acesso:", type="password")
    if st.button("Entrar"):
        acesso = validar_acesso(pin)
        if acesso != "negado":
            st.session_state.perfil = acesso
            st.rerun()
        else: st.error("Acesso negado.")
    st.stop()

# --- 3. INTERFACE E MENU ---
else:
    perfil = st.session_state.perfil
    st.sidebar.title(f"🚀 {'Professor' if perfil == 'admin' else 'Estudante'}")
    
    # Itens principais
    itens = ["Atividades (Drive)", "Expressões (PEMDAS)", "Equações (1º e 2º Grau)", "Cálculo de Funções", "Logaritmos"]
    
    if perfil == "admin":
        # OS 4 GERADORES SOLICITADOS
        geradores = ["GERADOR: Operações Escolha", "GERADOR: Nível Colegial", "GERADOR: Matrizes e Sistemas", "GERADOR: Manual (Colunas)"]
        itens = geradores + itens + ["Sistemas Lineares", "Matrizes", "Financeiro"]
        
    menu = st.sidebar.radio("Navegação:", itens)
    if st.sidebar.button("Sair"):
        st.session_state.perfil = None
        st.rerun()

    # --- FUNÇÃO DE CABEÇALHO PADRÃO ---
    def criar_pdf_base(titulo):
        pdf = FPDF()
        pdf.add_page()
        if os.path.exists("cabecalho.png"):
            pdf.image("cabecalho.png", x=12.5, y=8, w=185) 
            pdf.set_y(46)
        else: pdf.set_y(15)
        pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, txt=titulo, ln=True, align='C'); pdf.ln(5)
        return pdf

    # --- 1. GERADOR OPERAÇÕES (POR ESCOLHA) ---
    if menu == "GERADOR: Operações Escolha":
        st.header("🔢 Gerador de Operações Básicas")
        col1, col2, col3, col4 = st.columns(4)
        soma = col1.checkbox("Soma (+)", value=True)
        sub = col2.checkbox("Subtração (-)", value=True)
        mult = col3.checkbox("Multiplicação (x)")
        div = col4.checkbox("Divisão (÷)")
        
        qtd = st.slider("Quantidade de questões:", 4, 30, 12)
        
        if st.button("Gerar PDF"):
            ops = []
            if soma: ops.append('+'); 
            if sub: ops.append('-'); 
            if mult: ops.append('x'); 
            if div: ops.append('÷')
            
            if not ops: st.error("Selecione uma operação.")
            else:
                pdf = criar_pdf_base("Atividade de Matemática")
                pdf.set_font("Arial", size=11); letras = "abcdefghijklmnopqrstuvwxyz"
                for i in range(qtd):
                    op = random.choice(ops)
                    n1, n2 = random.randint(100, 999), random.randint(10, 99)
                    if op == '+': txt = f"{n1} + {n2} ="
                    elif op == '-': txt = f"{n1+n2} - {n1} ="
                    elif op == 'x': txt = f"{random.randint(10,99)} x {random.randint(2,9)} ="
                    else: 
                        d = random.randint(2,12)
                        txt = f"{d * random.randint(5,40)} ÷ {d} ="
                    pdf.cell(0, 10, txt=f"{letras[i%26]}) {txt}", ln=True)
                st.download_button("Baixar PDF", pdf.output(dest='S').encode('latin-1'), "operacoes.pdf")

    # --- 2. GERADOR COLEGIAL ---
    elif menu == "GERADOR: Nível Colegial":
        st.header("📚 Gerador Colegial")
        if st.button("Gerar Lista"):
            pdf = criar_pdf_base("Exercícios Nível Colegial")
            pdf.set_font("Arial", size=11)
            for i in range(10):
                q = f"{random.randint(2,9)}x + {random.randint(1,20)} = {random.randint(21,80)}"
                pdf.cell(0, 10, txt=f"{chr(97+i)}) {q}", ln=True)
            st.download_button("Baixar PDF", pdf.output(dest='S').encode('latin-1'), "colegial.pdf")

    # --- 3. GERADOR MATRIZES/SISTEMAS ---
    elif menu == "GERADOR: Matrizes e Sistemas":
        st.header("📊 Gerador Álgebra")
        if st.button("Gerar PDF"):
            pdf = criar_pdf_base("Matrizes e Sistemas")
            pdf.set_font("Arial", size=11)
            for i in range(8):
                q = f"Calcule o Determinante: [{random.randint(1,5)}, {random.randint(0,4)} | {random.randint(0,4)}, {random.randint(1,5)}]"
                pdf.cell(0, 10, txt=f"{chr(97+i)}) {q}", ln=True)
            st.download_button("Baixar PDF", pdf.output(dest='S').encode('latin-1'), "algebra.pdf")

    # --- 4. GERADOR MANUAL (REGRAS PRESERVADAS) ---
    elif menu == "GERADOR: Manual (Colunas)":
        st.header("📄 Gerador Manual")
        titulo = st.text_input("Título:", "Atividade")
        texto = st.text_area("Conteúdo (Use . para colunas):", height=300)
        if st.button("Gerar PDF Manual"):
            pdf = criar_pdf_base(titulo)
            pdf.set_font("Arial", size=10); letras = "abcdefghijklmnopqrstuvwxyz"; letra_idx = 0
            for linha in texto.split('\n'):
                txt = linha.strip()
                if not txt: continue
                match = re.match(r'^(\.+)', txt)
                pts = len(match.group(1)) if match else 0
                if re.match(r'^\d+', txt): # Reinicia letras se for nova questão
                    pdf.ln(4); pdf.set_font("Arial", 'B', 11); pdf.multi_cell(0, 8, txt); pdf.set_font("Arial", size=10); letra_idx = 0
                elif pts > 0:
                    it = txt[pts:].strip()
                    if pts > 1: pdf.set_y(pdf.get_y() - 8)
                    pdf.set_x(10 + (pts-1)*32); pdf.cell(32, 8, f"{letras[letra_idx%26]}) {it}", ln=True); letra_idx += 1
                else: pdf.multi_cell(0, 8, txt)
            st.download_button("Baixar PDF", pdf.output(dest='S').encode('latin-1'), "manual.pdf")

    # --- CÁLCULOS DIRETOS ---
    elif menu == "Cálculo de Funções":
        st.header("𝑓(x) Cálculo")
        f_exp = st.text_input("f(x):", "x**2 + 5")
        x_val = st.number_input("x:", value=3.0)
        if st.button("Calcular"):
            try:
                res = eval(f_exp.replace('x', f'({x_val})'))
                st.metric("Resultado", f"{res:.2f}")
            except: st.error("Erro na fórmula.")

    elif menu == "Matrizes":
        st.header("📊 Determinante 2x2")
        m11 = st.number_input("a11", value=1.0); m12 = st.number_input("a12", value=0.0)
        m21 = st.number_input("a21", value=0.0); m22 = st.number_input("a22", value=1.0)
        if st.button("Calcular"):
            st.success(f"Determinante: {(m11*m22)-(m12*m21)}")