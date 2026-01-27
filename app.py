# --- MÓDULO: GERADOR DE ATIVIDADES ---
    elif menu == "Gerador de Atividades":
        st.header("📄 Gerador de PDF Personalizado")
        
        titulo_pdf = st.text_input("Título:", "Atividade de Matemática")
        conteudo = st.text_area("Digite os itens (cada linha será uma letra):", height=200)
        
        if st.button("Gerar PDF"):
            if conteudo:
                pdf = FPDF()
                pdf.add_page()
                
                # 1. IMAGEM NO TOPO (CABEÇALHO)
                # Certifique-se de que o arquivo 'cabecalho.png' existe no seu GitHub
                if os.path.exists("cabecalho.png"):
                    pdf.image("cabecalho.png", x=10, y=8, w=190)
                    pdf.ln(40) # Espaço para não escrever em cima da imagem
                
                # 2. TÍTULO
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(200, 10, txt=titulo_pdf, ln=True, align='C')
                pdf.ln(5)
                
                # 3. CONTEÚDO COM LETRAS (a, b, c...)
                pdf.set_font("Arial", size=12)
                letras = "abcdefghijklmnopqrstuvwxyz"
                
                for i, linha in enumerate(conteudo.split('\n')):
                    if linha.strip():
                        # Usa o índice para pegar a letra correspondente
                        prefixo = f"{letras[i % 26]}) "
                        pdf.multi_cell(0, 10, txt=f"{prefixo}{linha.strip()}")
                
                pdf_bytes = pdf.output(dest='S').encode('latin-1', 'replace')
                st.download_button("📥 Baixar PDF Atualizado", data=pdf_bytes, file_name="atividade.pdf", mime="application/pdf")
            else:
                st.warning("Digite o conteúdo para as alíneas.")