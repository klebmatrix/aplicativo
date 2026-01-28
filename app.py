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
    # Tenta buscar dos Secrets (Render/Streamlit). Se falhar (local), usa padrões.
    try:
        senha_aluno = str(st.secrets.get("acesso_aluno", "123456")).strip()
        senha_professor = str(st.secrets.get("chave_mestra", "12345678")).strip()
    except:
        senha_aluno = "123456"
        senha_professor = "12345678"
        
    if pin_digitado == senha_aluno: return "aluno"
    elif pin_digitado == senha_professor: return "admin"
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
    
    # Itens preservados + Novos itens
    itens = ["Atividades (Drive)", "Expressões (PEMDAS)", "Equações (1º e 2º Grau)", "Cálculo de Funções", "Logaritmos", "Funções Aritméticas"]
    if perfil == "admin":
        # Inserindo os geradores no topo para o professor
        itens = ["GERADOR AUTO (Básico/Colegial)", "Gerador de Atividades (Manual)"] + itens + ["Sistemas Lineares", "Matrizes", "Financeiro"]
        
    menu = st.sidebar.radio("Navegação:", itens)
    
    if st.sidebar.button("Sair"):
        st.session_state.perfil = None
        st.rerun()

    # --- NOVO MÓDULO: GERADOR AUTOMÁTICO (OPERAÇÕES + COLEGIAL) ---
    if menu == "GERADOR AUTO (Básico/Colegial)":
        st.header("🖨️ Gerador Instantâneo de Exercícios")
        tema_auto = st.selectbox("Selecione o Conteúdo:", [
            "Operações Básicas (Soma, Sub, Mult, Div)",
            "Equações (1º e 2º Grau)",
            "Matrizes (Determinantes)",
            "Funções (f(x))",
            "Potenciação e Radiciação",
            "Razão e Proporção"
        ])
        
        if st.button("Gerar PDF Automático"):
            pdf = FPDF()
            pdf.add_page()
            if os.path.exists("cabecalho.png"):
                pdf.image("cabecalho.png", x=12.5, y=8, w=185) 
                pdf.set_y(46)
            else: pdf.set_y(15)
            
            pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, txt=f"Exercícios: {tema_auto}", ln=True, align='C'); pdf.ln(5)
            pdf.set_font("Arial", size=11); letras = "abcdefghijklmnopqrstuvwxyz"
            
            for i in range(12): # 12 questões automáticas
                if "Operações Básicas" in tema_auto:
                    op = random.choice(['+', '-', 'x', '÷'])
                    n1, n2 = random.randint(100, 999), random.randint(10, 99)
                    if op == '+': q = f"{n1} + {n2} ="
                    elif op == '-': q = f"{n1+n2} - {n1} ="
                    elif op == 'x': q = f"{random.randint(10,99)} x {random.randint(2,9)} ="
                    else: 
                        div = random.randint(2,12)
                        q = f"{div * random.randint(10,40)} ÷ {div} ="
                elif "Equações" in tema_auto:
                    q = f"{random.randint(2,9)}x + {random.randint(1,20)} = {random.randint(30,100)}"
                elif "Matrizes" in tema_auto:
                    q = f"Calcule o Determinante: [{random.randint(1,5)}, {random.randint(1,5)} | {random.randint(1,5)}, {random.randint(1,5)}]"
                elif "Potenciação" in tema_auto:
                    q = f"Calcule: {random.randint(2,10)}^{random.randint(2,3)} + √{random.choice([25,49,64,81,100,121,144])} ="
                elif "Razão" in tema_auto:
                    q = f"Determine x na proporção: {random.randint(1,5)}/{random.randint(6,10)} = x/{random.randint(20,50)}"
                else:
                    q = f"Calcule f({random.randint(1,10)}) para f(x) = {random.randint(2,5)}x + {random.randint(1,10)}"
                
                pdf.cell(0, 10, txt=f"{letras[i%26]}) {q}", ln=True)
            
            st.download_button("📥 Baixar PDF", pdf.output(dest='S').encode('latin-1', 'replace'), "atv_automatica.pdf")

    # --- MÓDULO: GERADOR MANUAL (PRESERVADO COM SUAS REGRAS) ---
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
                
                pdf.set_font("Arial", 'B', 12); pdf.cell(0, 10, txt=titulo_pdf, ln=True, align='C'); pdf.ln(2)
                pdf.set_font("Arial", size=10); letras = "abcdefghijklmnopqrstuvwxyz"; letra_idx = 0
                
                for linha in conteudo.split('\n'):
                    txt = linha.strip()
                    if not txt: continue
                    match = re.match(r'^(\.+)', txt)
                    num_pontos = len(match.group(1)) if match else 0
                    
                    if re.match(r'^\d+', txt): # Se começar com número, reseta letras
                        pdf.ln(4); pdf.set_font("Arial", 'B', 11)
                        pdf.set_x(10); pdf.multi_cell(0, 8, txt=txt)
                        pdf.set_font("Arial", size=10); letra_idx = 0 
                    elif num_pontos > 0: # Colunas
                        item = txt[num_pontos:].strip()
                        prefixo = f"{letras[letra_idx % 26]}) "
                        if num_pontos > 1: pdf.set_y(pdf.get_y() - 8)
                        pdf.set_x(10 + (num_pontos - 1) * 32)
                        pdf.cell(32, 8, txt=f"{prefixo}{item}", ln=True); letra_idx += 1
                    else:
                        pdf.set_x(10); pdf.multi_cell(0, 8, txt=txt)
                st.download_button("📥 Baixar PDF", pdf.output(dest='S').encode('latin-1', 'replace'), "atividade.pdf")

    # --- MANTIDOS E ATIVADOS: SISTEMAS, MATRIZES, LOGARITMOS E FINANCEIRO ---
    elif menu == "Sistemas Lineares":
        st.header("⚖️ Sistema 2x2")
        a1, b1, c1 = st.number_input("a1"), st.number_input("b1"), st.number_input("c1")
        a2, b2, c2 = st.number_input("a2"), st.number_input("b2"), st.number_input("c2")
        if st.button("Calcular"):
            try:
                res = np.linalg.solve(np.array([[a1, b1], [a2, b2]]), np.array([c1, c2]))
                st.success(f"Solução: x = {res[0]:.2f}, y = {res[1]:.2f}")
            except: st.error("Erro no sistema.")

    elif menu == "Matrizes":
        st.header("📊 Determinante 2x2")
        m11 = st.number_input("M11", value=1.0); m12 = st.number_input("M12", value=0.0)
        m21 = st.number_input("M21", value=0.0); m22 = st.number_input("M22", value=1.0)
        if st.button("Calcular"):
            st.metric("Det(M)", (m11*m22) - (m12*m21))

    elif menu == "Logaritmos":
        st.header("🔢 Logaritmo")
        num = st.number_input("Número:", value=100.0); bas = st.number_input("Base:", value=10.0)
        if st.button("Calcular"):
            st.success(f"Resultado: {math.log(num, bas):.4f}")

    elif menu == "Financeiro":
        st.header("💰 Juros Compostos")
        c, i, t = st.number_input("Capital"), st.number_input("Taxa (%)")/100, st.number_input("Meses")
        if st.button("Calcular"):
            st.success(f"Montante: R$ {c * (1+i)**t:.2f}")

    # (Módulos de Drive, Expressões, Equações, Funções e Funções Aritméticas seguem sua lógica original)
    elif menu == "Atividades (Drive)":
        st.header("📝 Pasta de Atividades")
        st.link_button("📂 Abrir Google Drive", "https://drive.google.com/drive/folders/1NkFeom_k3LUJYAFVBBDu4GD5aYVeNEZc")

    elif menu == "Expressões (PEMDAS)":
        st.header("🧮 PEMDAS")
        exp = st.text_input("Expressão:")
        if st.button("Resolver"):
            try: st.success(f"Resultado: {eval(exp.replace('^', '**'))}")
            except: st.error("Erro na expressão.")

    elif menu == "Equações (1º e 2º Grau)":
        st.header("📐 Equações")
        grau = st.selectbox("Grau:", ["1º Grau", "2º Grau"])
        if grau == "1º Grau":
            a, b = st.number_input("a:"), st.number_input("b:")
            if st.button("Calcular"): st.success(f"x = {-b/a:.2f}")
        else:
            a, b, c = st.number_input("a", value=1.0), st.number_input("b"), st.number_input("c")
            if st.button("Calcular"):
                delta = b**2 - 4*a*c
                if delta >= 0:
                    x1 = (-b + math.sqrt(delta))/(2*a)
                    x2 = (-b - math.sqrt(delta))/(2*a)
                    st.write(f"x1 = {x1:.2f}, x2 = {x2:.2f}")
                else: st.error("Delta negativo.")