import streamlit as st
import math
import numpy as np
import os
import random
import re
from fpdf import FPDF

# --- 1. FUNÇÕES GLOBAIS (DEFINIDAS NO TOPO) ---

def tratar_texto_pdf(text):
    """Garante nitidez e evita caracteres que quebram o PDF padrão"""
    if not text: return ""
    return str(text).replace("√", "V").replace("²", "^2").replace("³", "^3")

def validar_acesso(pin_digitado):
    """Validação de PIN com base nos Secrets (Render/Streamlit)"""
    senha_aluno = str(st.secrets.get("acesso_aluno", "123456")).strip()
    senha_prof = str(st.secrets.get("chave_mestra", "chave_mestra")).strip().lower()
    if pin_digitado == senha_aluno: return "aluno"
    elif pin_digitado == senha_prof: return "admin"
    return "negado"

# --- 2. CONFIGURAÇÃO ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide", page_icon="🚀")

# Inicialização de estados
for key in ['perfil', 'sub_menu', 'preview_questoes', 'gabarito']:
    if key not in st.session_state:
        st.session_state[key] = [] if key in ['preview_questoes', 'gabarito'] else None

# --- 3. LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Login")
    pin = st.text_input("PIN de Acesso:", type="password", max_chars=8)
    if st.button("Entrar"):
        acesso = validar_acesso(pin)
        if acesso != "negado":
            st.session_state.perfil = acesso
            st.rerun()
        else:
            st.error("PIN incorreto ou acesso negado.")
    st.stop()

# --- 4. INTERFACE E MENU LATERAL ---
perfil = st.session_state.perfil
st.sidebar.title(f"🚀 {'Professor' if perfil == 'admin' else 'Estudante'}")
usar_cabecalho = st.sidebar.checkbox("Incluir Cabeçalho no PDF", value=True)

# NOVO: SELETOR DE COLUNAS
layout_colunas = st.sidebar.selectbox("Layout dos Itens:", ["1 Coluna", "2 Colunas", "3 Colunas"], index=1)

if st.sidebar.button("🧹 Limpar Tudo"):
    st.session_state.preview_questoes = []
    st.session_state.sub_menu = None
    st.rerun()

if st.sidebar.button("Sair/Logout"):
    st.session_state.clear()
    st.rerun()

# --- 5. PAINEL ADMIN ---
if perfil == "admin":
    st.title("🛠️ Painel de Controle")
    st.subheader("📝 Geradores de Atividades (PDF)")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: 
        if st.button("🔢 Operações", use_container_width=True): st.session_state.sub_menu = "op"
    with c2: 
        if st.button("📐 Equações", use_container_width=True): st.session_state.sub_menu = "eq"
    with c3: 
        if st.button("📚 Colegial", use_container_width=True): st.session_state.sub_menu = "col"
    with c4: 
        if st.button("⚖️ Álgebra", use_container_width=True): st.session_state.sub_menu = "alg"
    with c5: 
        if st.button("📄 Manual", use_container_width=True): st.session_state.sub_menu = "man"

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

    if op_atual == "op":
        st.header("🔢 Gerador de Operações")
        escolhas = st.multiselect("Sinais:", ["+", "-", "x", "÷"], ["+", "-"])
        num_ini = st.number_input("Questão inicial nº:", 1)
        qtd = st.number_input("Qtd de itens:", 4, 30, 10)
        if st.button("Gerar Preview"):
            st.session_state.preview_questoes = ["t. Atividade de Operações", f"{num_ini}. Calcule:"] + \
                [f"{random.randint(10,500)} {random.choice(escolhas)} {random.randint(2,50)} =" for _ in range(qtd)]

    elif op_atual == "eq":
        st.header("📐 Equações")
        grau = st.radio("Grau:", ["1º Grau", "2º Grau"], horizontal=True)
        if st.button("Gerar Preview"):
            qs = [f"{random.randint(2,9)}x + {random.randint(1,20)} = {random.randint(21,99)}" if grau == "1º Grau" else f"x^2 + {random.randint(2,8)}x + {random.randint(1,12)} = 0" for _ in range(8)]
            st.session_state.preview_questoes = [f"t. Equações de {grau}", "1. Resolva as equações:"] + qs

    elif op_atual == "man":
        st.header("📄 Módulo Manual")
        txt_m = st.text_area("Cole suas questões aqui:", height=250)
        if st.button("Gerar Atividade Manual"):
            st.session_state.preview_questoes = txt_m.split('\n')

    elif op_atual == "calc_f":
        st.header("𝑓(x) Funções")
        f_in = st.text_input("Função:", "x**2 + 5*x + 6")
        x_val = st.number_input("Valor de x:", value=2.0)
        if st.button("Calcular"):
            try:
                res = eval(f_in.replace('x', f'({x_val})'))
                st.success(f"Resultado: f({x_val}) = {res}")
            except Exception as e: st.error(f"Erro na fórmula: {e}")

    elif op_atual == "pemdas":
        st.header("📊 PEMDAS")
        expr = st.text_input("Expressão matemática:", "2 + 3 * (10 / 2)**2")
        if st.button("Resolver"):
            try: st.info(f"Resultado: {eval(expr)}")
            except: st.error("Expressão inválida.")

    elif op_atual == "fin":
        st.header("💰 Matemática Financeira")
        c_pv, c_tx, c_tp = st.columns(3)
        pv = c_pv.number_input("Capital (R$):", 1000.0)
        tx = c_tx.number_input("Taxa (% a.m.):", 1.0)
        tp = c_tp.number_input("Tempo (meses):", 12)
        if st.button("Calcular Montante (Juros Compostos)"):
            fv = pv * (1 + tx/100)**tp
            st.metric("Montante Final", f"R$ {fv:.2f}")

