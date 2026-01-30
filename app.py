import streamlit as st
import random
import re
import os
from fpdf import FPDF

# 1. Configuração inicial (DEVE ser a primeira coisa)
st.set_page_config(page_title="Quantum Math", layout="wide")

# 2. Inicializar a memória do navegador (Session State)
if 'preview_questoes' not in st.session_state:
    st.session_state.preview_questoes = []

# 3. Sidebar
st.sidebar.title("Configurações")
layout_colunas = st.sidebar.selectbox("Colunas:", [1, 2, 3], index=1)

# 4. Gerador de Operações (A partir do 6)
st.title("🛠️ Gerador de Atividades")

c1, c2 = st.columns(2)

with c1:
    st.subheader("🔢 Operações Automáticas")
    num_ini = st.number_input("Iniciar na questão nº:", value=6)
    qtd = st.number_input("Quantidade de itens:", value=10)
    
    if st.button("🚀 Gerar Agora"):
        # Criando a lista de questões
        novas_questoes = [
            ".M1", 
            "t. ATIVIDADE DE MATEMÁTICA", 
            f"{num_ini}. Resolva as operações abaixo:"
        ]
        for _ in range(qtd):
            n1 = random.randint(10, 99)
            n2 = random.randint(10, 99)
            novas_questoes.append(f"{n1} + {n2} =")
        
        # SALVANDO NA MEMÓRIA
        st.session_state.preview_questoes = novas_questoes
        st.rerun() # Força o Streamlit a mostrar o preview

with c2:
    st.subheader("📄 Inserção Manual")
    txt_manual = st.text_area("Cole aqui (ex: .M1, t. Titulo, 6. Pergunta)")
    if st.button("📥 Adicionar Manual"):
        if txt_manual:
            st.session_state.preview_questoes = txt_manual.split('\n')
            st.rerun()

# 5. Exibição do Preview e Botão de PDF
if st.session_state.preview_questoes:
    st.divider()
    st.subheader("👁️ Preview")
    
    # Mostra na tela para conferir
    for linha in st.session_state.preview_questoes:
        st.write(linha)

    # Função do PDF ajustada para NÃO travar
    def gerar_pdf(lista):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        y = 20
        
        letras = "abcdefghijklmnopqrstuvwxyz"
        l_idx = 0
        largura_col = 190 / layout_colunas
        y_fixo = y

        for item in lista:
            item = item.strip()
            if not item: continue

            # Regra .M1 (M1 na esquerda e negrito)
            mod_match = re.match(r'^\.M(\d+)', item, re.IGNORECASE)
            
            if item.startswith("t."):
                pdf.set_font("Arial", 'B', 14)
                pdf.cell(190, 10, item[2:].strip(), ln=True, align='C')
                l_idx = 0
            elif mod_match:
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(190, 10, f"M{mod_match.group(1)}", ln=True, align='L')
                l_idx = 0
            elif re.match(r'^\d+\.', item):
                pdf.set_font("Arial", '', 12) # QUESTÃO NORMAL
                pdf.cell(190, 10, item, ln=True, align='L')
                l_idx = 0
            else:
                # Itens em colunas
                pdf.set_font("Arial", '', 12)
                col = l_idx % layout_colunas
                if col == 0 and l_idx > 0: pdf.ln(2)
                
                texto_item = f"{letras[l_idx % 26]}) {re.sub(r'^[.\s]+', '', item)}"
                pdf.cell(largura_col, 8, texto_item, align='L')
                l_idx += 1
        
        return pdf.output(dest='S').encode('latin-1')

    # Botão de Download
    pdf_final = gerar_pdf(st.session_state.preview_questoes)
    st.download_button("📥 Baixar Atividade", data=pdf_final, file_name="atividade.pdf")