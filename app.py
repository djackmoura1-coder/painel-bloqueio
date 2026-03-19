import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(
    page_title="Sistema de Bloqueio",
    layout="wide"
)

# 🔗 CONEXÃO GOOGLE
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

credentials = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)

client = gspread.authorize(credentials)

# PLANILHAS
sheet_users = client.open_by_key(
    "1IGKJfifqmCdyptPT7INeSjjkW9VnfbQhc4yjKKfwyao"
).worksheet("usuarios")

sheet_solic = client.open_by_key(
    "1IGKJfifqmCdyptPT7INeSjjkW9VnfbQhc4yjKKfwyao"
).worksheet("solicitacoes_usuarios")

# 📊 USUÁRIOS
df_users = pd.DataFrame(sheet_users.get_all_records())

if not df_users.empty:
    df_users.columns = df_users.columns.str.strip().str.lower()
    df_users["usuario"] = df_users["usuario"].astype(str)
    df_users["senha"] = df_users["senha"].astype(str)

# 📊 SOLICITAÇÕES
df_solic = pd.DataFrame(sheet_solic.get_all_records())

if not df_solic.empty:
    df_solic.columns = df_solic.columns.str.strip().str.lower()
    df_solic = df_solic.fillna("")

# SESSION
if "logado" not in st.session_state:
    st.session_state.logado = False

# 🔐 LOGIN + CADASTRO
if not st.session_state.logado:

    st.title("🔐 Login do Sistema")

    col1, col2 = st.columns(2)

    # 🔑 LOGIN
    with col1:
        st.subheader("Entrar")

        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")

        if st.button("Entrar"):

            user_data = df_users[df_users["usuario"] == usuario]

            if not user_data.empty:

                user_data = user_data.iloc[0]

                if str(user_data["senha"]) == str(senha):

                    st.session_state.logado = True
                    st.session_state.usuario = usuario
                    st.session_state.perfil = user_data["perfil"]

                    st.rerun()

                else:
                    st.error("Senha incorreta")

            else:
                st.error("Usuário não encontrado")

    # 📝 CADASTRO
    with col2:
        st.subheader("Solicitar cadastro")

        novo_usuario = st.text_input("Novo usuário")
        nova_senha = st.text_input("Nova senha", type="password")

        if st.button("Solicitar cadastro"):

            if novo_usuario.strip() == "" or nova_senha.strip() == "":
                st.warning("Preencha todos os campos")

            elif not df_solic.empty and novo_usuario in df_solic["usuario"].values:
                st.warning("Já existe uma solicitação para esse usuário")

            else:

                sheet_solic.append_row([
                    str(novo_usuario),
                    str(nova_senha),
                    "operador",
                    "Pendente"
                ])

                st.success("Solicitação enviada para aprovação!")
                st.rerun()

# 🟢 SISTEMA
else:

    st.sidebar.success(f"👤 {st.session_state.usuario}")

    if st.sidebar.button("Sair"):
        st.session_state.logado = False
        st.rerun()

    st.title("📦 Sistema Operacional de Bloqueio")

    st.markdown("""
    Use o menu lateral:

    📌 Solicitar  
    🔧 Resolver  
    """)

    # 🔥 APROVAÇÃO (SÓ ADMIN)
    if st.session_state.perfil == "admin":

        st.subheader("👤 Aprovação de usuários")

        pendentes = df_solic[df_solic["status"] == "Pendente"]

        if not pendentes.empty:

            usuario_aprovar = st.selectbox(
                "Usuários pendentes",
                pendentes["usuario"]
            )

            if st.button("Aprovar usuário"):

                dados = pendentes[pendentes["usuario"] == usuario_aprovar].iloc[0]

                # ADICIONA USUÁRIO
                sheet_users.append_row([
                    str(dados["usuario"]),
                    str(dados["senha"]),
                    str(dados["perfil"])
                ])

                # ATUALIZA STATUS
                df_solic.loc[df_solic["usuario"] == usuario_aprovar, "status"] = "Aprovado"

                sheet_solic.update(
                    [df_solic.columns.values.tolist()] + df_solic.values.tolist()
                )

                st.success("Usuário aprovado com sucesso!")
                st.rerun()

        else:
            st.info("Nenhuma solicitação pendente")
