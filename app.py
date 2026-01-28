import streamlit as st
import numpy as np
import random
import os
import re
from fpdf import FPDF

# --- 1. CONFIGURAÇÕES ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide", page_icon="🚀")

def clean_txt(text):
    rep = {"√": "V", "²": "^2", "³": "^3", "÷": "/", "×": "x", "{": ""}
    for o, n in rep.items(): text = text.replace(o, n)
    return str(text).encode('latin-1', 'replace').decode('latin-1')

if 'perfil' not in st.session_state: st.session_state.perfil = None
if 'sub_menu' not in st.session_state: st.session_state.sub_menu = None
if 'questoes_para_exibir' not in st.session_state: st.session_state.questoes_para_exibir = []
if 'titulo_da_vez' not in st.session_state: st.session_state.titulo_da_vez = ""

# --- 2. FUNÇÃO MESTRE DE RENDERIZAÇÃO (CARDS) ---
def renderizar_atividade_na_tela(questoes, titulo):
    if not questoes: return
    
    st.divider()
    # 1. Imagem no Topo
    if os.path.exists("cabecalho.png"):
        st.image("cabecalho.png", use_container_width=True)
    
    # 2. Título Centralizado
    st.markdown(f"<h1 style='text-align: center;'>{titulo}</h1>", unsafe_allow_html=True)
    
    letras = "abcdefghijklmnopqrstuvwxyz"
    l_idx = 0
    
    for q in questoes:
        linha = str(q).strip()
        if not linha: continue
        
        # Regra: Se começa com número, é título e reseta as letras
        if re.match(r'^\d+', linha):
            st.markdown(f"### {linha}")
            l_idx = 0
        else:
            # Layout de Card com Borda
            with st.container(border=True):
                c1, c2 = st.columns([0.05, 0.95])
                with c1: st.write(f"**{letras[l_idx%26]})**")
                with c2:
                    # Suporte para Raiz (V) e Potência (^) no LaTeX
                    if any(x in linha for x in ["V", "^", "/", "{", "|"]):
                        txt = linha.replace("V", "\\sqrt{").replace("^", "^{")
                        # Se tiver fechamento simples necessário para V e ^
                        if "\\sqrt{" in txt: txt += "}"
                        if "^{" in txt: txt += "}"
                        st.latex(txt.lstrip(','))
                    else:
                        st.write(linha.lstrip(','))
                l_idx += 1

# --- 3. LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Login")
    pin = st.text_input("PIN:", type="password")
    if st.button("Entrar"):
        try:
            # Pega do Render ou usa padrão
            s_prof = str(st.secrets.get("chave_mestra", "12345678")).strip().lower()
        except: s_prof = "12345678"
        
        if pin == s_prof: 
            st.session_state.perfil = "admin"
            st.rerun()
        else: st.error("Acesso Negado.")
    st.stop()

# --- 4. PAINEL PROFESSOR ---
st.sidebar.title("🚀 Quantum Prof")
if st.sidebar.button("Sair"):
    st.session_state.perfil = None
    st.rerun()

st.title("🛠️ Gerador de Atividades")
c1, c2, c3, c4 = st.columns(4)

with c1:
    if st.button("🔢 Operações", use_container_width=True): 
        st.session_state.sub_menu = "op"
with c2:
    if st.button("📐 Equações", use_container_width=True): 
        st.session_state.sub_menu = "eq"
with c3:
    if st.button("📚 Colegial", use_container_width=True): 
        st.session_state.sub_menu = "col"
with c4:
    if st.button("📄 Manual", use_container_width=True): 
        st.session_state.sub_menu = "man"

st.divider()

# --- LÓGICA DE GERAÇÃO ---
menu = st.session_state.sub_menu

if menu == "op":
    qtd = st.number_input("Qtd de questões:", 1, 20, 10)
    if st.button("Gerar Agora"):
        st.session_state.titulo_da_vez = "ATIVIDADE DE OPERAÇÕES"
        st.session_state.questoes_para_exibir = ["1. Efetue os cálculos:"] + [f"{random.randint(10,500)} + {random.randint(10,500)} =" for _ in range(qtd)]

elif menu == "eq":
    if st.button("Gerar Equações"):
        st.session_state.titulo_da_vez = "ESTUDO DE EQUAÇÕES"
        st.session_state.questoes_para_exibir = ["1. Resolva as sentenças:"] + [f"{random.randint(2,9)}x + {random.randint(1,20)} = {random.randint(21,99)}" for _ in range(5)]

elif menu == "man":
    st.session_state.titulo_da_vez = st.text_input("Título:", "ATIVIDADE MANUAL")
    txt = st.text_area("Questões (Use número para nova seção):", "1. Matemática:\n,V36\n,5^2\n2. Outros:\nQuestão Teste")
    if st.button("Visualizar Manual"):
        st.session_state.questoes_para_exibir = txt.split('\n')

# --- 5. EXIBIÇÃO UNIFICADA (CARDS) ---
if st.session_state.questoes_para_exibir:
    renderizar_atividade_na_tela(st.session_state.questoes_para_exibir, st.session_state.titulo_da_vez)
    
    # Botão de PDF
    if st.button("📥 Baixar em PDF"):
        pdf = FPDF(); pdf.add_page()
        if os.path.exists("cabecalho.png"): pdf.image("cabecalho.png", x=10, y=8, w=190); pdf.set_y(50)
        pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, clean_txt(st.session_state.titulo_da_vez), ln=True, align='C')
        pdf.set_font("Arial", size=11); l_idx = 0; letras = "abcdefghijklmnopqrstuvwxyz"
        
        for q in st.session_state.questoes_para_exibir:
            line = str(q).strip()
            if not line: continue
            if re.match(r'^\d+', line):
                pdf.ln(5); pdf.set_font("Arial", 'B', 12); pdf.multi_cell(0, 8, clean_txt(line))
                pdf.set_font("Arial", size=11); l_idx = 0
            else:
                pdf.multi_cell(0, 8, f"{letras[l_idx%26]}) {clean_txt(line.lstrip(','))}")
                l_idx += 1
        st.download_button("✅ Salvar PDF", pdf.output(dest='S').encode('latin-1'), "atividade.pdf")