# --- 6. PDF ENGINE (AJUSTADO PARA COLUNAS PARALELAS) ---
if st.session_state.preview_questoes:
    st.subheader("👁️ Preview da Atividade")
    for item in st.session_state.preview_questoes:
        st.write(item)

    def export_pdf():
        try:
            pdf = FPDF()
            pdf.add_page()
            y = 20
            
            if usar_cabecalho and os.path.exists("cabecalho.png"):
                pdf.image("cabecalho.png", 10, 10, 190)
                y = 65

            letras = "abcdefghijklmnopqrstuvwxyz"
            l_idx = 0
            
            # Logica de colunas baseada na sua escolha
            if "1 Coluna" in layout_colunas: n_cols = 1
            elif "2 Colunas" in layout_colunas: n_cols = 2
            else: n_cols = 3
            
            largura_col = 190 / n_cols
            y_inicio_linha = y

            for line in st.session_state.preview_questoes:
                line = line.strip()
                if not line: continue

                # TÍTULO (t.) ou QUESTÃO (1.) - Sempre ocupam a linha toda
                if line.lower().startswith("t.") or re.match(r'^\d+\.', line):
                    if l_idx > 0: y = pdf.get_y() + 5
                    
                    is_titulo = line.lower().startswith("t.")
                    pdf.set_font("Helvetica", 'B', 14 if is_titulo else 12)
                    pdf.set_xy(10, y)
                    txt_final = line[2:].strip() if is_titulo else line
                    pdf.multi_cell(190, 10, tratar_texto_pdf(txt_final), align='C' if is_titulo else 'L')
                    y = pdf.get_y() + 2
                    y_inicio_linha = y
                    l_idx = 0
                
                # ITENS (a, b, c) - Aqui entra o paralelo
                else:
                    pdf.set_font("Helvetica", size=12)
                    col_atual = l_idx % n_cols
                    
                    # Se voltar para a primeira coluna, atualiza o Y para a próxima "fileira"
                    if col_atual == 0 and l_idx > 0:
                        y_inicio_linha = pdf.get_y()
                    
                    x_pos = 10 + (col_atual * largura_col)
                    pdf.set_xy(x_pos, y_inicio_linha)
                    
                    conteudo = re.sub(r'^[.\s]+', '', line)
                    pdf.multi_cell(largura_col - 5, 7, f"{letras[l_idx % 26]}) {tratar_texto_pdf(conteudo)}", align='L')
                    l_idx += 1
            
            return bytes(pdf.output())
        except Exception as e:
            st.error(f"Erro no PDF: {e}")
            return None

    pdf_data = export_pdf()
    if pdf_data:
        st.download_button("📥 Baixar PDF", data=pdf_data, file_name="atividade.pdf", mime="application/pdf")