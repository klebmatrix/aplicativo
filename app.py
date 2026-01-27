import streamlit as st
import math
import numpy as np
import os
import re
from fpdf import FPDF

# --- 1. SEGURANÇA ---
def validar_acesso(pin_digitado):
    try:
        senha_aluno = str(st.secrets["acesso_aluno"]).strip()
        senha_professor = str(st.secrets["chave_mestra"]).strip()
        if pin_digitado == senha_aluno: return "aluno"
        elif pin_digitado == senha_professor: return "admin"
    except: return "negado"
    return "negado"

st.set_page_config(page_title="Quantum Math Lab", layout="wide")
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

# --- 3. INTERFACE ---
else:
    perfil = st.session_state.perfil
    st.sidebar.title(f"🚀 {'Professor' if perfil == 'admin' else 'Estudante'}")
    
    itens = ["Atividades (Drive)", "Expressões (PEMDAS)", "Equações (1º e 2º Grau)", "Cálculo de Funções", "Logaritmos", "Funções Aritméticas"]
    if perfil == "admin":
        itens += ["Gerador de Atividades", "Sistemas Lineares", "Matrizes", "Financeiro"]
        
    menu = st.sidebar.radio("Navegação:", itens)
    
    if st.sidebar.button("Sair"):
        st.session_state.perfil = None
        st.rerun()

    # --- GERADOR DE ATIVIDADES ---
    if menu == "Gerador de Atividades":
        st.header("📄 Gerador de Atividades")
        titulo_pdf = st.text_input("Título da Atividade:", "Lista de Exercícios")
        conteudo = st.text_area("Digite o conteúdo (Linha com número inicia bloco, linhas seguintes ganham letras):", height=250)
        
        if st.button("Gerar PDF"):
            if conteudo:
                pdf = FPDF()
                pdf.add_page()
                
                # Inserção do Cabeçalho
                if os.path.exists("cabecalho.png"):
                    pdf.image("cabecalho.png", x=10, y=8, w=190)
                    pdf.ln(40) 
                else:
                    st.error("❌ Arquivo 'cabecalho.png' não encontrado no repositório.")

                pdf.set_font("Arial", 'B', 16)
                pdf.cell(200, 10, txt=titulo_pdf, ln=True, align='C')
                pdf.ln(10)
                
                pdf.set_font("Arial", size=12)
                letras = "abcdefghijklmnopqrstuvwxyz"
                letra_idx = 0
                
                for linha in conteudo.split('\n'):
                    txt = linha.strip()
                    if not txt: continue
                    
                    # Lógica: Se começa com número (ex: 1. ou 10)
                    if re.match(r'^\d+', txt):
                        pdf.ln(5)
                        pdf.set_font("Arial", 'B', 12)
                        pdf.multi_cell(0, 10, txt=txt)
                        pdf.set_font("Arial", size=12)
                        letra_idx = 0 
                    else:
                        # Se não tem número, vira a), b), c)...
                        prefixo = f"{letras[letra_idx % 26]}) "
                        pdf.multi_cell(0, 10, txt=f"    {prefixo}{txt}")
                        letra_idx += 1
                
                pdf_bytes = pdf.output(dest='S').encode('latin-1', 'replace')
                st.download_button("📥 Baixar PDF", data=pdf_bytes, file_name="atividade_quantum.pdf")
            else:
                st.warning("Adicione conteúdo para gerar.")

    # --- OUTROS MENUS (EQUAÇÕES, FINANCEIRO, ETC) ---
    elif menu == "Expressões (PEMDAS)":
        st.header("🧮 Expressões")
        exp = st.text_input("Expressão:")
        if st.button("Calcular"):
            try:
                res = eval(exp.replace('^', '**'), {"__builtins__": None}, {"math": math, "sqrt": math.sqrt})
                st.success(f"Resultado: {res}")
            except: st.error("Erro na expressão.")

    elif menu == "Financeiro":
        st.header("💰 Financeiro")
        c = st.number_input("Capital:", value=1000.0)
        i = st.number_input("Taxa (%):", value=5.0) / 100
        t = st.number_input("Tempo:", value=12.0)
        if st.button("Calcular"):
            st.success(f"Montante: R$ {c * (1 + i)**t:.2f}")

    # (Para os demais menus, basta seguir este padrão de indentação do elif)