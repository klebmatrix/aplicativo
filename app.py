import streamlit as st
import math
import numpy as np
import os
import random
import re
from fpdf import FPDF

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide", page_icon="🚀")

# Inicialização de estados
if 'perfil' not in st.session_state: st.session_state.perfil = None
if 'sub_menu' not in st.session_state: st.session_state.sub_menu = None
if 'preview_questoes' not in st.session_state: st.session_state.preview_questoes = []

def clean_txt(text):
    """Tradução para o PDF não bugar com símbolos"""
    if not text: return ""
    text = str(text).replace("√", "V").replace("²", "^2").replace("³", "^3")
    return text.encode('latin-1', 'replace').decode('latin-1')

def tratar_math(texto):
    """Trata potências e raízes para exibição no LaTeX do Streamlit"""
    t = texto.strip()
    t = t.replace("²", "^{2}").replace("³", "^{3}")
    return t

def validar_acesso(pin_digitado):
    try:
        senha_aluno = str(st.secrets.get("acesso_aluno", "123456")).strip()
        senha_prof = str(st.secrets.get("chave_mestra", "chave_mestra")).strip().lower()
    except:
        senha_aluno, senha_prof = "123456", "chave_mestra"
    if pin_digitado == senha_aluno: return "aluno"
    elif pin_digitado == senha_prof: return "admin"
    return "negado"

# --- LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Login")
    pin = st.text_input("PIN:", type="password")
    if st.button("Entrar"):
        acesso = validar_acesso(pin)
        if acesso != "negado":
            st.session_state.perfil = acesso
            st.rerun()
        else: st.error("PIN incorreto.")
    st.stop()

# --- 2. MENU E LOGOUT ---
perfil = st.session_state.perfil
st.sidebar.title(f"🚀 {'Professor' if perfil == 'admin' else 'Estudante'}")
if st.sidebar.button("Sair/Logout"):
    st.session_state.perfil = None
    st.session_state.sub_menu = None
    st.session_state.preview_questoes = []
    st.rerun()

# --- 4. PAINEL PRINCIPAL (ADMIN) ---
if perfil == "admin":
    st.title("🛠️ Painel de Controle do Professor")
    
    st.subheader("📝 Geradores de Atividades (PDF)")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: 
        if st.button("🔢 Operações\nBásicas", use_container_width=True): st.session_state.sub_menu = "op"
    with c2: 
        if st.button("📐 Equações\n1º e 2º Grau", use_container_width=True): st.session_state.sub_menu = "eq"
    with c3: 
        if st.button("📚 Colegial\nFrações/Funções", use_container_width=True): st.session_state.sub_menu = "col"
    with c4: 
        if st.button("⚖️ Álgebra\nLinear", use_container_width=True): st.session_state.sub_menu = "alg"
    with c5: 
        if st.button("📄 Gerador\nManual", use_container_width=True): st.session_state.sub_menu = "man"

    st.markdown("---")
    st.subheader("🧮 Ferramentas de Cálculo Online")
    d1, d2, d3 = st.columns(3)
    with d1: 
        if st.button("𝑓(x) Cálculo\nde Funções", use_container_width=True): st.session_state.sub_menu = "calc_f"
    with d2: 
        if st.button("📊 Expressões\n(PEMDAS)", use_container_width=True): st.session_state.sub_menu = "pemdas"
    with d3: 
        if st.button("💰 Calculadora\nFinanceira", use_container_width=True): st.session_state.sub_menu = "fin"

    op_atual = st.session_state.sub_menu
    st.divider()

    if op_atual == "op":
        st.header("🔢 Operações")
        escolhas = st.multiselect("Sinais:", ["+", "-", "x", "÷"], ["+", "-"])
        qtd = st.number_input("Qtd:", 4, 30, 10)
        if st.button("Gerar Preview"):
            st.session_state.preview_questoes = ["t. Atividade de Operações"] + [
                f"{random.randint(10,500)} {random.choice(escolhas)} {random.randint(2,50)} =" 
                for _ in range(qtd)
            ]

    elif op_atual == "eq":
        st.header("📐 Equações")
        grau = st.radio("Grau:", ["1º Grau", "2º Grau"], horizontal=True)
        if st.button("Gerar Preview"):
            if grau == "1º Grau":
                qs = [f"{random.randint(2,9)}x + {random.randint(1,20)} = {random.randint(21,99)}" for _ in range(8)]
            else:
                qs = [f"x² + {random.randint(2,8)}x + {random.randint(1,12)} = 0" for _ in range(8)]
            st.session_state.preview_questoes = [f"t. Equações de {grau}"] + qs

    elif op_atual == "man":
        st.header("📄 Manual")
        txt_m = st.text_area("Texto (Use 't.' para título e números para seções):", height=200)
        if st.button("Gerar Preview"):
            st.session_state.preview_questoes = txt_m.split('\n')

    elif op_atual == "calc_f":
        st.header("𝑓(x) Cálculo de Funções")
        f_input = st.text_input("Defina f(x):", "x**2 + 5*x + 6")
        x_val = st.number_input("Valor de x:", value=1.0)
        if st.button("Calcular Resultado"):
            try:
                resultado = eval(f_input.replace('x', f'({x_val})'))
                st.metric(label=f"f({x_val})", value=f"{resultado:.4f}")
                st.latex(f"f({x_val}) = {resultado}")
            except Exception as e: st.error(f"Erro: {e}")

