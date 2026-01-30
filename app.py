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
# ADICIONADO: Inicializa o gabarito para não dar erro no PDF
if 'gabarito' not in st.session_state: st.session_state.gabarito = []

def clean_txt(text):
    """Trata potências e raízes para leitura humana no PDF (padrão latin-1)"""
    if not text: return ""
    text = str(text)
    text = text.replace("√", "V").replace("²", "^2").replace("³", "^3")
    return text.encode('latin-1', 'replace').decode('latin-1')

def validar_acesso(pin_digitado):
    senha_aluno = str(st.secrets.get("acesso_aluno", "123456")).strip()
    senha_prof = str(st.secrets.get("chave_mestra", "chave_mestra")).strip().lower()
    if pin_digitado == senha_aluno: return "aluno"
    elif pin_digitado == senha_prof: return "admin"
    return "negado"

# --- LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Login")
    pin = st.text_input("PIN (6 dígitos):", type="password", max_chars=8)
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

usar_cabecalho = st.sidebar.checkbox("Incluir Cabeçalho no PDF", value=True)

if st.sidebar.button("🧹 Limpar Tudo"):
    st.session_state.preview_questoes = []
    st.session_state.gabarito = []
    st.session_state.sub_menu = None
    st.rerun()

if st.sidebar.button("Sair/Logout"):
    for key in list(st.session_state.keys()): del st.session_state[key]
    st.rerun()

# --- PAINEL ADMIN ---
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

    # --- LÓGICA DOS GERADORES ---
    if op_atual == "op":
        st.header("🔢 Operações")
        escolhas = st.multiselect("Sinais:", ["+", "-", "x", "÷"], ["+", "-"])
        num_ini = st.number_input("Começar do número:", 1)
        qtd = st.number_input("Quantidade:", 4, 30, 10)
        if st.button("Gerar Preview"):
            st.session_state.preview_questoes = ["t. Atividade de Operações", f"{num_ini}. Calcule:"] + [f"{random.randint(10,500)} {random.choice(escolhas)} {random.randint(2,50)} =" for _ in range(qtd)]

    elif op_atual == "eq":
        st.header("📐 Equações")
        grau = st.radio("Grau:", ["1º Grau", "2º Grau"], horizontal=True)
        num_ini = st.number_input("Começar do número:", 1)
        if st.button("Gerar Preview"):
            qs = [f"{random.randint(2,9)}x + {random.randint(1,20)} = {random.randint(21,99)}" if grau == "1º Grau" else f"x^2 + {random.randint(2,8)}x + {random.randint(1,12)} = 0" for _ in range(8)]
            st.session_state.preview_questoes = [f"t. Equações de {grau}", f"{num_ini}. Resolva:"] + qs

    elif op_atual == "col":
        st.header("📚 Colegial (Temas)")
        temas = st.multiselect("Temas:", ["Frações", "Porcentagem", "Potenciação", "Radiciação"], ["Frações", "Porcentagem"])
        num_ini = st.number_input("Começar do número:", 1)
        qtd = st.number_input("Quantidade:", 4, 30, 10)
        if st.button("Gerar Preview") and temas:
            qs = [f"t. Exercícios Colegiais", f"{num_ini}. Resolva os itens:"]
            for _ in range(qtd):
                t = random.choice(temas)
                if t == "Frações": qs.append(f"{random.randint(1,9)}/{random.randint(2,5)} + {random.randint(1,9)}/{random.randint(2,5)} =")
                elif t == "Porcentagem": qs.append(f"{random.randint(5,95)}% de {random.randint(100,999)} =")
                elif t == "Potenciação": qs.append(f"{random.randint(2,12)}^2 =")
                elif t == "Radiciação": qs.append(f"√{random.choice([4, 9, 16, 25, 36, 49, 64, 81, 100])} =")
            st.session_state.preview_questoes = qs

    elif op_atual == "alg":
        st.header("⚖️ Álgebra (Sistemas)")
        tipos = st.multiselect("Tipos:", ["1º Grau", "2º Grau"], ["1º Grau"])
        num_ini = st.number_input("Começar do número:", 1)
        qtd = st.number_input("Quantidade:", 2, 10, 4)
        if st.button("Gerar Preview") and tipos:
            qs = ["t. Sistemas de Equações", f"{num_ini}. Resolva os sistemas abaixo:"]
            for i in range(qtd):
                t = random.choice(tipos)
                if t == "1º Grau": qs.append(f"{random.randint(1,5)}x + {random.randint(1,5)}y = {random.randint(10,40)}")
                else: qs.append(f"x^2 + y = {random.randint(10,30)} e x + y = {random.randint(2,10)}")
            st.session_state.preview_questoes = qs

    elif op_atual == "man":
        st.header("📄 Módulo Manual")
        txt_m = st.text_area("Digite ou cole suas questões aqui:", height=300)
        if st.button("Gerar Atividade Manual"):
            st.session_state.preview_questoes = txt_m.split('\n')

    elif op_atual == "calc_f":
        st.header("𝑓(x) Funções")
        f_in = st.text_input("Função:", "x**2 + 5*x + 6")
        x_in = st.number_input("Valor de x:", value=1.0)
        if st.button("Calcular"):
            try:
                res = eval(f_in.replace('x', f'({x_in})'))
                st.success(f"Resultado: f({x_in}) = {res}")
            except Exception as e: st.error(f"Erro: {e}")

    elif op_atual == "pemdas":
        st.header("📊 PEMDAS")
        expr = st.text_input("Expressão:", "2 + 3 * (10 / 2)")
        if st.button("Resolver"):
            try: st.info(f"Resultado: {eval(expr)}")
            except: st.error("Expressão inválida.")

    elif op_atual == "fin":
        st.header("💰 Financeira")
        c1, c2, c3 = st.columns(3)
        pv = c1.number_input("Capital (R$):", 0.0)
        tx = c2.number_input("Taxa (%):", 0.0)
        tp = c3.number_input("Tempo (meses):", 0)
        if st.button("Calcular"):
            fv = pv * (1 + tx/100)**tp
            st.metric("Montante Final", f"R$ {fv:.2f}")

