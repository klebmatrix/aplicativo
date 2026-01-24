import streamlit as st
import os
import numpy as np
from cryptography.fernet import Fernet

# --- CONFIGURAÇÃO DE SEGURANÇA ---
# Substitua pelo TOKEN que o comando do terminal gerou para você
PIN_CRIPTOGRAFADO = "gAAAAABpdPwNgg7J86tk5_CQCt9ZPF8JMjD2He9LQ79G3R7AH3excYYlXGJ5KvoFPPpHUbnNcuD1ndd9I3lovdyFBXH97hOD4w=="

def validar_acesso(pin_digitado):
    try:
        # Busca a variável em minúsculo conforme sua solicitação
        chave = os.environ.get('chave_mestra')
        if not chave:
            return False
        
        # Limpeza de caracteres da chave
        chave = chave.strip().replace("'", "").replace('"', "")
        if chave.startswith('b'): chave = chave[1:]
            
        f = Fernet(chave.encode())
        pin_real = f.decrypt(PIN_CRIPTOGRAFADO.strip().encode()).decode()
        return pin_digitado == pin_real
    except:
        return False

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Quantum Math Suite", page_icon="⚛️", layout="wide")

if 'logado' not in st.session_state:
    st.session_state.logado = False

# --- TELA DE LOGIN ---
if not st.session_state.logado:
    st.title("🔐 Acesso Restrito: Laboratório Quântico")
    col1, col2 = st.columns([1, 1])
    with col1:
        pin_input = st.text_input("Digite seu PIN de acesso:", type="password")
        if st.button("Desbloquear"):
            if validar_acesso(pin_input):
                st.session_state.logado = True
                st.rerun()
            else:
                st.error("Acesso negado. Verifique o PIN ou a configuração da chave_mestra.")
    st.stop()

# --- ÁREA LOGADA: O SUPER APP MATEMÁTICO ---
st.sidebar.title("⚛️ Math Suite v1.0")
menu = st.sidebar.radio("Navegação:", ["Quântica", "Álgebra Linear", "Cálculo & Funções", "Estatística"])

if st.sidebar.button("Encerrar Sessão"):
    st.session_state.logado = False
    st.rerun()

st.title(f"Módulo: {menu}")

# --- MÓDULO 1: QUÂNTICA ---
if menu == "Quântica":
    st.header("Cálculos de Estado e Densidade")
    st.latex(r"|\psi\rangle = \cos(\theta)|0\rangle + e^{i\phi}\sin(\theta)|1\rangle")
    
    theta = st.slider("Ângulo θ (rad)", 0.0, np.pi, np.pi/4)
    phi = st.slider("Ângulo de Fase φ (rad)", 0.0, 2*np.pi, 0.0)
    
    alpha = np.cos(theta)
    beta = np.exp(1j * phi) * np.sin(theta)
    
    state = np.array([[alpha], [beta]])
    rho = np.dot(state, state.conj().T)
    
    st.subheader("Matriz de Densidade ρ")
    st.write(rho)
    
    # Gráfico de Probabilidades
    probs = {"|0⟩": np.abs(alpha)**2, "|1⟩": np.abs(beta)**2}
    st.bar_chart(probs)

# --- MÓDULO 2: ÁLGEBRA LINEAR ---
elif menu == "Álgebra Linear":
    st.header("Processamento de Matrizes")
    dim = st.selectbox("Dimensão da Matriz:", [2, 3])
    
    st.write(f"Preencha a matriz {dim}x{dim}:")
    matriz_data = []
    for i in range(dim):
        cols = st.columns(dim)
        row = [cols[j].number_input(f"M[{i},{j}]", value=float(i==j)) for j in range(dim)]
        matriz_data.append(row)
    
    m = np.array(matriz_data)
    
    col_res1, col_res2 = st.columns(2)
    with col_res1:
        st.write("**Determinante:**", np.linalg.det(m))
        st.write("**Traço:**", np.trace(m))
    with col_res2:
        try:
            st.write("**Inversa:**")
            st.write(np.linalg.inv(m))
        except:
            st.warning("Matriz não inversível.")

# --- MÓDULO 3: CÁLCULO ---
elif menu == "Cálculo & Funções":
    st.header("Análise Gráfica")
    exp = st.text_input("Defina f(x) (ex: np.sin(x) * np.exp(-x/5))", "np.sin(x)")
    
    x = np.linspace(-10, 10, 500)
    try:
        y = eval(exp)
        st.line_chart(y)
    except Exception as e:
        st.error(f"Erro na expressão: {e}")

# --- MÓDULO 4: ESTATÍSTICA ---
elif menu == "Estatística":
    st.header("Distribuições e Dados")
    samples = st.number_input("Número de Amostras:", 100, 10000, 1000)
    data = np.random.normal(0, 1, samples)
    st.subheader("Distribuição Normal (Gaussiana)")
    st.line_chart(np.histogram(data, bins=50)[0])