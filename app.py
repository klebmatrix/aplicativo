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
    
    itens = ["Atividades (Drive)", "Expressões (PEMDAS)", "Equações (1º e 2º Grau)", "Cálculo de Funções", "Logaritmos", "Funções Aritméticas"]
    if perfil == "admin":
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

    # --- 4 GERADORES ---

    if menu == "GERADOR: Operações Escolha":
        st.header("🔢 Gerador de Operações Básicas")
        st.write("Selecione as operações que deseja incluir na atividade:")
        c1, c2, c3, c4 = st.columns(4)
        soma = c1.checkbox("Soma (+)", value=True)
        sub = c2.checkbox("Subtração (-)", value=True)
        mult = c3.checkbox("Multiplicação (x)")
        div = c4.checkbox("Divisão (÷)")
        
        qtd = st.slider("Quantidade de questões:", 4, 30, 12)
        
        if st.button("Gerar PDF Escolhido"):
            ops_selecionadas = []
            if soma: ops_selecionadas.append('+')
            if sub: ops_selecionadas.append('-')
            if mult: ops_selecionadas.append('x')
            if div: ops_selecionadas.append('÷')
            
            if not ops_selecionadas:
                st.error("Selecione pelo menos uma operação!")
            else:
                pdf = criar_pdf_base("Atividade de Matemática: Operações")
                pdf.set_font("Arial", size=11); letras = "abcdefghijklmnopqrstuvwxyz"
                for i in range(qtd):
                    op = random.choice(ops_selecionadas)
                    n1, n2 = random.randint(100, 999), random.randint(10, 99)
                    if op == '+': txt = f"{n1} + {n2} ="
                    elif op == '-': txt = f"{n1+n2} - {n1} ="
                    elif op == 'x': txt = f"{random.randint(10,99)} x {random.randint(2,9)} ="
                    else: 
                        d = random.randint(2,12)
                        txt = f"{d * random.randint(5,40)} ÷ {d} ="
                    pdf.cell(0, 10, txt=f"{letras[i%26]}) {txt}", ln=True)
                st.download_button("📥 Baixar PDF", pdf.output(dest='S').encode('latin-1'), "operacoes.pdf")

    elif menu == "GERADOR: Manual (Colunas)":
        st.header("📄 Gerador Manual (Lógica de Pontos)")
        titulo = st.text_input("Título:", "Atividade")
        texto = st.text_area("Conteúdo:", height=300)
        if st.button("Gerar PDF"):
            pdf = FPDF()
            pdf.add_page()
            if os.path.exists("cabecalho.png"): pdf.image("cabecalho.png", x=12.5, y=8, w=185); pdf.set_y(46)
            pdf.set_font("Arial", 'B', 12); pdf.cell(0, 10, titulo, ln=True, align='C'); pdf.ln(2)
            pdf.set_font("Arial", size=10); letras = "abcdefghijklmnopqrstuvwxyz"; letra_idx = 0
            for linha in texto.split('\n'):
                txt = linha.strip()
                if not txt: continue
                match = re.match(r'^(\.+)', txt)
                pts = len(match.group(1)) if match else 0
                if re.match(r'^\d+', txt): # Se começa com número, reseta letra
                    pdf.ln(4); pdf.set_font("Arial", 'B', 11); pdf.multi_cell(0, 8, txt); pdf.set_font("Arial", size=10); letra_idx = 0
                elif pts > 0:
                    it = txt[pts:].strip()
                    if pts > 1: pdf.set_y(pdf.get_y() - 8)
                    pdf.set_x(10 + (pts-1)*32); pdf.cell(32, 8, f"{letras[letra_idx%26]}) {it}", ln=True); letra_idx += 1
                else: pdf.multi_cell(0, 8, txt)
            st.download_button("📥 Baixar PDF", pdf.output(dest='S').encode('latin-1'), "manual.pdf")

    # --- MÓDULOS DE CÁLCULO FUNCIONAIS ---

    elif menu == "Funções Aritméticas":
        st.header("🔍 Analisador de Números")
        n = st.number_input("Número:", min_value=1, value=24)
        if st.button("Analisar"):
            divs = [d for d in range(1, n + 1) if n % d == 0]
            st.write(f"Divisores: {divs}")
            st.write(f"Primo? {'Sim' if len(divs) == 2 else 'Não'}")

    elif menu == "Cálculo de Funções":
        st.header("𝑓(x) Cálculo")
        f_exp = st.text_input("f(x):", "x**2 + 5")
        x_val = st.number_input("x:", value=3.0)
        if st.button("Calcular"):
            try:
                res = eval(f_exp.replace('x', f'({x_val})'))
                st.metric("Resultado", res)
            except: st.error("Erro na fórmula.")

    # (Geradores Colegial e Matrizes seguem a mesma lógica de PDF automática)