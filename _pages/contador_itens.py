import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import re
import html

st.title("📦 Contador de Itens")

st.subheader("📋 Cole a lista de itens")

# ===============================
# 🔗 CONEXÃO COM PLANILHA
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
# 🔥 FUNÇÃO DE LIMPEZA
# ===============================
def limpar_texto(texto):
    texto = html.unescape(texto)  # &amp; → &
    texto = texto.lower()
    texto = texto.strip()
    texto = re.sub(r'\s+', ' ', texto)  # remove espaços duplicados
    texto = re.sub(r'[^\w\s]', '', texto)  # remove símbolos
    return texto

# ===============================
# 🔥 NORMALIZA PRODUTOS
# ===============================
if not df_produtos.empty:
    df_produtos.columns = df_produtos.columns.str.strip().str.lower()
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
# 📥 CAMPO DE TEXTO
# ===============================
texto = st.text_area(
    "Itens (um por linha)",
    key="lista_itens"
)

# ===============================
# 🔘 BOTÕES
# ===============================
col1, col2 = st.columns(2)

with col1:
    if st.button("🔍 Fazer contagem"):

        if texto.strip() == "":
            st.warning("Cole a lista primeiro")
            st.stop()

        # 🔥 lista digitada
        lista = texto.split("\n")
        lista = [limpar_texto(item) for item in lista if item.strip() != ""]

        # 🔥 contagem
        df_lista = pd.Series(lista).value_counts().reset_index()
        df_lista.columns = ["produto", "quantidade"]

        # ===============================
        # 🔗 FILTRAR APENAS PRODUTOS CADASTRADOS
        # ===============================
        df_final = df_lista.merge(
            df_produtos[["produto"]],
            on="produto",
            how="inner"
        )

        st.subheader("📊 Itens Encontrados no Cadastro")

        if df_final.empty:
            st.warning("Nenhum item da lista está cadastrado")
        else:
            st.dataframe(df_final, use_container_width=True)

with col2:
    if st.button("🗑️ Limpar lista"):
        st.session_state.limpar_lista = True
        st.rerun()
