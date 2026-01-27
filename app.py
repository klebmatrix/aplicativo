import streamlit as st
import math
import numpy as np

# --- 1. SEGURANÇA E LOGIN ---
def validar_acesso(pin_digitado):
    try:
        # Puxa as senhas configuradas nos Secrets do Streamlit
        senha_aluno = str(st.secrets["acesso_aluno"]).strip()
        senha_professor = str(st.secrets["chave_mestra"]).strip()
        
        if pin_digitado == senha_aluno:
            return "aluno"
        elif pin_digitado == senha_professor:
            return "admin"
    except:
        st.error("Erro: Configure 'acesso_aluno' e 'chave_mestra' nos Secrets do Streamlit!")
    return "negado"

st.set_page_config(page_title="Quantum Math Lab", layout="wide")

if 'perfil' not in st.session_state:
    st.session_state.perfil = None

# --- TELA DE LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Quantum Math Lab")
    pin = st.text_input("Digite seu PIN ou Chave Mestra:", type="password")
    if st.button("Entrar"):
        acesso = validar_acesso(pin)
        if acesso != "negado":
            st.session_state.perfil = acesso
            st.rerun()
        else:
            st.error("Acesso negado.")
    st.stop()

# --- 2. INTERFACE PÓS-LOGIN ---
else:
    perfil = st.session_state.perfil
    st.sidebar.title(f"🚀 {'Professor' if perfil == 'admin' else 'Estudante'}")
    
    # Menus disponíveis
    itens = ["Atividades (Drive)", "Expressões (PEMDAS)", "Equações (1º e 2º Grau)", "Cálculo de Funções", "Logaritmos"]
    if perfil == "admin":
        itens += ["Gerador de Atividades", "Sistemas Lineares", "Matrizes"]
        
    menu = st.sidebar.radio("Navegação:", itens)
    if st.sidebar.button("Sair"):
        st.session_state.perfil = None
        st.rerun()

    # --- EQUAÇÕES (CORRIGIDO) ---
    if menu == "Equações (1º e 2º Grau)":
        st.header("📐 Resolução de Equações")
        tipo = st.selectbox("Escolha o tipo:", ["1º Grau (ax + b = 0)", "2º Grau (ax² + bx + c = 0)"])
        
        if tipo == "1º Grau (ax + b = 0)":
            a = st.number_input("Valor de a:", value=1.0)
            b = st.number_input("Valor de b:", value=0.0)
            if st.button("Resolver"):
                if a != 0:
                    x = -b / a
                    st.success(f"Resultado: x = {x:.2f}")
                else:
                    st.error("O valor de 'a' não pode ser zero.")
        
        else:
            col1, col2, col3 = st.columns(3)
            with col1: a2 = st.number_input("a:", value=1.0)
            with col2: b2 = st.number_input("b:", value=-5.0)
            with col3: c2 = st.number_input("c:", value=6.0)
            
            if st.button("Calcular Raízes"):
                delta = (b2**2) - (4*a2*c2)
                st.write(f"Delta (Δ) = {delta}")
                if delta > 0:
                    x1 = (-b2 + math.sqrt(delta)) / (2*a2)
                    x2 = (-b2 - math.sqrt(delta)) / (2*a2)
                    st.success(f"Duas raízes reais: x1 = {x1:.2f} e x2 = {x2:.2f}")
                elif delta == 0:
                    x = -b2 / (2*a2)
                    st.success(f"Uma raiz real: x = {x:.2f}")
                else:
                    st.error("Não existem raízes reais (Δ < 0).")

    # --- GERADOR DE ATIVIDADES (SÓ PROFESSOR) ---
    elif menu == "Gerador de Atividades":
        st.header("📄 Gerador de Atividades")
        st.write("Configurações de impressão e exportação.")
        titulo = st.text_input("Título da Atividade:", "Lista de Exercícios - Física Quântica")
        num_questoes = st.slider("Número de Questões:", 1, 20, 5)
        
        if st.button("Gerar Prévia"):
            st.info(f"Gerando lista: {titulo} com {num_questoes} questões...")
            # Aqui você pode adicionar a lógica de PDF com FPDF se desejar
            st.success("Prévia gerada com sucesso!")

    # --- LOGARITMOS ---
    elif menu == "Logaritmos":
        st.header("🔢 Logaritmos")
        base = st.number_input("Base:", value=10.0)
        logaritmando = st.number_input("Logaritmando:", value=100.0)
        if st.button("Calcular"):
            st.success(f"Resultado: {math.log(logaritmando, base):.4f}")

    # --- OUTROS MENUS ---
    elif menu == "Atividades (Drive)":
        st.link_button("📂 Abrir Google Drive", "https://drive.google.com/drive/folders/1NkFeom_k3LUJYAFVBBDu4GD5aYVeNEZc")