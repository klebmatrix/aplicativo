import streamlit as st
import os
import math
import numpy as np
from cryptography.fernet import Fernet

# --- 1. FUNÇÃO DE VALIDAÇÃO (CONEXÃO COM RENDER) ---
def validar_acesso(pin_digitado):
    # Puxa as variáveis brutas do Render
    # [cite: 2026-01-23] Puxando do ambiente, não do código
    aluno_env = os.environ.get('acesso_aluno', '').strip().replace("'", "").replace('"', "")
    mestre_env = os.environ.get('chave_mestra', '').strip().replace("'", "").replace('"', "")

    # Validação para Alunos
    if aluno_env and pin_digitado == aluno_env:
        return "aluno"
    
    # Validação para Professor (Usando a chave_mestra minúscula)
    # [cite: 2026-01-24]
    try:
        if mestre_env:
            # Limpa o formato da chave para o Fernet aceitar
            if mestre_env.startswith('b'): mestre_env = mestre_env[1:]
            
            f = Fernet(mestre_env.encode())
            
            # Token criptografado do seu PIN (Ajustado para 6-8 caracteres)
            # [cite: 2026-01-21]
            PIN_CRIPTO = "gAAAAABpdRRwrtzON4oc6ayd3fx1LjLjX8TjRj7riCkHHuOpi0lcYFAu04KEXEo8d3-GJz9HmpP-AjvbLOLzr6zC6GMUvOCP1A=="
            
            if pin_digitado == f.decrypt(PIN_CRIPTO.encode()).decode():
                return "admin"
    except Exception as e:
        # Se houver erro na chave mestre, o Python não trava, apenas nega
        pass
            
    return "negado"

# --- 2. CONFIGURAÇÃO DA INTERFACE ---
st.set_page_config(page_title="Quantum Math Lab", layout="wide")

if 'perfil' not in st.session_state:
    st.session_state.perfil = None

# --- 3. TELA DE LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Quantum Math Lab")
    pin = st.text_input("Digite o PIN de Acesso:", type="password")
    
    if st.button("Entrar"):
        resultado = validar_acesso(pin)
        if resultado != "negado":
            st.session_state.perfil = resultado
            st.rerun()
        else:
            st.error("PIN incorreto. Verifique as chaves no painel Environment do Render.")
    st.stop()

# --- 4. ÁREA LOGADA (PROFESSOR + ALUNO) ---
else:
    perfil = st.session_state.perfil
    st.sidebar.title(f"🚀 {'PAINEL PROFESSOR' if perfil == 'admin' else 'ÁREA ALUNO'}")
    
    # Menu dinâmico baseado no perfil detectado
    itens = ["Atividades", "Expressões (PEMDAS)", "Equações 1º/2º Grau", "Cálculo f(x)"]
    if perfil == "admin":
        itens += ["Sistemas Lineares", "Matrizes", "Gerador PDF"]
        
    menu = st.sidebar.radio("Navegação:", itens)
    
    if st.sidebar.button("Sair"):
        st.session_state.perfil = None
        st.rerun()

    # --- CONTEÚDO ---
    if menu == "Atividades":
        st.header("📝 Exercícios")
        st.link_button("📂 Abrir Drive", "https://drive.google.com/drive/folders/1NkFeom_k3LUJYAFVBBDu4GD5aYVeNEZc?usp=drive_link")

    elif menu == "Expressões (PEMDAS)":
        st.header("🧮 PEMDAS")
        
        exp = st.text_input("Expressão:", value="(10+5)*2")
        if st.button("Calcular"):
            try:
                res = eval(exp.replace('^', '**'), {"__builtins__": None}, {"math": math})
                st.success(f"Resultado: {res}")
            except:
                st.error("Erro na expressão.")

    elif menu == "Equações 1º/2º Grau":
        st.header("📐 Equações")
        st.latex(r"ax^2 + bx + c = 0")
        

[Image of the quadratic formula]

        a = st.number_input("a", value=1.0)
        b = st.number_input("b", value=-5.0)
        c = st.number_input("c", value=6.0)
        if st.button("Resolver"):
            delta = b**2 - 4*a*c
            if delta >= 0:
                x1 = (-b + math.sqrt(delta))/(2*a)
                x2 = (-b - math.sqrt(delta))/(2*a)
                st.success(f"x1 = {x1:.2f} | x2 = {x2:.2f}")
            else:
                st.error("Delta negativo.")