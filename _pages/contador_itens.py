import streamlit as st
import pandas as pd

st.title("📦 Contador de Itens")

st.subheader("📋 Cole a lista de itens")

# 🔥 CONTROLE DO TEXTO
if "lista_itens" not in st.session_state:
    st.session_state.lista_itens = ""

# 🔥 CAMPO DE TEXTO
texto = st.text_area(
    "Itens (um por linha)",
    key="lista_itens"
)

# 🔥 BOTÕES
col1, col2 = st.columns(2)

with col1:
    if st.button("🔍 Fazer contagem"):

        if texto.strip() == "":
            st.warning("Cole a lista primeiro")
            st.stop()

        lista = texto.split("\n")
        lista = [item.strip().lower() for item in lista if item.strip() != ""]

        df = pd.Series(lista).value_counts().reset_index()
        df.columns = ["produto", "quantidade"]

        st.subheader("📊 Resultado")
        st.dataframe(df, use_container_width=True)

with col2:
    if st.button("🗑️ Limpar lista"):

        # 🔥 limpa tudo
        st.session_state.lista_itens = ""

        # 🔥 atualiza tela
        st.rerun()
