# --- 6. VISUALIZAÇÃO UNIFICADA (CARDS NA TELA) ---
if st.session_state.preview_questoes and st.session_state.sub_menu in ["op", "eq", "col", "alg", "man"]:
    st.divider()
    if os.path.exists("cabecalho.png"): 
        st.image("cabecalho.png", use_container_width=True)
    
    letras = "abcdefghijklmnopqrstuvwxyz"
    l_idx = 0
    
    for q in st.session_state.preview_questoes:
        line = q.strip()
        if not line: continue
        
        # Títulos
        if line.lower().startswith("t."):
            st.markdown(f"<h1 style='text-align: center; color: #007bff; border-bottom: 2px solid #007bff;'>{line[2:].strip()}</h1>", unsafe_allow_html=True)
        
        # Seções Numéricas (Reseta contagem)
        elif re.match(r'^\d+', line):
            st.markdown(f"### {line}")
            l_idx = 0
        
        # Modo M e Itens Comuns em Colunas
        else:
            # Lógica para alternar entre as colunas do Streamlit
            if l_idx % 2 == 0:
                cv1, cv2 = st.columns(2)
                target_col = cv1
            else:
                target_col = cv2
            
            with target_col:
                with st.container(border=True):
                    if line.startswith("-M"):
                        # Exibe apenas M1-, M2- etc (sem a letra a, b na frente)
                        st.write(f"**{line[1:].strip()}**")
                    else:
                        # Exibe com letra automática
                        st.write(f"**{letras[l_idx%26]})** {line}")
            l_idx += 1
# --- 7. EXPORTAÇÃO PDF A4 (VERSÃO FINAL COM MODO M) ---
st.markdown("---")
st.subheader("📥 Exportar Atividade Finalizada")

def gerar_pdf(com_cabecalho):
    # Definimos as letras dentro da função para evitar NameError
    letras_pdf = "abcdefghijklmnopqrstuvwxyz"
    
    # Garantimos que buscamos a lista de questões atualizada
    questoes_lista = st.session_state.get('preview_questoes', [])
    
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_margins(15, 15, 15)
    
    # Altura inicial dinâmica
    if com_cabecalho and os.path.exists("cabecalho.png"):
        pdf.image("cabecalho.png", x=12.5, y=10, w=185)
        y_at = 55
    else:
        y_at = 20

    l_pdf_idx = 0
    y_base = y_at
    
    for q in questoes_lista:
        line = q.strip()
        if not line: continue
        
        pdf.set_font("Arial", size=11)
        
        # 1. Títulos no PDF
        if line.lower().startswith("t."):
            pdf.set_font("Arial", 'B', 16)
            pdf.set_y(y_at + 5)
            pdf.cell(0, 12, clean_txt(line[2:]), ln=True, align='C')
            y_at = pdf.get_y() + 5
        
        # 2. Seções Numéricas no PDF
        elif re.match(r'^\d+', line):
            pdf.set_y(y_at + 5)
            pdf.set_font("Arial", 'B', 12)
            pdf.multi_cell(0, 8, clean_txt(line))
            y_at = pdf.get_y()
            l_pdf_idx = 0
        
        # 3. Itens (Modo M ou Letras Automáticas)
        else:
            # Lógica Modo M vs Letras
            if line.startswith("-M"):
                txt_final = clean_txt(line[1:]) # Tira o "-"
            else:
                txt_final = f"{letras_pdf[l_pdf_idx%26]}) {clean_txt(line)}"
            
            # Posicionamento em Duas Colunas
            if l_pdf_idx % 2 == 0:
                y_base = y_at
                pdf.set_xy(15, y_base + 2)
                pdf.multi_cell(90, 8, txt_final)
                y_prox = pdf.get_y()
            else:
                pdf.set_xy(110, y_base + 2)
                pdf.multi_cell(85, 8, txt_final)
                y_at = max(y_prox, pdf.get_y())
            
            l_pdf_idx += 1
    
    # Retorno seguro em bytes para o Streamlit
    return pdf.output(dest='S').encode('latin-1')

# Exibição dos botões lado a lado
cp1, cp2 = st.columns(2)
with cp1:
    if st.button("📄 PDF COM Cabeçalho", use_container_width=True):
        try:
            data_pdf = gerar_pdf(True)
            st.download_button("✅ Baixar Com Cabeçalho", data_pdf, "atividade_cabecalho.pdf", "application/pdf")
        except Exception as e:
            st.error(f"Erro ao gerar: {e}")

with cp2:
    if st.button("📄 PDF SEM Cabeçalho", use_container_width=True):
        try:
            data_pdf = gerar_pdf(False)
            st.download_button("✅ Baixar Sem Cabeçalho", data_pdf, "atividade_simples.pdf", "application/pdf")
        except Exception as e:
            st.error(f"Erro ao gerar: {e}")