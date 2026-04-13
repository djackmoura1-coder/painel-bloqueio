import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import re
import html

st.title("📦 Contador de Itens")

st.subheader("📋 Cole a lista de itens")

# ===============================
# 🔗 CONEXÃO
# ===============================
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

credentials = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)

client = gspread.authorize(credentials)
spreadsheet = client.open_by_key("1IGKJfifqmCdyptPT7INeSjjkW9VnfbQhc4yjKKfwyao")

sheet_produtos = spreadsheet.worksheet("produtos")
df_produtos = pd.DataFrame(sheet_produtos.get_all_records())

# ===============================
# 🔥 LIMPEZA
# ===============================
def limpar_texto(texto):
    texto = html.unescape(texto)
    texto = texto.lower().strip()
    texto = re.sub(r'\s+', ' ', texto)
    texto = re.sub(r'[^\w\s]', '', texto)
    return texto

# ===============================
# 🔥 NORMALIZA PRODUTOS
# ===============================
if not df_produtos.empty:
    df_produtos.columns = df_produtos.columns.str.strip().str.lower()
    df_produtos["produto_original"] = df_produtos["produto"]
    df_produtos["produto"] = df_produtos["produto"].astype(str).apply(limpar_texto)

# ===============================
# 🔥 CONTROLE DE LIMPEZA
# ===============================
if "limpar_lista" not in st.session_state:
    st.session_state.limpar_lista = False

if st.session_state.limpar_lista:
    st.session_state.lista_itens = ""
    st.session_state.limpar_lista = False

# ===============================
# 📥 INPUT
# ===============================
texto = st.text_area("Itens (um por linha)", key="lista_itens")

# ===============================
# 🔘 BOTÕES
# ===============================
col1, col2 = st.columns(2)

with col1:
    if st.button("🔍 Fazer contagem"):

        if texto.strip() == "":
            st.warning("Cole a lista primeiro")
            st.stop()

        lista = texto.split("\n")
        lista = [limpar_texto(item) for item in lista if item.strip() != ""]

        df_lista = pd.Series(lista).value_counts().reset_index()
        df_lista.columns = ["produto_digitado", "quantidade"]

        resultados = []

        for _, row in df_lista.iterrows():

            digitado = row["produto_digitado"]

            encontrados = df_produtos[
                df_produtos["produto"].str.startswith(digitado)
            ]

            for _, prod in encontrados.iterrows():
                resultados.append({
                    "produto": prod["produto_original"],
                    "produto_limpo": prod["produto"],
                    "quantidade": row["quantidade"]
                })

        df_final = pd.DataFrame(resultados)

        if not df_final.empty:
            df_final = df_final.groupby(["produto", "produto_limpo"])["quantidade"].sum().reset_index()

        st.session_state.resultado_contagem = df_final

with col2:
    if st.button("🗑️ Limpar lista"):
        st.session_state.limpar_lista = True
        st.rerun()

# ===============================
# 📊 EXIBIR RESULTADO
# ===============================
if "resultado_contagem" in st.session_state:

    df_final = st.session_state.resultado_contagem

    st.subheader("📊 Produtos Encontrados")

    if df_final.empty:
        st.warning("Nenhum produto encontrado")
    else:
        st.dataframe(df_final[["produto", "quantidade"]], use_container_width=True)

        # ===============================
        # 🔥 BOTÃO DE BAIXA
        # ===============================
        if st.button("📉 Dar baixa no estoque"):

            for _, row in df_final.iterrows():

                produto_limpo = row["produto_limpo"]
                qtd_baixa = int(row["quantidade"])

                idx = df_produtos[df_produtos["produto"] == produto_limpo].index

                if not idx.empty:
                    idx = idx[0]

                    estoque_atual = int(df_produtos.loc[idx, "quantidade_inicial"])
                    novo_estoque = estoque_atual - qtd_baixa

                    df_produtos.loc[idx, "quantidade_inicial"] = novo_estoque

            # 🔥 ATUALIZA PLANILHA
            sheet_produtos.update([df_produtos.columns.tolist()] + df_produtos.values.tolist())

            st.success("✅ Baixa realizada com sucesso!")

            # limpa resultado
            del st.session_state.resultado_contagem

            st.rerun()
