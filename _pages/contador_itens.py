import streamlit as st
import pandas as pd

st.title("📦 Contador de Itens")

st.subheader("📋 Cole a lista de itens")

texto = st.text_area("Itens (um por linha)")

# 🔥 BOTÃO DE CONTAGEM
if st.button("🔍 Fazer contagem"):

    if texto.strip() == "":
        st.warning("Cole a lista primeiro")
        st.stop()

    # 🔥 transforma em lista
    lista = texto.split("\n")

    # 🔥 limpa dados
    lista = [item.strip().lower() for item in lista if item.strip() != ""]

    # 🔥 conta itens
    df = pd.Series(lista).value_counts().reset_index()
    df.columns = ["produto", "quantidade"]

    st.subheader("📊 Resultado")

    st.dataframe(df, use_container_width=True)
