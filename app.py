import streamlit as st
import os
import numpy as np
from cryptography.fernet import Fernet
import pandas as pd
from fpdf import FPDF
import random

# --- SEGURANÇA ---
PIN_CRIPTOGRAFADO = "gAAAAABpdRRwrtzON4oc6ayd3fx1LjLjX8TjRj7riCkHHuOpi0lcYFAu04KEXEo8d3-GJz9HmpP-AjvbLOLzr6zC6GMUvOCP1A=="

def validar_acesso(pin_digitado):
    try:
        chave = os.environ.get('chave_mestra')
        if not chave: return "erro_env"
        chave = chave.strip().replace("'", "").replace('"', "").replace('b', '', 1) if chave.startswith('b') else chave.strip()
        f = Fernet(chave.encode())
        return "ok" if pin_digitado == f.decrypt(PIN_CRIPTOGRAFADO.strip().encode()).decode() else "erro_senha"
    except: return "erro_token"

# --- FUNÇÃO GERADORA DE PDF ---
def gerar_pdf(titulo, conteudo):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, txt=titulo, ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    for linha in conteudo:
        pdf.multi_cell(0, 10, txt=linha)
    return pdf.output(dest='S').encode('latin-1')

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Math Master Pro", layout="wide")
if 'logado' not in st.session_state: st.session_state.logado = False

if not st.session_state.logado:
    st.title("🔐 Autenticação")
    pin = st.text_input("Senha:", type="password")
    if st.button("Entrar"):
        res = validar_acesso(pin)
        if res == "ok": st.session_state.logado = True; st.rerun()
        else: st.error(f"Erro: {res}")
    st.stop()

# --- MENU ---
menu = st.sidebar.radio("Módulos:", ["Equações", "Sistemas", "Finanças", "Gerador de Atividades"])

# --- MÓDULO: EQUAÇÕES (COM PDF) ---
if menu == "Equações":
    st.header("🔍 Resolutor de Equações")
    a = st.number_input("Coeficiente a (≠ 0):", value=1, step=1)
    b = st.number_input("Termo b:", value=0, step=1)
    c = st.number_input("Igual a c:", value=0, step=1)
    
    if a != 0 and st.button("Resolver e Gerar Relatório"):
        x = (c - b) / a
        txt_res = f"Equação: {a}x + {b} = {c}\nResultado: x = {x}"
        st.success(txt_res)
        
        pdf_data = gerar_pdf("Relatorio de Equacao", [txt_res, "Calculo realizado via Quantum Math Lab."])
        st.download_button("📥 Baixar PDF", pdf_data, "resultado.pdf", "application/pdf")

# --- NOVO MÓDULO: GERADOR DE ATIVIDADES ---
elif menu == "Gerador de Atividades":
    st.header("📝 Gerador de Exercícios Aleatórios")
    qtd = st.slider("Quantidade de exercícios:", 1, 10, 5)
    
    if st.button("Gerar Nova Lista de Atividades"):
        lista_exercicios = []
        for i in range(qtd):
            ex_tipo = random.choice(["1grau", "geometria"])
            if ex_tipo == "1grau":
                raio_a = random.randint(1, 10)
                raio_b = random.randint(1, 50)
                raio_c = random.randint(1, 100)
                lista_exercicios.append(f"{i+1}) Resolva: {raio_a}x + {raio_b} = {raio_c}")
            else:
                r_geo = random.randint(1, 20)
                lista_exercicios.append(f"{i+1}) Calcule o volume de uma esfera de raio {r_geo} (use pi=3.14)")
        
        st.session_state.lista = lista_exercicios

    if 'lista' in st.session_state:
        for ex in st.session_state.lista:
            st.write(ex)
            
        pdf_atividades = gerar_pdf("Lista de Atividades Matematicas", st.session_state.lista)
        st.download_button("📥 Baixar Lista em PDF", pdf_atividades, "atividades.pdf", "application/pdf")