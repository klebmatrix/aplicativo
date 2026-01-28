import streamlit as st
import math
import numpy as np
import os
import random
import re
from fpdf import FPDF

# --- 1. CONFIGURAÇÃO E ACESSO ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

def validar_acesso(pin_digitado):
    # Puxa das variáveis de ambiente do Render (st.secrets)
    senha_aluno = str(st.secrets.get("acesso_aluno", "123456")).strip()
    senha_prof = str(st.secrets.get("chave_mestra", "12345678")).strip()
    
    if pin_digitado == senha_aluno:
        return "aluno"
    elif pin_digitado == senha_prof:
        return "admin"
    return "negado"

if 'perfil' not in st.session_state:
    st.session_state.perfil = None

# TELA DE LOGIN
if st.session_state.perfil is None:
    st.title("🔐 Login do Sistema")
    pin = st.text_input("Digite seu PIN:", type="password")
    if st.button("Entrar"):
        acesso = validar_acesso(pin)
        if acesso != "negado":
            st.session_state.perfil = acesso
            st.rerun()
        else:
            st.error("PIN inválido!")
    st.stop()

# --- 2. MENU E NAVEGAÇÃO ---
perfil = st.session_state.perfil
st.sidebar.title(f"🚀 {'Professor' if perfil == 'admin' else 'Estudante'}")

if perfil == "admin":
    itens = [
        "GERADOR: Operações Básicas", 
        "GERADOR: Equações (1º/2º)", 
        "GERADOR: Colegial (Frações/Funções)", 
        "GERADOR: Álgebra Linear", 
        "GERADOR: Manual (Colunas)",
        "Cálculo de Funções",
        "Expressões (PEMDAS)",
        "Financeiro"
    ]
else:
    itens = ["Expressões (PEMDAS)", "Equações (1º e 2º Grau)", "Cálculo de Funções"]

menu = st.sidebar.radio("Navegação:", itens)

if st.sidebar.button("Sair"):
    st.session_state.perfil = None
    st.rerun()

# --- 3. FUNÇÃO PARA EXPORTAR PDF ---
def exportar_pdf(questoes, titulo):
    pdf = FPDF()
    pdf.add_page()
    if os.path.exists("cabecalho.png"):
        pdf.image("cabecalho.png", x=12.5, y=8, w=185)
        pdf.set_y(46)
    else:
        pdf.set_y(15)
    
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, txt=titulo, ln=True, align='C')
    pdf.ln(5)
    pdf.set_font("Arial", size=11)
    letras = "abcdefghijklmnopqrstuvwxyz"
    
    for i, q in enumerate(questoes):
        pdf.cell(0, 10, txt=f"{letras[i%26]}) {q}", ln=True)
    
    return pdf.output(dest='S').encode('latin-1', 'replace')

# --- 4. EXECUÇÃO DOS MÓDULOS ---

if menu == "GERADOR: Operações Básicas":
    st.header("🔢 Operações com Escolha")
    c1, c2, c3, c4 = st.columns(4)
    s = c1.checkbox("Soma (+)", value=True)
    su = c2.checkbox("Subtração (-)", value=True)
    m = c3.checkbox("Multiplicação (x)")
    d = c4.checkbox("Divisão (÷)")
    qtd = st.slider("Qtd:", 4, 30, 10)
    
    ops = [o for o, v in zip(['+', '-', 'x', '÷'], [s, su, m, d]) if v]
    if ops:
        qs = []
        for i in range(qtd):
            op = random.choice(ops)
            n1, n2 = random.randint(10, 500), random.randint(10, 99)
            if op == '+': qs.append(f"{n1} + {n2} =")
            elif op == '-': qs.append(f"{n1+n2} - {n1} =")
            elif op == 'x': qs.append(f"{random.randint(10,50)} x {random.randint(2,9)} =")
            else: 
                dv = random.randint(2,12)
                qs.append(f"{dv * random.randint(5,20)} ÷ {dv} =")
        
        st.subheader("👀 Preview das Questões")
        for i, q in enumerate(qs):
            st.write(f"**{chr(97+i%26)})** {q}")
        
        pdf_bytes = exportar_pdf(qs, "Operações Básicas")
        st.download_button("📥 Baixar PDF", pdf_bytes, "operacoes.pdf")

