import streamlit as st
import math
import numpy as np
import os
import random
import re
from fpdf import FPDF

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide", page_icon="🚀")

if 'perfil' not in st.session_state: st.session_state.perfil = None
if 'sub_menu' not in st.session_state: st.session_state.sub_menu = None
if 'preview_questoes' not in st.session_state: st.session_state.preview_questoes = []

def clean_txt(text):
    if not text: return ""
    text = str(text).replace("√", "V").replace("²", "^2").replace("³", "^3")
    return text.encode('latin-1', 'replace').decode('latin-1')

def tratar_math(texto):
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

# --- MENU LATERAL ---
perfil = st.session_state.perfil
st.sidebar.title(f"🚀 {'Professor' if perfil == 'admin' else 'Estudante'}")
if st.sidebar.button("Sair/Logout"):
    for key in list(st.session_state.keys()): del st.session_state[key]
    st.rerun()

# --- PAINEL ADMIN ---
if perfil == "admin":
    st.title("🛠️ Painel de Controle")
    
    st.subheader("📝 Geradores de Atividades (PDF)")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: 
        if st.button("🔢 Operações", use_container_width=True): 
            st.session_state.sub_menu = "op"; st.session_state.preview_questoes = []
    with c2: 
        if st.button("📐 Equações", use_container_width=True): 
            st.session_state.sub_menu = "eq"; st.session_state.preview_questoes = []
    with c3: 
        if st.button("📚 Colegial", use_container_width=True): 
            st.session_state.sub_menu = "col"; st.session_state.preview_questoes = []
    with c4: 
        if st.button("⚖️ Álgebra", use_container_width=True): 
            st.session_state.sub_menu = "alg"; st.session_state.preview_questoes = []
    with c5: 
        if st.button("📄 Manual", use_container_width=True): 
            st.session_state.sub_menu = "man"; st.session_state.preview_questoes = []

    st.markdown("---")
    st.subheader("🧮 Ferramentas de Cálculo Online")
    d1, d2, d3 = st.columns(3)
    with d1: 
        if st.button("𝑓(x) Funções", use_container_width=True): st.session_state.sub_menu = "calc_f"
    with d2: 
        if st.button("📊 PEMDAS", use_container_width=True): st.session_state.sub_menu = "pemdas"
    with d3: 
        if st.button("💰 Financeira", use_container_width=True): st.session_state.sub_menu = "fin"

    op_atual = st.session_state.sub_menu
    st.divider()

    # --- LÓGICA DOS 5 GERADORES ---
    if op_atual == "op":
        st.header("🔢 Gerador de Operações")
        escolhas = st.multiselect("Sinais:", ["+", "-", "x", "÷"], ["+", "-"])
        qtd = st.number_input("Quantidade:", 4, 30, 10)
        if st.button("Gerar Preview"):
            st.session_state.preview_questoes = ["t. Atividade de Operações"] + [f"{random.randint(10,500)} {random.choice(escolhas)} {random.randint(2,50)} =" for _ in range(qtd)]

    elif op_atual == "eq":
        st.header("📐 Gerador de Equações")
        grau = st.radio("Grau:", ["1º Grau", "2º Grau"], horizontal=True)
        if st.button("Gerar Preview"):
            qs = [f"{random.randint(2,9)}x + {random.randint(1,20)} = {random.randint(21,99)}" if grau == "1º Grau" else f"x² + {random.randint(2,8)}x + {random.randint(1,12)} = 0" for _ in range(8)]
            st.session_state.preview_questoes = [f"t. Equações de {grau}"] + qs

    elif op_atual == "col":
        st.header("📚 Colegial (Frações)")
        if st.button("Gerar Preview"):
            st.session_state.preview_questoes = ["t. Exercícios de Frações"] + [f"{random.randint(1,9)}/{random.randint(2,5)} + {random.randint(1,9)}/{random.randint(2,5)} =" for _ in range(8)]

    elif op_atual == "alg":
        st.header("⚖️ Álgebra Linear")
        if st.button("Gerar Preview"):
            st.session_state.preview_questoes = ["t. Álgebra Linear", "1. Resolva os sistemas:"] + [f"System {i+1}: {random.randint(1,5)}x + {random.randint(1,5)}y = {random.randint(10,30)}" for i in range(4)]

    elif op_atual == "man":
        st.header("📄 Gerador Manual")
        txt_m = st.text_area("Digite as questões:", height=200)
        if st.button("Gerar Preview"):
            st.session_state.preview_questoes = txt_m.split('\n')

    # --- LÓGICA DAS 3 FERRAMENTAS ONLINE ---
    elif op_atual == "calc_f":
        st.header("𝑓(x) Calculadora de Funções")
        f_in = st.text_input("Função f(x):", "x**2 + 5*x + 6")
        x_in = st.number_input("Valor de x:", value=1.0)
        if st.button("Calcular"):
            try:
                res = eval(f_in.replace('x', f'({x_in})'))
                st.success(f"Resultado: f({x_in}) = {res}")
            except Exception as e: st.error(f"Erro na fórmula: {e}")

    elif op_atual == "pemdas":
        st.header("📊 Resolutor de Expressões")
        expr = st.text_input("Expressão:", "2 + 3 * (10 / 2)")
        if st.button("Resolver"):
            try: st.info(f"Resultado: {eval(expr)}")
            except: st.error("Expressão inválida.")

    elif op_atual == "fin":
        st.header("💰 Calculadora Financeira")
        c_pv, c_tx, c_tp = st.columns(3)
        pv = c_pv.number_input("Capital (R$):", 0.0)
        tx = c_tx.number_input("Taxa (% ao mês):", 0.0)
        tp = c_tp.number_input("Tempo (meses):", 0)
        if st.button("Calcular Juros Compostos"):
            fv = pv * (1 + tx/100)**tp
            st.metric("Montante Final", f"R$ {fv:.2f}")
