# --- GERADOR 5: MANUAL (REVISADO COM PREVIEW EM TEMPO REAL) ---
elif menu == "GERADOR: Manual (Colunas)":
    st.header("📄 Gerador Manual (Sistema de Colunas)")
    
    st.info("""
    **Instruções de Uso:**
    1. Se a linha começar com **Número** (ex: 1.), a próxima linha começa com **letra a)**.
    2. Use **pontos (.)** no início da linha para criar colunas:
       - `. item` -> Coluna 1
       - `.. item` -> Coluna 2
       - `... item` -> Coluna 3
    """)

    titulo_m = st.text_input("Título da Atividade:", "Atividade de Matemática")
    texto_m = st.text_area("Digite o conteúdo abaixo:", height=300, 
                           placeholder="1. Calcule as operações:\n. 2+2\n.. 5+5\n... 10+10")

    if texto_m:
        st.subheader("👀 Visualização Prévia (Como ficará no PDF)")
        st.markdown("---")
        
        # Lógica de visualização para o professor conferir antes de gerar
        linhas = texto_m.split('\n')
        letra_idx = 0
        letras = "abcdefghijklmnopqrstuvwxyz"
        
        for linha in linhas:
            t = linha.strip()
            if not t: continue
            
            # Verifica se começa com número para resetar letras
            if re.match(r'^\d+', t):
                st.markdown(f"### {t}")
                letra_idx = 0
            # Verifica se é coluna (.)
            elif t.startswith('.'):
                match = re.match(r'^(\.+)', t)
                num_pontos = len(match.group(1))
                conteudo = t[num_pontos:].strip()
                st.write(f"&nbsp;&nbsp;&nbsp;&nbsp;**{letras[letra_idx%26]})** {conteudo}")
                letra_idx += 1
            else:
                st.write(t)
        
        st.markdown("---")
        
        # BOTÃO DE GERAR PDF
        if st.button("📥 Gerar e Baixar PDF Manual"):
            pdf = FPDF()
            pdf.add_page()
            
            # Cabeçalho (Imagem)
            if os.path.exists("cabecalho.png"):
                pdf.image("cabecalho.png", x=12.5, y=8, w=185)
                pdf.set_y(46)
            else:
                pdf.set_y(15)
            
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(0, 10, titulo_m, ln=True, align='C')
            pdf.ln(5)
            
            pdf.set_font("Arial", size=10)
            letra_pdf_idx = 0
            
            for linha in linhas:
                t = linha.strip()
                if not t: continue
                
                match = re.match(r'^(\.+)', t)
                pts = len(match.group(1)) if match else 0
                
                # Regra: Começou com número, reseta letra e bota negrito
                if re.match(r'^\d+', t):
                    pdf.ln(4)
                    pdf.set_font("Arial", 'B', 11)
                    pdf.multi_cell(0, 8, t)
                    pdf.set_font("Arial", size=10)
                    letra_pdf_idx = 0
                
                # Regra: Colunas com pontos
                elif pts > 0:
                    item_texto = t[pts:].strip()
                    # Se for a partir da 2ª coluna, sobe a linha para alinhar
                    if pts > 1:
                        pdf.set_y(pdf.get_y() - 8)
                    
                    # Posicionamento X baseado nos pontos (32mm de largura por coluna)
                    pdf.set_x(10 + (pts-1)*32)
                    pdf.cell(32, 8, f"{letras[letra_pdf_idx%26]}) {item_texto}", ln=True)
                    letra_pdf_idx += 1
                
                # Texto normal
                else:
                    pdf.multi_cell(0, 8, t)
            
            pdf_output = pdf.output(dest='S').encode('latin-1', 'replace')
            st.download_button("Clique aqui para Baixar", pdf_output, "atividade_manual.pdf")