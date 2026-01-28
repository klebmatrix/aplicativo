# --- GERADOR 3: COLEGIAL (REVISADO E TESTADO) ---
elif menu == "GERADOR: Colegial (Frações/Funções)":
    st.header("📚 Temas Colegiais")
    
    # 1. Opções de Escolha
    col1, col2, col3 = st.columns(3)
    f_frac = col1.checkbox("Frações", value=True)
    f_pot = col2.checkbox("Potência e Raiz")
    f_fun = col3.checkbox("Funções (Afim/Quadrática)")
    
    qtd = st.slider("Quantidade de questões:", 4, 20, 8)
    
    temas = []
    if f_frac: temas.append("FRA")
    if f_pot: temas.append("POT")
    if f_fun: temas.append("FUN")
    
    if not temas:
        st.warning("Selecione pelo menos um tema para visualizar.")
    else:
        st.subheader("👀 Visualização Prévia")
        questoes = []
        for i in range(qtd):
            t = random.choice(temas)
            if t == "FRA":
                n1, n2 = random.randint(1, 9), random.randint(2, 5)
                txt = f"Resolva a operação com fração: {n1}/{n2} + {random.randint(1, 5)}/{n2} ="
            elif t == "POT":
                base = random.randint(2, 12)
                txt = f"Calcule o valor de: {base}² + √{random.choice([16, 25, 36, 49, 64, 81, 100])} ="
            else:
                a, b = random.randint(2, 5), random.randint(1, 10)
                txt = f"Dada a função f(x) = {a}x + {b}, determine o valor de f({random.randint(1, 6)})"
            
            questoes.append(txt)
            st.write(f"**{chr(97+i%26)})** {txt}")
        
        # 3. Botão de Impressão
        pdf_bytes = gerar_arquivo_pdf(questoes, "Atividade Colegial")
        st.download_button("📥 Imprimir em PDF (Colegial)", pdf_bytes, "colegial.pdf")

# --- GERADOR 4: ÁLGEBRA LINEAR (REVISADO E TESTADO) ---
elif menu == "GERADOR: Álgebra Linear":
    st.header("⚖️ Sistemas e Matrizes")
    
    # 1. Opções de Escolha
    c1, c2 = st.columns(2)
    m_det = c1.checkbox("Determinantes (Matriz 2x2)", value=True)
    m_sis = c2.checkbox("Sistemas Lineares (2 incógnitas)")
    
    qtd_a = st.number_input("Número de questões:", 2, 10, 4)
    
    opcoes_alg = []
    if m_det: opcoes_alg.append("DET")
    if m_sis: opcoes_alg.append("SIS")
    
    if not opcoes_alg:
        st.warning("Selecione uma opção para gerar as questões.")
    else:
        st.subheader("👀 Visualização Prévia")
        questoes_alg = []
        for i in range(qtd_a):
            tipo = random.choice(opcoes_alg)
            if tipo == "DET":
                a, b, c, d = random.randint(1, 5), random.randint(0, 3), random.randint(0, 3), random.randint(1, 5)
                txt = f"Calcule o determinante da matriz: | {a}  {b} | / | {c}  {d} |"
            else:
                res1, res2 = random.randint(5, 15), random.randint(1, 5)
                txt = f"Resolva o sistema linear: {{ x + y = {res1} ; x - y = {res2} }}"
            
            questoes_alg.append(txt)
            st.write(f"**{chr(97+i%26)})** {txt}")
            
        # 3. Botão de Impressão
        pdf_bytes_alg = gerar_arquivo_pdf(questoes_alg, "Atividade de Álgebra Linear")
        st.download_button("📥 Imprimir em PDF (Álgebra)", pdf_bytes_alg, "algebra_linear.pdf")