# --- 6. VISUALIZAÇÃO EM CARDS (DUAS COLUNAS NO STREAMLIT) ---
if st.session_state.preview_questoes:
    st.divider()
    if os.path.exists("cabecalho.png"):
        st.image("cabecalho.png", use_container_width=True)
    
    letras = "abcdefghijklmnopqrstuvwxyz"
    l_idx = 0

    # Filtramos apenas as questões que serão exibidas em colunas (excluindo títulos e números)
    items_to_show = []
    
    for q in st.session_state.preview_questoes:
        line = q.strip()
        if not line: continue
        
        # Se for título ou número, interrompe o fluxo de colunas e exibe largura total
        if line.lower().startswith(("t.", "titulo:", "título:")) or re.match(r'^\d+', line):
            # Se havia itens pendentes para mostrar em colunas, processamos eles agora
            if items_to_show:
                cols = st.columns(2)
                for i, item in enumerate(items_to_show):
                    with cols[i % 2]:
                        with st.container(border=True):
                            f = tratar_math(item['text'])
                            st.write(f"**{item['letra']})**")
                            if "x²" in item['text'] or "^" in item['text']: st.latex(f)
                            else: st.write(item['text'])
                items_to_show = [] # Limpa a lista

            if line.lower().startswith(("t.", "titulo:", "título:")):
                t_clean = re.sub(r'^(t\.|titulo:|título:)\s*', '', line, flags=re.IGNORECASE)
                st.markdown(f"<h1 style='text-align: center; color: #007bff; border-bottom: 2px solid #007bff;'>{t_clean}</h1>", unsafe_allow_html=True)
            else:
                st.markdown(f"### {line}")
                l_idx = 0 
        else:
            # Adiciona item na fila para exibição em 2 colunas
            items_to_show.append({'letra': letras[l_idx % 26], 'text': line})
            l_idx += 1

    # Processa os últimos itens se sobraram
    if items_to_show:
        cols = st.columns(2)
        for i, item in enumerate(items_to_show):
            with cols[i % 2]:
                with st.container(border=True):
                    f = tratar_math(item['text'])
                    st.write(f"**{item['letra']})**")
                    if "x²" in item['text'] or "^" in item['text']: st.latex(f)
                    else: st.write(item['text'])

# --- 7. EXPORTAÇÃO PDF (FOLHA A4 - COLUNAS ALINHADAS) ---
    if st.button("📥 Baixar Atividade Finalizada (PDF)"):
        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.add_page()
        pdf.set_margins(15, 15, 15)
        
        if os.path.exists("cabecalho.png"):
            pdf.image("cabecalho.png", x=12.5, y=10, w=185)
            y_atual = 55
        else:
            y_atual = 20

        letras = "abcdefghijklmnopqrstuvwxyz"
        l_idx_pdf = 0
        
        for q in st.session_state.preview_questoes:
            line = q.strip()
            if not line: continue
            
            if line.lower().startswith(("t.", "titulo:", "título:")):
                t_clean = re.sub(r'^(t\.|titulo:|título:)\s*', '', line, flags=re.IGNORECASE)
                pdf.set_y(y_atual + 5)
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(0, 12, clean_txt(t_clean), ln=True, align='C')
                y_atual = pdf.get_y() + 5
            elif re.match(r'^\d+', line):
                pdf.set_y(y_atual + 5)
                pdf.set_font("Arial", 'B', 12)
                pdf.multi_cell(0, 8, clean_txt(line))
                y_atual = pdf.get_y()
                l_idx_pdf = 0
            else:
                pdf.set_font("Arial", size=11)
                texto_item = f"{letras[l_idx_pdf % 26]}) {line}"
                if l_idx_pdf % 2 == 0:
                    y_base_coluna = y_atual 
                    pdf.set_xy(15, y_base_coluna)
                    pdf.multi_cell(90, 8, clean_txt(texto_item))
                    y_proxima_linha = pdf.get_y() 
                else:
                    pdf.set_xy(110, y_base_coluna)
                    pdf.multi_cell(85, 8, clean_txt(texto_item))
                    y_atual = max(y_proxima_linha, pdf.get_y())
                l_idx_pdf += 1

        st.download_button(
            label="✅ Baixar Atividade A4 Corrigida",
            data=bytes(pdf.output()),
            file_name="atividade_perfeita.pdf",
            mime="application/pdf"
        )