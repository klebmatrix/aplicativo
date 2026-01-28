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
    
    # --- FUNÇÃO PARA CRIAR PDF ---
    def exportar_pdf(lista_questoes, titulo):
        pdf = FPDF()
        pdf.add_page()
        if os.path.exists("cabecalho.png"):
            pdf.image("cabecalho.png", x=12.5, y=8, w=185)
            pdf.set_y(46)
        else: pdf.set_y(15)
        pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, txt=titulo, ln=True, align='C'); pdf.ln(5)
        pdf.set_font("Arial", size=11)
        letras = "abcdefghijklmnopqrstuvwxyz"
        for i, q in enumerate(lista_questoes):
            pdf.cell(0, 10, txt=f"{letras[i%26]}) {q}", ln=True)
        return pdf.output(dest='S').encode('latin-1', 'replace')

    # --- 1. GERADOR OPERAÇÕES (COM PREVIEW) ---
    if menu == "GERADOR: Operações":
        st.header("🔢 Escolha as Operações")
        c1, c2, c3, c4 = st.columns(4)
        s = c1.checkbox("Soma (+)", value=True); sub = c2.checkbox("Subtração (-)", value=True)
        m = c3.checkbox("Multiplicação (x)"); d = c4.checkbox("Divisão (÷)")
        qtd = st.slider("Questões:", 4, 30, 12)
        
        ops = [o for o, v in zip(['+', '-', 'x', '÷'], [s, sub, m, d]) if v]
        
        if ops:
            questoes = []
            for i in range(qtd):
                op = random.choice(ops)
                n1, n2 = random.randint(100, 999), random.randint(10, 99)
                if op == '+': txt = f"{n1} + {n2} ="
                elif op == '-': txt = f"{n1+n2} - {n1} ="
                elif op == 'x': txt = f"{random.randint(10,99)} x {random.randint(2,9)} ="
                else: div_n = random.randint(2,12); txt = f"{div_n * random.randint(5,40)} ÷ {div_n} ="
                questoes.append(txt)
            
            st.subheader("👀 Visualização das Questões")
            for i, q in enumerate(questoes): st.write(f"{chr(97+i%26)}) {q}")
            
            pdf_data = exportar_pdf(questoes, "Atividade de Matemática")
            st.download_button("📥 Baixar este PDF", pdf_data, "operacoes.pdf")

    # --- 2. GERADOR COLEGIAL (COM PREVIEW) ---
    elif menu == "GERADOR: Colegial":
        st.header("📚 Escolha os Temas")
        c1, c2, c3 = st.columns(3)
        eq = c1.checkbox("Equações", value=True); fun = c2.checkbox("Funções"); pot = c3.checkbox("Potenciação")
        qtd = st.slider("Questões:", 4, 20, 8)
        
        temas = [t for t, v in zip(["E", "F", "P"], [eq, fun, pot]) if v]
        if temas:
            questoes = []
            for i in range(qtd):
                t = random.choice(temas)
                if t == "E": q = f"{random.randint(2,9)}x + {random.randint(1,20)} = {random.randint(21,80)}"
                elif t == "F": q = f"Se f(x) = {random.randint(2,5)}x + 10, calcule f({random.randint(1,5)})"
                else: q = f"Calcule {random.randint(2,10)}² ="
                questoes.append(q)
            
            for i, q in enumerate(questoes): st.write(f"{chr(97+i%26)}) {q}")
            pdf_data = exportar_pdf(questoes, "Atividade Colegial")
            st.download_button("📥 Baixar PDF", pdf_data, "colegial.pdf")

    # --- 4. GERADOR MANUAL (ERRO DE SINTAXE CORRIGIDO) ---
    elif menu == "GERADOR: Manual (Colunas)":
        st.header("📄 Gerador Manual")
        titulo = st.text_input("Título:", "Atividade")
        texto = st.text_area("Conteúdo (Use . para colunas):", height=300)
        
        if st.button("Gerar PDF Manual"):
            pdf = FPDF()
            pdf.add_page()
            if os.path.exists("cabecalho.png"):
                pdf.image("cabecalho.png", x=12.5, y=8, w=185)
                pdf.set_y(46)
            else: pdf.set_y(15)
            
            pdf.set_font("Arial", 'B', 12); pdf.cell(0, 10, titulo, ln=True, align='C'); pdf.ln(2)
            pdf.set_font("Arial", size=10); letras = "abcdefghijklmnopqrstuvwxyz"; letra_idx = 0
            
            for linha in texto.split('\n'):
                txt = linha.strip()
                if not txt: 
                    continue # CORREÇÃO: O if agora está em linha separada
                
                match = re.match(r'^(\.+)', txt)
                pts = len(match.group(1)) if match else 0
                
                if re.match(r'^\d+', txt):
                    pdf.ln(4); pdf.set_font("Arial", 'B', 11); pdf.multi_cell(0, 8, txt)
                    pdf.set_font("Arial", size=10); letra_idx = 0
                elif pts > 0:
                    it = txt[pts:].strip()
                    if pts > 1: pdf.set_y(pdf.get_y() - 8)
                    pdf.set_x(10 + (pts-1)*32)
                    pdf.cell(32, 8, f"{letras[letra_idx%26]}) {it}", ln=True)
                    letra_idx += 1
                else:
                    pdf.multi_cell(0, 8, txt)
            
            st.download_button("📥 Baixar PDF Manual", pdf.output(dest='S').encode('latin-1'), "manual.pdf")

    # --- MÓDULO DE CÁLCULO ---
    elif menu == "Cálculo de Funções":
        st.header("𝑓(x) Cálculo")
        f_exp = st.text_input("f(x):", "x**2 + 5")
        x_val = st.number_input("x:", value=3.0)
        if st.button("Calcular"):
            try:
                res = eval(f_exp.replace('x', f'({x_val})'))
                st.success(f"f({x_val}) = {res}")
            except: st.error("Erro na fórmula.")