# --- PDF E VISUALIZAÇÃO ---
if st.session_state.preview_questoes:
    st.divider()
    col_d1, col_d2 = st.columns(2)
    
    def export_pdf(com_gab):
        pdf = FPDF()
        pdf.add_page()
        y = 60 if (usar_cabecalho and os.path.exists("cabecalho.png")) else 20
        if usar_cabecalho and os.path.exists("cabecalho.png"): 
            pdf.image("cabecalho.png", 10, 10, 190)
        
        l_idx = 0
        letras_lista = "abcdefghijklmnopqrstuvwxyz"
        
        for q in st.session_state.preview_questoes:
            line = q.strip()
            if not line: continue
            
            if line.lower().startswith("t.") or re.match(r'^\d+', line):
                pdf.set_y(y + 5)
                pdf.set_font("Arial", 'B', 12)
                txt_limpo = line[2:].strip() if line.lower().startswith("t.") else line
                pdf.multi_cell(0, 10, clean_txt(txt_limpo))
                y = pdf.get_y()
                l_idx = 0
            else:
                pdf.set_font("Arial", size=12)
                pdf.set_y(y)
                pdf.set_x(15)
                item_txt = f"{letras_lista[l_idx % 26]}) {line}"
                pdf.multi_cell(0, 10, clean_txt(item_txt))
                y = pdf.get_y()
                l_idx += 1
        
        if com_gab and st.session_state.gabarito:
            pdf.add_page()
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(0, 10, "GABARITO", ln=1, align='C')
            pdf.set_font("Arial", size=12)
            for g in st.session_state.gabarito:
                pdf.cell(0, 8, clean_txt(g), ln=1)
        
        # CONSERTO AQUI: converter bytearray para bytes
        return bytes(pdf.output())

    with col_d1:
        # CONSERTO AQUI: chamar a função no momento do clique para evitar erros de fluxo
        if st.download_button("📥 Sem Gabarito", data=export_pdf(False), file_name="questoes.pdf", mime="application/pdf"):
            st.success("PDF gerado!")
    
    with col_d2:
        if st.download_button("📥 Com Gabarito", data=export_pdf(True), file_name="gabarito.pdf", mime="application/pdf"):
            st.success("Gabarito gerado!")

    for item in st.session_state.preview_questoes:
        st.write(item)