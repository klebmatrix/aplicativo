import streamlit as st
import os
import math
from cryptography.fernet import Fernet

# --- 1. SEGURANÇA ---
# Esse PIN é o que a chave mestra precisa descriptografar para dar acesso "admin"
PIN_CRIPTOGRAFADO = "gAAAAABpdRRwrtzON4oc6ayd3fx1LjLjX8TjRj7riCkHHuOpi0lcYFAu04KEXEo8d3-GJz9HmpP-AjvbLOLzr6zC6GMUvOCP1A=="

def validar_acesso(pin_digitado):
    # Puxa as senhas do painel Secrets do Streamlit
    try:
        senha_aluno = str(st.secrets["acesso_aluno"]).strip()
        chave_mestra = str(st.secrets["chave_mestra"]).strip()
        
        # Teste 1: É Aluno?
        if pin_digitado == senha_aluno:
            return "aluno"
            
        # Teste 2: É Professor? (Usando a chave Fernet)
        # Limpa o 'b' ou aspas se você colou errado
        chave_limpa = chave_mestra.replace("b'", "").replace("'", "").replace('"', "")
        f = Fernet(chave_limpa.encode())
        pin_mestre_decifrado = f.decrypt(PIN_CRIPTOGRAFADO.encode()).decode()
        
        if pin_digitado == pin_mestre_decifrado:
            return "admin"
    except Exception as e:
        # Se quiser ver o erro durante o teste, desmarque a linha abaixo:
        # st.sidebar.error(f"Erro técnico: {e}")
        pass
        
    return "negado"

st.set_page_config(page_title="Quantum Math Lab", layout="wide")

# Inicializa as variáveis de navegação
if 'perfil' not in st.session_state:
    st.session_state.perfil = None

# --- 2. TELA DE LOGIN ---
if st.session_state.perfil is None:
    st.title("🔐 Quantum Math Lab")
    pin = st.text_input("PIN de Acesso:", type="password")
    
    if st.button("Entrar"):
        acesso = validar_acesso(pin)
        if acesso != "negado":
            st.session_state.perfil = acesso
            st.rerun() # FORÇA O APP A RECARREGAR E MOSTRAR O MENU
        else:
            st.error("PIN incorreto ou Chave Mestra inválida.")
    st.stop()

# --- 3. INTERFACE (SÓ APARECE APÓS LOGIN) ---
else:
    # ... (O restante do seu código de menus continua aqui)
    st.sidebar.success(f"Conectado como: {st.session_state.perfil.upper()}")