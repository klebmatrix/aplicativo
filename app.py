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

# --- 3. MENU ---
else:
    perfil = st.session_state.perfil
    st.sidebar.title(f"🚀 {'Professor' if perfil == 'admin' else 'Estudante'}")
    
    itens = ["Atividades (Drive)", "Expressões (PEMDAS)", "Equações (1º e 2º Grau)", "Cálculo de Funções", "Logaritmos"]
    if perfil == "admin":
        geradores = ["GERADOR: Operações", "GERADOR: Colegial", "GERADOR: Álgebra Linear", "GERADOR: Manual (Colunas)"]
        itens = geradores + itens + ["Sistemas Lineares", "Matrizes", "Financeiro"]
        
    menu = st.sidebar.radio("Navegação:", itens)
    if st.sidebar.button("Sair"):
        st.session_state.perfil = None
        st.rerun()

    # --- FUNÇÃO BASE PDF ---
    def criar_pdf_base(titulo):
        pdf = FPDF()
        pdf.add_page()
        if os.path.exists("cabecalho.png"):
            pdf.image("cabecalho.png", x=12.5, y=8, w=185) 
            pdf.set_y(46)
        else: pdf.set_y(15)
        pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, txt=titulo, ln=True, align='C'); pdf.ln(5)
        return pdf

    # --- 4 GERADORES COM ESCOLHA ---

    if menu == "GERADOR: Operações":
        st.header("🔢 Escolha as Operações")
        c1, c2, c3, c4 = st.columns(4)
        s = c1.checkbox("Soma (+)", value=True); sub = c2.checkbox("Subtração (-)", value=True)
        m = c3.checkbox("Multiplicação (x)"); d = c4.checkbox("Divisão (÷)")
        qtd = st.slider("Questões:", 4, 30, 12)
        if st.button("Gerar PDF"):
            ops = [o for o, v in zip(['+', '-', 'x', '÷'], [s, sub, m, d]) if v]
            if ops:
                pdf = criar_pdf_base("Atividade de Matemática"); pdf.set_font("Arial", size=11)
                for i in range(qtd):
                    op = random.choice(ops)
                    n1, n2 = random.randint(100, 999), random.randint(10, 99)
                    if op == '+': txt = f"{n1} + {n2} ="
                    elif op == '-': txt = f"{n1+n2} - {n1} ="
                    elif op == 'x': txt = f"{random.randint(10,99)} x {random.randint(2,9)} ="
                    else: div_n = random.randint(2,12); txt = f"{div_n * random.randint(5,40)} ÷ {div_n} ="
                    pdf.cell(0, 10, txt=f"{chr(97+i%26)}) {txt}", ln=True)
                st.download_button("📥 Baixar PDF", pdf.output(dest='S').encode('latin-1'), "operacoes.pdf")

    elif menu == "GERADOR: Colegial":
        st.header("📚 Escolha os Temas Colegiais")
        c1, c2, c3 = st.columns(3)
        eq1 = c1.checkbox("Equações 1º Grau", value=True); pot = c2.checkbox("Potenciação", value=True); raz = c3.checkbox("Razão e Proporção")
        fun = c1.checkbox("Funções f(x)"); rad = c2.checkbox("Radiciação")
        qtd = st.slider("Questões:", 4, 20, 10)
        if st.button("Gerar PDF"):
            temas = [t for t, v in zip(["E", "P", "R", "F", "D"], [eq1, pot, raz, fun, rad]) if v]
            if temas:
                pdf = criar_pdf_base("Atividade Nível Colegial"); pdf.set_font("Arial", size=11)
                for i in range(qtd):
                    t = random.choice(temas)
                    if t == "E": q = f"{random.randint(2,9)}x + {random.randint(1,20)} = {random.randint(21,80)}"
                    elif t == "P": q = f"Calcule: {random.randint(2,10)}^{random.randint(2,3)} ="
                    elif t == "R": q = f"Determine x: {random.randint(1,5)}/8 = x/{random.randint(16,40)}"
                    elif t == "F": q = f"Se f(x) = {random.randint(2,5)}x - {random.randint(1,10)}, calcule f({random.randint(1,6)})"
                    else: q = f"Calcule: √{random.choice([16,25,36,49,64,81,100,121,144])} ="
                    pdf.cell(0, 10, txt=f"{chr(97+i%26)}) {q}", ln=True)
                st.download_button("📥 Baixar PDF", pdf.output(dest='S').encode('latin-1'), "colegial.pdf")

    elif menu == "GERADOR: Álgebra Linear":
        st.header("📊 Escolha Matrizes ou Sistemas")
        c1, c2 = st.columns(2)
        det = c1.checkbox("Determinantes 2x2", value=True); sis = c2.checkbox("Sistemas 2x2", value=True)
        if st.button("Gerar PDF"):
            pdf = criar_pdf_base("Álgebra: Matrizes e Sistemas"); pdf.set_font("Arial", size=11)
            for i in range(8):
                tipo = random.choice(["D", "S"]) if det and sis else ("D" if det else "S")
                if tipo == "D": q = f"Calcule o Det: [{random.randint(1,5)}, {random.randint(0,4)} | {random.randint(0,4)}, {random.randint(1,5)}]"
                else: q = f"Resolva o sistema: {random.randint(1,3)}x + y = {random.randint(5,15)} e x - y = {random.randint(1,5)}"
                pdf.cell(0, 10, txt=f"{chr(97+i%26)}) {q}", ln=True)
            st.download_button("📥 Baixar PDF", pdf.output(dest='S').encode('latin-1'), "algebra.pdf")

    elif menu == "GERADOR: Manual (Colunas)":
        st.header("📄 Gerador Manual (Lógica de Pontos)")
        titulo = st.text_input("Título:", "Atividade"); texto = st.text_area("Conteúdo:", height=300)
        if st.button("Gerar PDF Manual"):
            pdf = criar_pdf_base(titulo); pdf.set_font("Arial", size=10); letras = "abcdefghijklmnopqrstuvwxyz"; letra_idx = 0
            for linha in texto.split('\n'):
                txt = linha.strip(); if not txt: continue
                match = re.match(r'^(\.+)', txt); pts = len(match.group(1)) if match else 0
                if re.match(r'^\d+', txt):
                    pdf.ln(4); pdf.set_font("Arial", 'B', 11); pdf.multi_cell(0, 8, txt); pdf.set_font("Arial", size=10); letra_idx = 0
                elif pts > 0:
                    it = txt[pts:].strip(); if pts > 1: pdf.set_y(pdf.get_y() - 8)
                    pdf.set_x(10 + (pts-1)*32); pdf.cell(32, 8, f"{letras[letra_idx%26]}) {it}", ln=True); letra_idx += 1
                else: pdf.multi_cell(0, 8, txt)
            st.download_button("📥 Baixar PDF", pdf.output(dest='S').encode('latin-1'), "manual.pdf")

    # --- CÁLCULOS DIRETOS ---
    elif menu == "Cálculo de Funções":
        st.header("𝑓(x) Cálculo")
        f_exp = st.text_input("f(x):", "x**2 + 5"); x_val = st.number_input("x:", value=3.0)
        if st.button("Calcular"):
            try: st.metric("Resultado", eval(f_exp.replace('x', f'({x_val})')))
            except: st.error("Erro na fórmula.")