# --- 6. VISUALIZAÇÃO UNIFICADA (CARDS NA TELA) ---
questoes_preview = st.session_state.get('preview_questoes', [])
menu_atual = st.session_state.get('sub_menu', None)

if questoes_preview and menu_atual in ["op", "eq", "col", "alg", "man"]:
    st.divider()
    if os.path.exists("cabecalho.png"): 
        st.image("cabecalho.png", use_container_width=True)
    
    letras_tela = "abcdefghijklmnopqrstuvwxyz"
    l_idx = 0
    
    for q in questoes_preview:
        line = q.strip()
        if not line: continue
        
        # TÍTULO (Centralizado)
        if line.lower().startswith("t."):
            st.markdown(f"<h2 style='text-align: center; color: #007bff; margin-top: 20px;'>{line[2:].strip()}</h2>", unsafe_allow_html=True)
            l_idx = 0
            
        # MODO M (Alinhado à Esquerda - Estilo Título)
        elif line.startswith("-M"):
            st.markdown(f"<h2 style='text-align: left; color: #333; margin-top: 15px; margin-bottom: 5px;'>{line[1:].strip()}</h2>", unsafe_allow_html=True)
            l_idx = 0
        
        # SEÇÕES NUMÉRICAS (Espaçamento reduzido na tela)
        elif re.match(r'^\d+', line):
            st.markdown(f"<div style='margin-top: 10px; margin-bottom: 0px;'><b>{line}</b></div>", unsafe_allow_html=True)
            l_idx = 0
            
        # ITENS EM COLUNAS
        else:
            cols = st.columns(2)
            col_target = cols[0] if l_idx % 2 == 0 else cols[1]
            with col_target:
                st.markdown("<div style='margin: -5px 0;'>", unsafe_allow_html=True)
                with st.container(border=True):
                    st.write(f"**{letras_tela[l_idx%26]})** {line}")
                st.markdown("</div>", unsafe_allow_html=True)
            l_idx += 1

# --- 7. EXPORTAÇÃO PDF A4 (COMPACTO E ALINHADO) ---
st.markdown("---")
st.subheader("📥 Exportar Atividade Finalizada")

def gerar_pdf_final(com_cabecalho):
    letras_pdf = "abcdefghijklmnopqrstuvwxyz"
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_margins(15, 15, 15)
    
    # Início do Y (Cabeçalho ou Topo)
    y_at = 55 if (com_cabecalho and os.path.exists("cabecalho.png")) else 15
    if com_cabecalho and os.path.exists("cabecalho.png"):
        pdf.image("cabecalho.png", x=12.5, y=10, w=185)

    l_pdf_idx = 0
    y_base = y_at
    
    for q in questoes_preview:
        line = q.strip()
        if not line: continue
        
        # 1. TÍTULO PRINCIPAL
        if line.lower().startswith("t."):
            pdf.set_font("Arial", 'B', 16)
            pdf.set_y(y_at + 5)
            pdf.cell(0, 10, clean_txt(line[2:]), ln=True, align='C')
            y_at = pdf.get_y() + 2
            l_pdf_idx = 0
            
        # 2. MODO M (Esquerda, estilo Título)
        elif line.startswith("-M"):
            pdf.set_font("Arial", 'B', 16)
            pdf.set_y(y_at + 4)
            pdf.cell(0, 10, clean_txt(line[1:]), ln=True, align='L')
            y_at = pdf.get_y() + 2
            l_pdf_idx = 0
            
        # 3. SEÇÕES NUMERADAS (Mais próximas)
        elif re.match(r'^\d+', line):
            pdf.set_font("Arial", 'B', 12)
            # Salto mínimo entre o item anterior e o novo número
            salto = 4 if l_pdf_idx > 0 else 1
            pdf.set_y(y_at + salto)
            pdf.multi_cell(0, 6, clean_txt(line)) # Altura 6 para compactar
            y_at = pdf.get_y() + 0.5
            l_pdf_idx = 0
            
        # 4. ITENS (a, b, c...)
        else:
            pdf.set_font("Arial", size=11)
            txt_item = f"{letras_pdf[l_pdf_idx%26]}) {clean_txt(line)}"
            
            if l_pdf_idx % 2 == 0:
                y_base = y_at
                pdf.set_xy(15, y_base + 0.5)
                pdf.multi_cell(90, 6, txt_item) # Altura 6
                y_prox = pdf.get_y()
            else:
                pdf.set_xy(110, y_base + 0.5)
                pdf.multi_cell(85, 6, txt_item)
                y_at = max(y_prox, pdf.get_y())
            l_pdf_idx += 1
    
    return pdf.output(dest='S').encode('latin-1')

# Interface de Botões
c1, c2 = st.columns(2)
with c1:
    if st.button("📄 PDF COM Cabeçalho", use_container_width=True):
        try:
            pdf_data = gerar_pdf_final(True)
            st.download_button("✅ Baixar PDF Completo", pdf_data, "atividade_topo.pdf", "application/pdf")
        except Exception as e: st.error(f"Erro: {e}")
        
with c2:
    if st.button("📄 PDF SEM Cabeçalho", use_container_width=True):
        try:
            pdf_data = gerar_pdf_final(False)
            st.download_button("✅ Baixar PDF Simples", pdf_data, "atividade_limpa.pdf", "application/pdf")
        except Exception as e: st.error(f"Erro: {e}")
