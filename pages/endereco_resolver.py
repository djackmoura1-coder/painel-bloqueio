import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import smtplib
from email.mime.text import MIMEText

# 🔒 LOGIN
if "logado" not in st.session_state or not st.session_state.logado:
    st.warning("🔒 Faça login")
    st.stop()

st.title("🔧 Resolver Atualização de Endereço")

# 🔗 CONEXÃO
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

credentials = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)

client = gspread.authorize(credentials)

sheet = client.open_by_key(
    "1IGKJfifqmCdyptPT7INeSjjkW9VnfbQhc4yjKKfwyao"
).worksheet("enderecos")

# 🔥 LEITURA SEGURA
dados = sheet.get_all_values()

if len(dados) < 2:
    st.warning("Nenhum dado encontrado.")
    st.stop()

df = pd.DataFrame(dados[1:], columns=dados[0])

# 🔥 NORMALIZAÇÃO
df.columns = (
    pd.Series(df.columns)
    .str.strip()
    .str.lower()
    .str.replace("á", "a")
    .str.replace("ã", "a")
    .str.replace("ç", "c")
    .str.replace("é", "e")
    .str.replace("í", "i")
    .str.replace("ó", "o")
    .str.replace("ú", "u")
)

# 🔎 BUSCA
st.subheader("🔎 Buscar rastreio")

busca = st.text_input("Digite o código de rastreio")

if busca:
    resultado_busca = df[df["rastreio"].astype(str).str.contains(busca)]

    if not resultado_busca.empty:
        st.dataframe(resultado_busca, use_container_width=True)
    else:
        st.warning("Nenhum resultado encontrado")

st.divider()

# 🔧 RESOLVER
st.subheader("Resolver ocorrência")

pendentes = df[df["status"] == "Pendente"]

if not pendentes.empty:

    rastreio = st.selectbox(
        "Selecionar rastreio",
        pendentes["rastreio"]
    )

    acao = st.radio(
        "Resultado",
        ["Atualizado", "Não atualizado"]
    )

    if st.button("Finalizar"):

        df.loc[df["rastreio"] == rastreio, "status"] = "Finalizado"
        df.loc[df["rastreio"] == rastreio, "resultado"] = acao

        # 🔥 PEGA EMAIL
        email_cliente = df.loc[df["rastreio"] == rastreio, "email"].values[0]

        # 🔄 ATUALIZA PLANILHA
        sheet.update([df.columns.tolist()] + df.values.tolist())

        # 📧 ENVIO DE EMAIL
        if email_cliente:

            mensagem = f"""
Olá,

A solicitação de atualização de endereço do pedido {rastreio} foi analisada.

Resultado: {acao}

Sistema de Atualização de Endereço
"""

            msg = MIMEText(mensagem)
            msg["Subject"] = "Atualização de endereço"
            msg["From"] = "djackmoura1@gmail.com"
            msg["To"] = email_cliente

            try:
                servidor = smtplib.SMTP("smtp.gmail.com", 587)
                servidor.starttls()
                servidor.login("djackmoura1@gmail.com", "xssw hyhl tjao eeyj")

                servidor.sendmail(
                    "djackmoura1@gmail.com",
                    email_cliente,
                    msg.as_string()
                )

                servidor.quit()

                st.success("✅ Atualização concluída e email enviado!")

            except:
                st.warning("Atualizado, mas falha ao enviar email")

        else:
            st.success("Atualização concluída (sem email cadastrado)")

        st.rerun()

else:
    st.info("Sem solicitações pendentes")

# 📊 HISTÓRICO
st.subheader("📊 Histórico")

st.dataframe(df, use_container_width=True)
