import streamlit as st
import os
from cryptography.fernet import Fernet
import sympy as sp
import numpy as np

# --- CONFIGURAÇÃO DE SEGURANÇA ---
# COPIE O SEGUNDO CÓDIGO DO GERADOR E COLE AQUI:
PIN_CRIPTOGRAFADO = "gAAAAABpdOfBi15EU9FFIHM43LlR-F8OmmakmUbq1Maslply2B2PNjORPbq3ymeC8iKge9Nc0f_o2YOdq1qGAOJY69ALmy6bmg=="

def validar_acesso(pin_digitado):
    try:
        chave = os.environ.get('CHAVE_MESTRA')
        if not chave:
            return False
        f = Fernet(chave.encode())
        pin_real = f.decrypt(PIN_CRIPTOGRAFADO.encode()).decode()
        return pin_digitado == pin_real
    except:
        return False

# --- CONTROLE DE LOGIN ---
if 'logado' not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    st.title("🌌 Quantum Math - Acesso Restrito")
    entrada = st.text_input("Digite seu PIN (6-8 dígitos):", type="password")
    if st.button("Desbloquear"):
        if validar_acesso(entrada):
            st.session_state.logado = True
            st.rerun()
        else:
            st.error("PIN incorreto ou erro de configuração.")
    st.stop()

# --- INTERFACE PRINCIPAL (PÓS-LOGIN) ---
st.sidebar.title("Módulos Matemáticos")
area = st.sidebar.selectbox("Área de Estudo", ["Mecânica Quântica", "Cálculo Complexo", "GeoGebra"])

if area == "Mecânica Quântica":
    st.header("⚛️ Operadores e Matrizes Quânticas")
    st.write("Cálculo da Matriz de Pauli $\sigma_z$ aplicada a um estado:")
    
    # Exemplo de Álgebra Linear Quântica
    sigma_z = np.array([[1, 0], [0, -1]])
    st.code(f"Matriz Sigma Z:\n{sigma_z}")
    
    st.latex(r"i\hbar \frac{\partial}{\partial t} \Psi(\mathbf{r},t) = \hat{H} \Psi(\mathbf{r},t)")

elif area == "Cálculo Complexo":
    st.header("🔢 Integrais Simbólicas")
    x = sp.Symbol('x')
    f = sp.exp(-x**2)
    st.latex(sp.latex(sp.Integral(f, (x, -sp.oo, sp.oo))))
    st.success(f"Resultado: {sp.integrate(f, (x, -sp.oo, sp.oo))}")

elif area == "GeoGebra":
    st.header("📐 Visualização Dinâmica")
    st.components.v1.iframe("https://www.geogebra.org/classic", height=600)