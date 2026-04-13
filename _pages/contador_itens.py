import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

st.title("📦 Contador de Itens (SKU)")

st.subheader("📋 Cole os SKUs (um por linha)")

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
sheet_log = spreadsheet.worksheet("movimentacoes")

# ===============================
# 📊 DADOS
# ===============================
df_produtos = pd.DataFrame(sheet_produtos.get_all_records())

if df_produtos.empty:
    st.warning("Nenhum produto cadastrado")
    st.stop()

# 🔥 NORMALIZA
df_produtos.columns = df_produtos.columns.str.strip().str.lower()

# ===============================
# 🔥 CONTROLE LIMPEZA
# ===============================
if "limpar_lista" not in st.session_state:
    st.session_state.limpar_lista = False

if st.session_state.limpar_lista:
    st.session_state.lista_itens = ""
    st.session_state.limpar_lista = False

# ===============================
# 📥 INPUT
# ===============================
texto = st.text_area("SKUs", key="lista_itens")

col1, col2 = st.columns(2)

# ===============================
# 🔍 CONTAGEM
# ===============================
with col1:
    if st.button("🔍 Fazer contagem"):

        if texto.strip() == "":
            st.warning("Cole os SKUs")
            st.stop()

        lista = texto.split("\n")
        lista = [item.strip() for item in lista if item.strip() != ""]

        df_lista = pd.Series(lista).value_counts().reset_index()
        df_lista.columns = ["sku", "quantidade"]

        # 🔗 CRUZAR COM PRODUTOS
        df_final = df_lista.merge(
            df_produtos,
            on="sku",
            how="inner"
        )

        if df_final.empty:
            st.warning("Nenhum SKU encontrado")
        else:
            st.session_state.resultado = df_final

# ===============================
# 🗑️ LIMPAR
# ===============================
with col2:
    if st.button("🗑️ Limpar lista"):
        st.session_state.limpar_lista = True
        st.rerun()

# ===============================
# 📊 RESULTADO
# ===============================
if "resultado" in st.session_state:

    df_final = st.session_state.resultado

    st.subheader("📊 Itens encontrados")

    st.dataframe(
        df_final[["sku", "produto", "quantidade"]],
        use_container_width=True
    )

    # ===============================
    # 📉 BAIXA
    # ===============================
    if st.button("📉 Dar baixa no estoque"):

        for _, row in df_final.iterrows():

            sku = row["sku"]
            qtd_baixa = int(row["quantidade"])

            idx = df_produtos[df_produtos["sku"] == sku].index

            if not idx.empty:
                idx = idx[0]

                estoque_atual = int(df_produtos.loc[idx, "quantidade_inicial"])
                novo_estoque = estoque_atual - qtd_baixa

                df_produtos.loc[idx, "quantidade_inicial"] = novo_estoque

                # 🔥 LOG
                sheet_log.append_row([
                    str(datetime.now()),
                    st.session_state.get("usuario"),
                    sku,
                    "Baixa",
                    qtd_baixa,
                    novo_estoque
                ])

        # 🔥 ATUALIZA PLANILHA
        sheet_produtos.update([df_produtos.columns.tolist()] + df_produtos.values.tolist())

        st.success("✅ Baixa realizada com sucesso!")

        del st.session_state.resultado
        st.rerun()