elif menu == "GERADOR: Equações (1º/2º)":
    st.header("📐 Equações")
    tipo = st.radio("Escolha o Grau:", ["1º Grau", "2º Grau", "Misto"])
    qtd_e = st.slider("Qtd:", 4, 20, 10)
    qs_e = []
    for i in range(qtd_e):
        esc = tipo
        if tipo == "Misto":
            esc = random.choice(["1º Grau", "2º Grau"])
        if esc == "1º Grau":
            qs_e.append(f"{random.randint(2,9)}x + {random.randint(1,20)} = {random.randint(21,90)}")
        else:
            qs_e.append(f"{random.randint(1,2)}x² + {random.randint(2,8)}x + {random.randint(1,6)} = 0")
    
    for i, q in enumerate(qs_e):
        st.write(f"**{chr(97+i)})** {q}")
    st.download_button("📥 Baixar PDF", exportar_pdf(qs_e, "Equações"), "equacoes.pdf")

elif menu == "GERADOR: Manual (Colunas)":
    st.header("📄 Criar Manualmente")
    titulo_m = st.text_input("Título:", "Atividade")
    texto_m = st.text_area("Digite o conteúdo (Use . para colunas)", height=250)
    if st.button("Gerar PDF"):
        pdf = FPDF()
        pdf.add_page()
        if os.path.exists("cabecalho.png"):
            pdf.image("cabecalho.png", x=12.5, y=8, w=185)
            pdf.set_y(46)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, titulo_m, ln=True, align='C')
        pdf.ln(2)
        pdf.set_font("Arial", size=10)
        letras = "abcdefghijklmnopqrstuvwxyz"
        l_idx = 0
        for linha in texto_m.split('\n'):
            t = linha.strip()
            if not t:
                continue
            m = re.match(r'^(\.+)', t)
            p = len(m.group(1)) if m else 0
            if re.match(r'^\d+', t): # Se começa com número (ex: 1.)
                pdf.ln(4)
                pdf.set_font("Arial", 'B', 11)
                pdf.multi_cell(0, 8, t)
                pdf.set_font("Arial", size=10)
                l_idx = 0 # Reinicia letras
            elif p > 0:
                if p > 1:
                    pdf.set_y(pdf.get_y() - 8)
                pdf.set_x(10 + (p-1)*32)
                pdf.cell(32, 8, f"{letras[l_idx%26]}) {t[p:].strip()}", ln=True)
                l_idx += 1
            else:
                pdf.multi_cell(0, 8, t)
        st.download_button("📥 Baixar Manual", pdf.output(dest='S').encode('latin-1'), "manual.pdf")

elif menu == "Cálculo de Funções":
    st.header("𝑓(x) Calculadora")
    f_e = st.text_input("Função f(x):", "x**2 + 5")
    val_x = st.number_input("Valor de x:", 2.0)
    if st.button("Calcular"):
        try:
            res = eval(f_e.replace('x', f'({val_x})').replace('^', '**'))
            st.metric("Resultado f(x)", res)
        except:
            st.error("Erro na fórmula!")

elif menu == "Financeiro":
    st.header("💰 Juros Compostos")
    cap = st.number_input("Capital (R$):", 1000.0)
    tax = st.number_input("Taxa (% a.m.):", 5.0) / 100
    mes = st.number_input("Tempo (meses):", 12)
    if st.button("Ver Resultado"):
        mont = cap * (1 + tax)**mes
        st.success(f"Montante Total: R$ {mont:.2f}")

# (Outros módulos seguem a mesma lógica de if/elif isolados)