import streamlit as st
import os
import numpy as np
from cryptography.fernet import Fernet
from scipy import optimize

# --- 1. CONFIGURAÇÃO DE SEGURANÇA ---
# ATENÇÃO: Substitua o token abaixo pelo que você gerou agora no terminal
PIN_CRIPTOGRAFADO = "gAAAAABpdQTrFt-9rDWi0dBTMd0lhm2ESaLs2D0Zv13A5MyWpO6mIIKEQ5AewuZ3v21w-_Msp96ZxJuUW0ov1jnTe5ePrc-vTQ=="

def validar_acesso(pin_digitado):
    try:
        # Busca a variável 'chave_mestra' em minúsculo
        chave = os.environ.get('chave_mestra')
        if not chave:
            st.error("Erro: 'chave_mestra' não configurada no Render.")
            return False
        
        # Limpeza para evitar erros de cópia (remove b', aspas e espaços)
        chave = chave.strip().replace("'", "").replace('"', "")
        if chave.startswith('b'): chave = chave[1:]
            
        f = Fernet(chave.encode())
        pin_real = f.decrypt(PIN_CRIPTOGRAFADO.strip().encode()).decode()
        return pin_digitado == pin_real
    except Exception as e:
        st.error(f"Erro técnico de sincronia: {e}")
        return False

# --- 2. CONFIGURAÇÃO DA INTERFACE ---
st.set_page_config(page_title="Quantum Math Station", layout="wide", page_icon="⚛️")

if 'logado' not in st.session_state:
    st.session_state.logado = False

# --- 3. FLUXO DE ACESSO ---
if not st.session_state.logado:
    st.title("🔐 Laboratório de Matemática Avançada")
    st.info("Sistema protegido por criptografia quântica.")
    
    pin_input = st.text_input("Digite seu PIN de acesso:", type="password")
    if st.button("Desbloquear Sistema"):
        if validar_acesso(pin_input):
            st.session_state.logado = True
            st.rerun()
        else:
            st.warning("PIN incorreto. Verifique se a 'chave_mestra' no Render condiz com este código.")
    st.stop()

# --- 4. ÁREA LOGADA (PAINEL MATEMÁTICO) ---
st.sidebar.title("⚛️ Menu Científico")
menu = st.sidebar.radio("Selecione o Módulo:", 
    ["Geometria (Área/Vol)", "Sistemas Lineares", "Raízes de Equações", "Física Quântica"])

if st.sidebar.button("Logoff"):
    st.session_state.logado = False
    st.rerun()

# --- MÓDULO: GEOMETRIA ---
if menu == "Geometria (Área/Vol)":
    st.header("📐 Geometria Analítica e Espacial")
    figura = st.selectbox("Figura Geométrica:", ["Círculo/Esfera", "Cilindro", "Cubo", "Pirâmide"])
    
    c1, c2 = st.columns(2)
    if figura == "Círculo/Esfera":
        r = c1.number_input("Raio (r):", min_value=0.0, value=1.0)
        c2.metric("Área (Círculo)", f"{np.pi * r**2:.4f}")
        c2.metric("Volume (Esfera)", f"{(4/3) * np.pi * r**3:.4f}")
        st.latex(r"V = \frac{4}{3} \pi r^3")

    elif figura == "Cilindro":
        r = c1.number_input("Raio da Base (r):", min_value=0.0, value=1.0)
        h = c1.number_input("Altura (h):", min_value=0.0, value=1.0)
        c2.metric("Volume", f"{np.pi * (r**2) * h:.4f}")
        st.latex(r"V = \pi r^2 h")

    elif figura == "Cubo":
        l = c1.number_input("Lado (l):", min_value=0.0, value=1.0)
        c2.metric("Volume", f"{l**3:.4f}")
        st.latex(r"V = l^3")

# --- MÓDULO: SISTEMAS LINEARES ---
elif menu == "Sistemas Lineares":
    st.header("📏 Resolutor de Sistemas (Ax = B)")
    n = st.slider("Número de Variáveis:", 2, 4, 2)
    st.write("Insira os coeficientes da Matriz A e os resultados de B:")
    
    matriz_A = []
    lista_B = []
    for i in range(n):
        cols = st.columns(n + 1)
        linha = [cols[j].number_input(f"A{i}{j}", value=1.0 if i==j else 0.0) for j in range(n)]
        matriz_A.append(linha)
        lista_B.append(cols[n].number_input(f"B{i}", value=1.0))
        
    if st.button("Calcular Solução"):
        try:
            sol = np.linalg.solve(np.array(matriz_A), np.array(lista_B))
            st.success(f"Resultados: {sol}")
        except:
            st.error("O sistema não possui solução única.")

# --- MÓDULO: RAÍZES ---
elif menu == "Raízes de Equações":
    st.header("🔍 Cálculo de Raízes (Método de Newton)")
    func_str = st.text_input("Equação f(x):", "x**2 - 2")
    chute = st.number_input("Ponto de partida (chute):", value=1.0)
    
    if st.button("Achar Raiz"):
        try:
            f = lambda x: eval(func_str)
            raiz = optimize.newton(f, chute)
            st.success(f"Raiz aproximada: {raiz:.6f}")
            # Gráfico simples
            x_vals = np.linspace(raiz-5, raiz+5, 100)
            y_vals = [eval(func_str.replace('x', f'({val})')) for val in x_vals]
            st.line_chart(y_vals)
        except Exception as e:
            st.error(f"Erro: {e}")

# --- MÓDULO: QUÂNTICA ---
elif menu == "Física Quântica":
    st.header("⚛️ Operadores e Estados")
    st.latex(r"\sigma_x = \begin{pmatrix} 0 & 1 \\ 1 & 0 \end{pmatrix}")
    pauli_x = np.array([[0, 1], [1, 0]])
    st.write("Matriz de Pauli X representação NumPy:")
    st.write(pauli_x)
    
    if st.button("Calcular Autovalores"):
        eigen = np.linalg.eigvals(pauli_x)
        st.write(f"Autovalores: {eigen}")