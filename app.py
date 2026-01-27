import streamlit as st
from fpdf import FPDF
import os
import re

# Configuração da Página
st.set_page_config(page_title="Gerador de Atividades", layout="centered")

# --- LOGIN SEGURO (CONFORME SUAS DIRETRIZES) ---
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    st.title("🔐 Acesso ao Sistema")
    
    # Busca a senha nas variáveis de ambiente do Render (chave_mestra em lowercase)
    # Se não houver variável, o padrão é '123456'
    pin_correto = os.getenv("chave_mestra", "123456")
    
    senha = st.text_input("Digite seu PIN (6-8 dígitos):", type="password", max_chars=8)
    
    if st.button("Entrar"):
        if senha == pin_correto:
            st.session_state['autenticado'] = True
            st.rerun()
        else:
            st.error("PIN incorreto. Verifique as variáveis no Render.")

else:
    # --- INTERFACE DO GERADOR ---
    st.sidebar.title("Configurações")
    if st.sidebar.button("Sair"):
        st.session_state['autenticado'] = False
        st.rerun()

    st.header("📄 Gerador de Atividades Profissional")
    
    titulo_pdf = st.text_input("Título da Atividade:", "Complementação para o estudo da Matemática")
    conteudo = st.text_area("Conteúdo (Use . para colunas):", height=400)
    
    if st.button("Gerar PDF Agora"):
        if conteudo:
            pdf = FPDF()
            pdf.add_page()
            
            # 1. CABEÇALHO (185mm - Centralizado)
            if os.path.exists("cabecalho.png"):
                pdf.image("cabecalho.png", x=12.5, y=8, w=185) 
                pdf.set_y(48) # Espaço fixo para o título abaixo da imagem
            else:
                pdf.set_y(15)
            
            # 2. TÍTULO DA ATIVIDADE
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, txt=titulo_pdf, ln=True, align='C')
            pdf.ln(2)
            
            # 3. LÓGICA DE PROCESSAMENTO
            pdf.set_font("Arial", size=10)
            letras = "abcdefghijklmnopqrstuvwxyz"
            letra_idx = 0
            
            for linha in conteudo.split('\n'):
                txt = linha.strip()
                if not txt: continue
                
                # Identifica se a linha começa com pontos
                match_pontos = re.match(r'^(\.+)', txt)
                
                # SE FOR QUESTÃO (Começa com número: 1., 2º, etc)
                if re.match(r'^\d+', txt):
                    pdf.ln(4)
                    pdf.set_font("Arial", 'B', 11)
                    pdf.set_x(10) # Alinhado na margem sem recuo
                    pdf.multi_cell(0, 7, txt=txt)
                    pdf.set_font("Arial", size=10)
                    letra_idx = 0 # Reseta letras (a, b, c) para nova questão
                
                # SE FOR COLUNA (. até ......)
                elif match_pontos:
                    num_pontos = len(match_pontos.group(1))
                    item_limpo = txt[num_pontos:].strip()
                    prefixo = f"{letras[letra_idx % 26]}) "
                    
                    # Se for a partir do segundo ponto (..), sobe para alinhar
                    if num_pontos > 1:
                        pdf.set_y(pdf.get_y() - 8)
                    
                    # Define a posição X baseado no número de pontos (32mm por coluna)
                    col_x = 10 + (num_pontos - 1) * 32
                    pdf.set_x(col_x)
                    
                    pdf.cell(32, 8, txt=f"{prefixo}{item_limpo}", ln=True)
                    letra_idx += 1
                
                # SE FOR TEXTO NORMAL (Professor/Enunciado)
                else:
                    pdf.set_x(10) # Garante margem esquerda
                    pdf.multi_cell(0, 7, txt=txt)
            
            # SAÍDA DO ARQUIVO
            pdf_output = pdf.output(dest='S').encode('latin-1', 'replace')
            st.download_button("📥 Baixar Atividade PDF", data=pdf_output, file_name="atividade.pdf")
        else:
            st.warning("Por favor, digite o conteúdo da atividade.")

# --- LEMBRETE PARA O RENDER ---
# No painel do Render, vá em Settings -> Environment Variables e adicione:
# Key: chave_mestra
# Value: 123456 (ou seu PIN escolhido)