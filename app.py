import streamlit as st
import numpy as np
import random
import os
import re
from fpdf import FPDF

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide", page_icon="🚀")

def clean_txt(text):
    rep = {"√": "V", "²": "^2", "³": "^3", "÷": "/", "×": "x", "{": ""}
    for o, n in rep.items(): text = text.replace(o, n)
    return str(text).encode('latin-1', 'replace').decode('latin-1')

if 'perfil' not in st.session_state: st.session_state.perfil = None
if 'sub_menu' not in st.session_state: st.session_state.sub_menu = None
if 'lista_questoes' not in st.session_state: st.session_state.lista_questoes = []
if 'titulo_doc' not in st.session_state: st.session_state.titulo_doc = "ATIVIDADE"

# --- 2. MOTOR DE RENDERIZAÇÃO (O QUE VOCÊ QUERIA) ---
def renderizar_cards():
    if not st.session_state.lista_questoes:
        return

    st.divider()
    # 1. Imagem no Topo (Header)
    if os.path.exists("cabecalho.png"):
        st.image("cabecalho.png", use_container_width=True)
    
    # 2. Título
    st.markdown(f"<h1 style='text-align: center; color: #007bff;'>{st.session_state.titulo_doc}</h1>", unsafe_allow_html=True)
    
    letras = "abcdefghijklmnopqrstuvwxyz"
    l_idx = 0
    
    for linha in st.session_state.lista_questoes:
        t = str(linha).strip()
        if not t: continue
        
        # REGRA: Se começar com número, reseta letra e exibe destaque
        if re.match(r'^\d+', t):
            st.markdown(f"### {t}")
            l_idx = 0
        else:
            # CARD DE QUESTÃO
            with st.container(border=True):
                c1, c2 = st.columns([0.05, 0.95])
                with c1:
                    st.write(f"**{letras[l_idx%26]})**")
                with c2:
                    # Formatação Matemática simples (LaTeX)
                    clean_t = t.lstrip(',')
                    if any(m in clean_t for m in ["V", "^", "/", "|"]):
                        st.latex(clean_t.replace("V", "\\sqrt").replace("^", "^{") + "}" if "^" in clean_t else clean_t)
                    else:
                        st.write(clean_t)
                l_idx += 1

# --- 3. LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Login")
    pin = st.text_input("PIN:", type="password")
    if st.button("Entrar"):
        try: s_prof = str(st.secrets.get("chave_mestra", "chave_mestra")).strip().lower()
        except: s_prof = "chave_mestra"
        if pin == s_prof:
            st.session_state.perfil = "admin"
            st.rerun()
        else: st.error("PIN incorreto.")
    st.stop()

# --- 4. PAINEL PROFESSOR ---
with st.sidebar:
    st.header("🚀 Menu")
    if st.button("🔢 Operações"): st.session_state.sub_menu = "op"
    if st.button("📐 Equações"): st.session_state.sub_menu = "eq"
    if st.button("📚 Colegial"): st.session_state.sub_menu = "col"
    if st.button("📄 Manual"): st.session_state.sub_menu = "man"
    st.divider()
    if st.button("Logout"):
        st.session_state.perfil = None
        st.rerun()

# --- 5. LÓGICA DE GERAÇÃO POR MÓDULO ---
st.title(f"Módulo: {st.session_state.sub_menu or 'Início'}")

if st.session_state.sub_menu == "op":
    qtd = st.number_input("Qtd:", 5, 20, 10)
    if st.button("Gerar Operações"):
        st.session_state.titulo_doc = "OPERAÇÕES BÁSICAS"
        st.session_state.lista_questoes = ["1. Resolva os cálculos:"] + [f"{random.randint(10,99)} + {random.randint(10,99)} =" for _ in range(qtd)]

elif st.session_state.sub_menu == "eq":
    if st.button("Gerar Equações"):
        st.session_state.titulo_doc = "EQUAÇÕES DE 1º GRAU"
        st.session_state.lista_questoes = ["1. Determine o valor de x:"] + [f"{random.randint(2,9)}x + {random.randint(1,20)} = {random.randint(21,99)}" for _ in range(5)]

elif st.session_state.sub_menu == "man":
    st.session_state.titulo_doc = st.text_input("Título da Atividade:", "ATIVIDADE MANUAL")
    txt_man = st.text_area("Questões (Linha com número reseta as letras):", "1. Calcule:\n,V36\n,5^2\n2. Teoria:\nO que é Pi?")
    if st.button("Visualizar Cards"):
        st.session_state.lista_questoes = txt_man.split('\n')

# --- 6. EXIBIÇÃO E PDF ---
if st.session_state.lista_questoes:
    renderizar_cards()
    
    if st.button("📥 Gerar PDF"):
        pdf = FPDF(); pdf.add_page()
        if os.path.exists("cabecalho.png"):
            pdf.image("cabecalho.png", x=12, y=8, w=186)
            pdf.set_y(50)
        
        pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, clean_txt(st.session_state.titulo_doc), ln=True, align='C')
        pdf.set_font("Arial", size=11); l_idx = 0; letras = "abcdefghijklmnopqrstuvwxyz"
        
        for linha in st.session_state.lista_questoes:
            t = str(linha).strip()
            if not t: continue
            if re.match(r'^\d+', t):
                pdf.ln(5); pdf.set_font("Arial", 'B', 11); pdf.multi_cell(0, 8, clean_txt(t))
                pdf.set_font("Arial", size=11); l_idx = 0
            else:
                pdf.multi_cell(0, 8, f"{letras[l_idx%26]}) {clean_txt(t.lstrip(','))}")
                l_idx += 1
        st.download_button("✅ Baixar PDF", pdf.output(dest='S').encode('latin-1'), "atividade.pdf")