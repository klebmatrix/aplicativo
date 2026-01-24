import streamlit as st
import os
import numpy as np
from cryptography.fernet import Fernet
from scipy import optimize

# --- SEGURANÇA ---
PIN_CRIPTOGRAFADO = "COLE_AQUI_SEU_TOKEN_GERADO"

def validar_acesso(pin_digitado):
    try:
        chave = os.environ.get('chave_mestra')
        if not chave: return False
        chave = chave.strip().replace("'", "").replace('"', "")
        if chave.startswith('b'): chave = chave[1:]
        f = Fernet(chave.encode())
        return pin_digitado == f.decrypt(PIN_CRIPTOGRAFADO.strip().encode()).decode()
    except: return False

# --- UI ---
st.set_page_config(page_title="Math Master Quantum", layout="wide")

if 'logado' not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    st.title("🔐 Acesso Restrito")
    pin_input = st.text_input("PIN:", type="password")
    if st.button("Entrar"):
        if validar_acesso(pin_input):
            st.session_state.logado = True
            st.rerun()
    st.stop()

# --- ÁREA LOGADA ---
st.sidebar.title("🛠️ Ferramentas")
menu = st.sidebar.radio("Escolha:", ["Raízes de Equações", "Sistemas Lineares", "Quântica & Matrizes"])

if menu == "Raízes de Equações":
    st.header("🔍 Encontrar Raízes (Zeros da Função)")
    st.write("Encontre onde $f(x) = 0$")
    
    formula = st.text_input("Defina f(x) (ex: x**2 - 4 ou np.sin(x))", "x**2 - 5")
    chute = st.number_input("Chute inicial (x0):", value=1.0)
    
    if st.button("Calcular Raiz"):
        try:
            # Transforma a string em uma função real
            func = lambda x: eval(formula)
            raiz = optimize.newton(func, chute)
            st.success(f"Raiz encontrada: **{raiz:.6f}**")
            
            # Plot do gráfico ao redor da raiz
            x_plot = np.linspace(raiz-5, raiz+5, 100)
            y_plot = [eval(formula.replace('x', f'({xi})')) for xi in x_plot]
            st.line_chart(y_plot)
        except Exception as e:
            st.error(f"Erro no cálculo: {e}")

elif menu == "Sistemas Lineares":
    st.header("📏 Resolutor de Sistemas Lineares")
    st.write("Resolve sistemas do tipo $Ax = B$")
    
    n = st.number_input("Número de incógnitas:", 2, 5, 3)
    
    st.write("Matriz A (Coeficientes):")
    A = []
    for i in range(n):
        cols = st.columns(n)
        row = [cols[j].number_input(f"A[{i},{j}]", value=1.0 if i==j else 0.0, key=f"A{i}{j}") for j in range(n)]
        A.append(row)
        
    st.write("Vetor B (Resultados):")
    B = []
    cols_b = st.columns(n)
    for i in range(n):
        B.append(cols_b[i].number_input(f"B[{i}]", value=1.0, key=f"B{i}"))
        
    if st.button("Resolver Sistema"):
        try:
            solucao = np.linalg.solve(np.array(A), np.array(B))
            st.subheader("Solução:")
            for i, sol in enumerate(solucao):
                st.write(f"**x_{i+1}** = {sol:.4f}")
        except np.linalg.LinAlgError:
            st.error("O sistema não tem solução única (Matriz Singular).")

elif menu == "Quântica & Matrizes":
    st.header("⚛️ Operadores Quânticos")
    # Exemplo de matriz de Pauli X
    pauli_x = np.array([[0, 1], [1, 0]])
    st.write("Matriz de Pauli X:")
    st.write(pauli_x)
    
    val, vec = np.linalg.eig(pauli_x)
    st.write("**Autovalores:**", val)