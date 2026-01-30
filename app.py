import streamlit as st
import random
import re
import os
import math
from fpdf import FPDF

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

# Inicialização de estados para não perder dados no clique
for key in ['perfil', 'sub_menu', 'preview_questoes', 'res_calc']:
    if key not in st.session_state:
        st.session_state[key] = [] if key == 'preview_questoes' else None

# --- 2. LOGIN (Secrets Render) ---
def validar_acesso(pin):
    p_aluno = str(st.secrets.get("acesso_aluno", "123456")).strip()
    p_prof = str(st.secrets.get("chave_mestra", "chave_mestra")).strip().lower()
    return "admin" if pin == p_prof else "aluno" if pin == p_aluno else None

if st.session_state.perfil is None:
    st.title("🔐 Login")
    pin_input = st.text_input("PIN:", type="password")
    if st.button("Acessar"):
        res = validar_acesso(pin_input)
        if res: st.session_state.perfil = res; st.rerun()
        else: st.error("PIN Incorreto")
    st.stop()

# --- 3. SIDEBAR ---
st.sidebar.title(f"🚀 {st.session_state.perfil.upper()}")
usar_cabecalho = st.sidebar.checkbox("Usar cabecalho.png", value=True)
layout_cols = st.sidebar.selectbox("Colunas PDF:", [1, 2, 3], index=2)

if st.sidebar.button("🧹 Limpar Tudo", use_container_width=True):
    st.session_state.preview_questoes = []; st.session_state.sub_menu = None; st.session_state.res_calc = None; st.rerun()

if st.sidebar.button("🚪 Sair", use_container_width=True):
    st.session_state.clear(); st.rerun()

# --- 4. PAINEL DE COMANDO (8 BOTÕES) ---
st.title("🛠️ Centro de Comando")
g1, g2, g3, g4, g5 = st.columns(5)
if g1.button("🔢 Operações", use_container_width=True): st.session_state.sub_menu = "op"
if g2.button("📐 Equações", use_container_width=True): st.session_state.sub_menu = "eq"
if g3.button("⛓️ Sistemas", use_container_width=True): st.session_state.sub_menu = "sis"
if g4.button("⚖️ Álgebra", use_container_width=True): st.session_state.sub_menu = "alg"
if g5.button("📄 Manual", use_container_width=True): st.session_state.sub_menu = "man"

c1, c2, c3 = st.columns(3)
if c1.button("𝑓(x) Funções", use_container_width=True): st.session_state.sub_menu = "calc_f"
if c2.button("📊 PEMDAS", use_container_width=True): st.session_state.sub_menu = "pemdas"
if c3.button("💰 Financeira", use_container_width=True): st.session_state.sub_menu = "fin"

st.divider()
menu = st.session_state.sub_menu

# --- 5. LÓGICA DE GERAÇÃO (OPERÇÕES) ---
if menu == "op":
    st.subheader("🔢 Gerador de Operações")
    # ESCOLHA DA OPERAÇÃO
    tipo_op = st.radio("Escolha a Operação:", ["Soma", "Subtração", "Multiplicação", "Divisão"], horizontal=True)
    n_ini = st.number_input("Nº da Questão Inicial:", value=6)
    
    if st.button("✨ Gerar Questões"):
        simbolos = {"Soma": "+", "Subtração": "-", "Multiplicação": "x", "Divisão": "÷"}
        s = simbolos[tipo_op]
        
        # Gera 12 contas aleatórias
        contas = []
        for _ in range(12):
            a, b = random.randint(10, 999), random.randint(10, 500)
            if tipo_op == "Divisão": # Garante divisão exata para facilitar
                b = random.randint(2, 20)
                a = b * random.randint(5, 50)
            contas.append(f"{a} {s} {b} =")
            
        st.session_state.preview_questoes = [
            ".M1", 
            f"t. ATIVIDADE DE {tipo_op.upper()}", 
            f"{n_ini}. Resolva as operações abaixo:"
        ] + contas

# --- Lógica simplificada para os outros para o código não ficar gigante ---
elif menu == "eq":
    tipo_eq = st.radio("Grau:", ["1º Grau", "2º Grau"], horizontal=True)
    if st.button("Gerar"):
        st.session_state.preview_questoes = [".M1", f"t. EQUAÇÕES {tipo_eq}", "6. Resolva:"] + ["x + 2 = 10", "2x = 8"]

elif menu == "sis":
    if st.button("Gerar Sistema"):
        st.session_state.preview_questoes = [".M1", "t. SISTEMAS", "6. Resolva:"] + ["{ x+y=10 \n { x-y=2"]

elif menu == "man":
    txt = st.text_area("Texto Manual:")
    if st.button("Aplicar"): st.session_state.preview_questoes = txt.split("\n")

# --- 6. CÁLCULOS ---
elif menu == "calc_f":
    a = st.number_input("a", value=1.0)
    if st.button("Calcular"): st.session_state.res_calc = "Resultado da Função"

# (Financeira e PEMDAS seguem a mesma lógica de salvar no res_calc)

if st.session_state.res_calc:
    st.success(st.session_state.res_calc)

# --- 7. VISUALIZAÇÃO E MOTOR PDF (REGRAS DE IMAGEM E LETRAS) ---
if st.session_state.preview_questoes:
    st.subheader("👁️ Preview")
    with st.container(border=True):
        for line in st.session_state.preview_questoes: st.write(line)

    def export_pdf():
        pdf = FPDF()
        pdf.add_page()
        y_pos = 10
        
        # SOMENTE A IMAGEM CABECALHO.PNG
        if usar_cabecalho and os.path.exists("cabecalho.png"):
            pdf.image("cabecalho.png", 10, 10, 190)
            y_pos = 65 
        
        pdf.set_y(y_pos)
        letras, l_idx = "abcdefghijklmnopqrstuvwxyz", 0
        n_cols = int(layout_cols)
        larg_col = 190 / n_cols
        
        for line in st.session_state.preview_questoes:
            line = line.strip()
            if not line: continue
            
            if line.startswith(".M"):
                pdf.set_font("Helvetica", 'B', 12); pdf.cell(190, 10, line[1:], ln=True)
            elif line.lower().startswith("t."):
                pdf.set_font("Helvetica", 'B', 14); pdf.cell(190, 10, line[2:].strip().upper(), ln=True, align='C')
            elif re.match(r'^\d+\.', line): # SE FOR NÚMERO (Ex: 6.)
                pdf.set_font("Helvetica", 'B', 12); pdf.cell(190, 10, line, ln=True)
                l_idx = 0 # Reseta para começar no 'a)'
            else: # SE NÃO FOR NÚMERO, VIRA LETRA (a, b, c...)
                pdf.set_font("Helvetica", size=12)
                col = l_idx % n_cols
                pdf.cell(larg_col, 8, f"{letras[l_idx%26]}) {line.lstrip('. ')}", ln=(col == n_cols-1))
                l_idx += 1
                
        return pdf.output(dest='S').encode('latin-1')

    st.download_button("📥 Baixar PDF", data=export_pdf(), file_name="atividade.pdf")