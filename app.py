import streamlit as st
import math
import numpy as np
import os
import random
import re
from fpdf import FPDF

# --- CONFIGURAÇÃO ÚNICA DA PÁGINA ---
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
    
    # Itens do Menu (Garantindo que todos apareçam)
    itens = ["Atividades (Drive)", "Expressões (PEMDAS)", "Equações (1º e 2º Grau)", "Cálculo de Funções", "Logaritmos", "Funções Aritméticas"]
    if perfil == "admin":
        itens = ["GERADOR COLEGIAL (Auto)", "Gerador de Atividades (Manual)"] + itens + ["Sistemas Lineares", "Matrizes", "Financeiro"]
        
    menu = st.sidebar.radio("Navegação:", itens)
    if st.sidebar.button("Sair"):
        st.session_state.perfil = None
        st.rerun()

    # --- MÓDULO: GERADOR COLEGIAL (AUTO) ---
    if menu == "GERADOR COLEGIAL (Auto)":
        st.header("📚 Gerador de Exercícios Nível Colegial")
        tema = st.selectbox("Escolha o tema:", ["Equações", "Matrizes", "Funções", "Potenciação e Radiciação", "Razão e Proporção"])
        
        if st.button("Gerar PDF de Treino"):
            pdf = FPDF()
            pdf.add_page()
            if os.path.exists("cabecalho.png"):
                pdf.image("cabecalho.png", x=12.5, y=8, w=185) 
                pdf.set_y(46)
            else: pdf.set_y(15)
            
            pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, txt=f"Lista de Exercícios: {tema}", ln=True, align='C'); pdf.ln(5)
            pdf.set_font("Arial", size=11)
            
            letras = "abcdefghijklmnopqrstuvwxyz"
            for i in range(10):
                if tema == "Equações":
                    q = f"{random.randint(2,9)}x + {random.randint(1,20)} = {random.randint(30,100)}"
                elif tema == "Matrizes":
                    q = f"Calcule o determinante da matriz [{random.randint(1,5)}, {random.randint(1,5)} | {random.randint(1,5)}, {random.randint(1,5)}]"
                elif tema == "Funções":
                    q = f"Dada f(x) = {random.randint(2,5)}x + {random.randint(1,10)}, calcule f({random.randint(1,10)})"
                elif tema == "Potenciação e Radiciação":
                    q = f"Simplifique: {random.randint(2,5)}^{random.randint(2,4)} * √{random.choice([16, 25, 36, 49, 64, 81, 100])}"
                else: # Razão e Proporção
                    q = f"Encontre x: {random.randint(1,10)} / {random.randint(11,20)} = x / {random.randint(21,50)}"
                
                pdf.cell(0, 10, txt=f"{letras[i%26]}) {q}", ln=True)
            
            st.download_button("📥 Baixar PDF", pdf.output(dest='S').encode('latin-1', 'replace'), "exercicios.pdf")

    # --- MÓDULO: GERADOR MANUAL (REGRAS DE COLUNAS PRESERVADAS) ---
    elif menu == "Gerador de Atividades (Manual)":
        st.header("📄 Gerador Manual")
        titulo_pdf = st.text_input("Título:", "Atividade de Matemática")
        conteudo = st.text_area("Conteúdo:", height=300)
        if st.button("Gerar PDF Manual"):
            pdf = FPDF()
            pdf.add_page()
            if os.path.exists("cabecalho.png"): pdf.image("cabecalho.png", x=12.5, y=8, w=185); pdf.set_y(46)
            else: pdf.set_y(15)
            pdf.set_font("Arial", 'B', 12); pdf.cell(0, 10, txt=titulo_pdf, ln=True, align='C'); pdf.ln(2)
            pdf.set_font("Arial", size=10); letra_idx = 0
            for linha in conteudo.split('\n'):
                txt = linha.strip()
                if not txt: continue
                match = re.match(r'^(\.+)', txt)
                num_pontos = len(match.group(1)) if match else 0
                if re.match(r'^\d+', txt):
                    pdf.ln(4); pdf.set_font("Arial", 'B', 11); pdf.multi_cell(0, 8, txt=txt); pdf.set_font("Arial", size=10); letra_idx = 0 
                elif num_pontos > 0:
                    item = txt[num_pontos:].strip()
                    if num_pontos > 1: pdf.set_y(pdf.get_y() - 8)
                    pdf.set_x(10 + (num_pontos - 1) * 32); pdf.cell(32, 8, txt=f"{chr(97+letra_idx)}) {item}", ln=True); letra_idx += 1
                else: pdf.multi_cell(0, 8, txt=txt)
            st.download_button("📥 Baixar PDF", pdf.output(dest='S').encode('latin-1', 'replace'), "manual.pdf")

    # --- MÓDULOS DE CÁLCULO (ATIVADOS) ---
    elif menu == "Equações (1º e 2º Grau)":
        st.header("📐 Equações")
        tipo = st.radio("Grau:", ["1º Grau", "2º Grau"])
        if tipo == "1º Grau":
            a, b = st.number_input("a", value=1.0), st.number_input("b", value=0.0)
            if st.button("Resolver"): st.success(f"x = {-b/a:.2f}")
        else:
            a, b, c = st.number_input("a", value=1.0), st.number_input("b", value=-5.0), st.number_input("c", value=6.0)
            if st.button("Resolver"):
                delta = b**2 - 4*a*c
                if delta >= 0:
                    x1 = (-b + math.sqrt(delta))/(2*a)
                    x2 = (-b - math.sqrt(delta))/(2*a)
                    st.write(f"Delta: {delta} | x1 = {x1:.2f}, x2 = {x2:.2f}")
                else: st.error("Sem raízes reais.")

    elif menu == "Cálculo de Funções":
        st.header("𝑓(x) Funções")
        func = st.text_input("Função (ex: 2*x + 5):", "x**2 + 3")
        x_val = st.number_input("Valor de x:", value=2.0)
        if st.button("Calcular f(x)"):
            res = eval(func.replace('x', f'({x_val})'))
            st.metric("Resultado", res)

    elif menu == "Matrizes":
        st.header("📊 Determinante 2x2")
        col1, col2 = st.columns(2)
        m11 = col1.number_input("M11", value=1.0); m12 = col2.number_input("M12", value=0.0)
        m21 = col1.number_input("M21", value=0.0); m22 = col2.number_input("M22", value=1.0)
        if st.button("Calcular Det"):
            st.success(f"Determinante: {(m11*m22) - (m12*m21)}")

    elif menu == "Logaritmos":
        st.header("🔢 Logaritmos")
        log_n = st.number_input("Número:", value=100.0)
        log_b = st.number_input("Base:", value=10.0)
        if st.button("Calcular"): st.success(f"Resultado: {math.log(log_n, log_b):.4f}")

    elif menu == "Sistemas Lineares":
        st.header("⚖️ Sistema 2x2")
        a1, b1, c1 = st.number_input("a1"), st.number_input("b1"), st.number_input("c1")
        a2, b2, c2 = st.number_input("a2"), st.number_input("b2"), st.number_input("c2")
        if st.button("Resolver"):
            try:
                res = np.linalg.solve(np.array([[a1, b1], [a2, b2]]), np.array([c1, c2]))
                st.success(f"x = {res[0]:.2f}, y = {res[1]:.2f}")
            except: st.error("Sem solução única.")

    elif menu == "Atividades (Drive)":
        st.link_button("📂 Abrir Drive", "https://drive.google.com/drive/folders/1NkFeom_k3LUJYAFVBBDu4GD5aYVeNEZc")

    elif menu == "Financeiro":
        st.header("💰 Juros Compostos")
        c, i, t = st.number_input("Capital"), st.number_input("Taxa (%)")/100, st.number_input("Meses")
        if st.button("Calcular"): st.success(f"Montante: R$ {c * (1+i)**t:.2f}")