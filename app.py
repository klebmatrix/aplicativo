import streamlit as st
import os
import numpy as np
import pandas as pd
from cryptography.fernet import Fernet
from fpdf import FPDF
import math

# --- 1. SEGURANÇA (PIN de 6 dígitos) ---
def validar_acesso(pin_digitado):
    # Acesso Estudante
    senha_aluno_env = os.environ.get('acesso_aluno', '').strip().replace("'", "").replace('"', "")
    if senha_aluno_env and pin_digitado == senha_aluno_env:
        return "aluno"
    
    # Acesso Professor
    try:
        chave = os.environ.get('chave_mestra', '').strip().replace("'", "").replace('"', "")
        if not chave: 
            # Fallback para teste local
            if pin_digitado == "admin": return "admin"
            return "erro_env"
            
        if chave.startswith('b'): chave = chave[1:]
        
        f = Fernet(chave.encode())
        # O PIN que você criptografou (Atualizado para Qzj7bJEy)
        PIN_CRIPTO = "gAAAAABpd_xXuRomCwkP5ndxDS1kG5MB5Zk0po7cJLo-mAS1pqdJQjRsJ-Bp6ShKov8PNRP8-vzHwpDp93K2h1vC9uapl4aAzw=="
        
        if pin_digitado == f.decrypt(PIN_CRIPTO.encode()).decode():
            return "admin"
    except: 
        pass
    return "negado"

# Configuração da página deve ser a primeira chamada do Streamlit
st.set_page_config(page_title="Quantum Math Lab", layout="wide", page_icon="⚛️")

# Inicialização do estado
if 'perfil' not in st.session_state: 
    st.session_state.perfil = None

# --- 2. TELA DE LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Quantum Math Lab")
    st.subheader("Acesso ao Sistema")
    
    pin = st.text_input("PIN de Acesso:", type="password")
    if st.button("Entrar"):
        acesso = validar_acesso(pin)
        if acesso != "negado":
            st.session_state.perfil = acesso
            st.rerun()
        else:
            st.error("Acesso Negado. Verifique as chaves no Render.")
            st.info("Dica: Se estiver testando localmente, tente o PIN 'admin'.")
    st.stop()

# --- 3. DASHBOARD INTEGRADO ---
else:
    perfil = st.session_state.perfil
    st.sidebar.title(f"🚀 {'PROFESSOR' if perfil == 'admin' else 'ESTUDANTE'}")
    
    # Menu dinâmico
    itens = ["Atividades (Drive)", "Expressões (PEMDAS)", "Equações 1º/2º Grau", "Cálculo de Funções", "Logaritmos"]
    if perfil == "admin":
        itens += ["Gerador de Atividades (PDF)", "Sistemas Lineares", "Matrizes", "Financeiro"]
        
    menu = st.sidebar.radio("Navegação:", itens)
    
    if st.sidebar.button("Sair"):
        st.session_state.perfil = None
        st.rerun()

    # --- MÓDULOS ---
    with st.container(key=f"content_{menu.lower().replace(' ', '_')}"):
        if menu == "Atividades (Drive)":
            st.header("📝 Pasta do Aluno")
            st.info("Acesse os materiais didáticos e atividades compartilhadas.")
            st.link_button("📂 Abrir Drive", "https://drive.google.com/drive/folders/1NkFeom_k3LUJYAFVBBDu4GD5aYVeNEZc?usp=drive_link")

        elif menu == "Expressões (PEMDAS)":
            st.header("🧮 Hierarquia PEMDAS")
            st.write("Resolva expressões respeitando a ordem: Parênteses, Expoentes, Multiplicação/Divisão, Adição/Subtração.")
            
            exp = st.text_input("Digite a Expressão:", value="(10+5)*2")
            if st.button("Calcular"):
                try:
                    # Substituição segura para potência
                    safe_exp = exp.replace('^', '**')
                    res = eval(safe_exp, {"__builtins__": None}, {"math": math, "sqrt": math.sqrt})
                    st.success(f"Resultado: {res}")
                except Exception as e:
                    st.error(f"Erro na sintaxe: {e}")

        elif menu == "Equações 1º/2º Grau":
            st.header("📐 Equações")
            st.latex(r"ax^2 + bx + c = 0")
            
            c1, c2, c3 = st.columns(3)
            a = c1.number_input("Valor de a:", value=1.0, key="eq_a")
            b = c2.number_input("Valor de b:", value=-5.0, key="eq_b")
            c = c3.number_input("Valor de c:", value=6.0, key="eq_c")
            
            if st.button("Resolver Equação"):
                if a == 0:
                    if b != 0:
                        st.info(f"Equação de 1º Grau: x = {-c/b:.2f}")
                    else:
                        st.error("Equação inválida.")
                else:
                    delta = b**2 - 4*a*c
                    st.write(f"**Delta (Δ):** {delta}")
                    if delta >= 0:
                        x1 = (-b + math.sqrt(delta)) / (2*a)
                        x2 = (-b - math.sqrt(delta)) / (2*a)
                        st.success(f"x1 = {x1:.2f} | x2 = {x2:.2f}")
                    else:
                        st.error("Delta Negativo: Não possui raízes reais.")

        elif menu == "Cálculo de Funções":
            st.header("𝑓(x) Funções")
            f_in = st.text_input("Defina f(x):", "2*x + 5")
            v_x = st.number_input("Valor de x:", 0.0)
            if st.button("Calcular f(x)"):
                try:
                    # Substituição simples de x pelo valor
                    res_f = eval(f_in.replace('x', f'({v_x})').replace('^', '**'))
                    st.success(f"f({v_x}) = {res_f}")
                except Exception as e:
                    st.error(f"Erro na função: {e}")

        elif menu == "Logaritmos":
            st.header("🔢 Logaritmos")
            st.latex(r"\log_{base}(num)")
            
            c1, c2 = st.columns(2)
            base = c1.number_input("Base:", value=10.0, key="log_base")
            num = c2.number_input("Logaritmando:", value=100.0, key="log_num")
            
            if st.button("Calcular Logaritmo"):
                try:
                    if num > 0 and base > 0 and base != 1:
                        st.success(f"Resultado: {math.log(num, base):.4f}")
                    else:
                        st.error("Valores inválidos para logaritmo.")
                except Exception as e:
                    st.error(f"Erro: {e}")

        # Módulos do Professor (Admin)
        elif menu == "Gerador de Atividades (PDF)":
            st.header("📄 Gerador de Material Didático")
            st.write("Ferramenta exclusiva para criação de listas de exercícios em PDF.")
            st.info("Módulo em desenvolvimento.")

        elif menu == "Sistemas Lineares":
            st.header("📏 Resolução de Sistemas")
            st.write("Resolva sistemas de equações lineares (Ax = B).")
            st.info("Módulo em desenvolvimento.")

        elif menu == "Matrizes":
            st.header("🧮 Operações com Matrizes")
            st.write("Cálculo de determinantes, transpostas e inversas.")
            st.info("Módulo em desenvolvimento.")
            
        elif menu == "Financeiro":
            st.header("💰 Matemática Financeira")
            st.write("Juros simples, compostos e amortizações.")
            st.info("Módulo em desenvolvimento.")
