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
        geradores = [
            "GERADOR: Operações Básicas", 
            "GERADOR: Equações (1º/2º)", 
            "GERADOR: Colegial (Frações/Funções)", 
            "GERADOR: Álgebra Linear", 
            "GERADOR: Manual (Colunas)"
        ]
        itens = geradores + itens + ["Financeiro"]
        
    menu = st.sidebar.radio("Navegação:", itens)

    # --- FUNÇÃO EXPORTAR PDF ---
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

    # --- GERADOR 1: OPERAÇÕES BÁSICAS (ESCOLHA E PREVIEW) ---
    if menu == "GERADOR: Operações Básicas":
        st.header("🔢 Escolha as Operações para o PDF")
        
        c1, c2, c3, c4 = st.columns(4)
        soma = c1.checkbox("Soma (+)", value=True)
        sub = c2.checkbox("Subtração (-)", value=True)
        mult = c3.checkbox("Multiplicação (x)")
        div = c4.checkbox("Divisão (÷)")
        
        qtd = st.slider("Quantidade de questões:", 4, 30, 12)
        
        ops_selecionadas = []
        if soma: ops_selecionadas.append('+')
        if sub: ops_selecionadas.append('-')
        if mult: ops_selecionadas.append('x')
        if div: ops_selecionadas.append('÷')
        
        if not ops_selecionadas:
            st.warning("Por favor, selecione ao menos uma operação para visualizar as questões.")
        else:
            # Gerar lista para Preview
            random.seed(42) # Semente opcional para manter o preview estável até o download
            questoes = []
            for i in range(qtd):
                op = random.choice(ops_selecionadas)
                n1, n2 = random.randint(100, 999), random.randint(10, 99)
                if op == '+': 
                    txt = f"{n1} + {n2} ="
                elif op == '-': 
                    txt = f"{n1+n2} - {n1} ="
                elif op == 'x': 
                    txt = f"{random.randint(10,99)} x {random.randint(2,9)} ="
                else: 
                    d = random.randint(2,12)
                    txt = f"{d * random.randint(5,40)} ÷ {d} ="
                questoes.append(txt)
            
            st.subheader("👀 Preview das Questões")
            cols_preview = st.columns(2)
            for i, q in enumerate(questoes):
                cols_preview[i % 2].write(f"{chr(97+i%26)}) {q}")
            
            pdf_data = exportar_pdf(questoes, "Atividade de Matemática: Operações")
            st.download_button("📥 Baixar PDF das Operações", pdf_data, "operacoes.pdf")

    # --- GERADOR 2: EQUAÇÕES (1º E 2º GRAU) ---
    elif menu == "GERADOR: Equações (1º/2º)":
        st.header("📐 Gerador de Equações")
        grau = st.radio("Escolha o Grau:", ["Somente 1º Grau", "Somente 2º Grau", "Misto"])
        qtd = st.slider("Questões:", 4, 20, 10)
        
        qs = []
        for i in range(qtd):
            tipo = grau
            if grau == "Misto": tipo = random.choice(["Somente 1º Grau", "Somente 2º Grau"])
            if tipo == "Somente 1º Grau":
                qs.append(f"{random.randint(2,9)}x + {random.randint(1,20)} = {random.randint(21,90)}")
            else:
                qs.append(f"{random.randint(1,3)}x² + {random.randint(2,8)}x + {random.randint(1,5)} = 0")
        
        for i, q in enumerate(qs): st.write(f"{chr(97+i)}) {q}")
        st.download_button("📥 Baixar PDF", exportar_pdf(qs, "Atividade de Equações"), "equacoes.pdf")

    # --- GERADOR MANUAL (REGRAS DE COLUNAS) ---
    elif menu == "GERADOR: Manual (Colunas)":
        st.header("📄 Gerador Manual")
        titulo = st.text_input("Título:", "Atividade Personalizada")
        texto = st.text_area("Digite o conteúdo:", height=300)
        if st.button("Gerar PDF"):
            pdf = FPDF()
            pdf.add_page()
            if os.path.exists("cabecalho.png"):
                pdf.image("cabecalho.png", x=12.5, y=8, w=185)
                pdf.set_y(46)
            else:
                pdf.set_y(15)
            pdf.set_font("Arial", 'B', 12); pdf.cell(0, 10, titulo, ln=True, align='C'); pdf.ln(2)
            pdf.set_font("Arial", size=10); letras = "abcdefghijklmnopqrstuvwxyz"; letra_idx = 0
            for linha in texto.split('\n'):
                txt = linha.strip()
                if not txt: continue
                match = re.match(r'^(\.+)', txt)
                pts = len(match.group(1)) if match else 0
                if re.match(r'^\d+', txt): # Se começar com número, reseta letra para a)
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
        st.header("𝑓(x) Cálculo Direto")
        f_exp = st.text_input("f(x):", "x**2 + 5")
        x_val = st.number_input("x:", value=3.0)
        if st.button("Calcular"):
            try:
                # Substitui ^ por ** para o eval entender potência
                res = eval(f_exp.replace('x', f'({x_val})').replace('^', '**'))
                st.metric(f"f({x_val})", f"{res:.2f}")
            except: st.error("Erro na fórmula. Use 'x' e operadores como * e **.")