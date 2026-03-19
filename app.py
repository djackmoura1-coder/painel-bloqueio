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

# 🔑 PLANILHAS
spreadsheet = client.open_by_key("1IGKJfifqmCdyptPT7INeSjjkW9VnfbQhc4yjKKfwyao")

sheet_users = spreadsheet.worksheet("usuarios")
sheet_solic = spreadsheet.worksheet("solicitacoes_usuarios")

# 🔄 DADOS
df_users = pd.DataFrame(sheet_users.get_all_records())
df_solic = pd.DataFrame(sheet_solic.get_all_records())

# SESSION
if "logado" not in st.session_state:
    st.session_state.logado = False

# 🔐 LOGIN
if not st.session_state.logado:

    st.title("🔐 Login do Sistema")

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):

        if not df_users.empty and usuario in df_users["usuario"].values:

            user_data = df_users[df_users["usuario"] == usuario].iloc[0]

            if user_data["senha"] == senha:

                st.session_state.logado = True
                st.session_state.usuario = usuario
                st.session_state.perfil = user_data["perfil"]
                st.session_state.departamento = user_data.get("departamento", "")

                st.rerun()

            else:
                st.error("Senha incorreta")

        else:
            st.error("Usuário não encontrado")

    # 📌 CADASTRO
    st.divider()
    st.subheader("📌 Solicitar acesso")

    novo_usuario = st.text_input("Novo usuário")
    nova_senha = st.text_input("Nova senha", type="password")

    departamento = st.selectbox(
        "Departamento",
        ["Atendimento", "Logística", "Faturamento", "Expedição"]
    )

    if st.button("Solicitar cadastro"):

        if novo_usuario == "" or nova_senha == "":
            st.warning("Preencha todos os campos")

        elif not df_solic.empty and novo_usuario in df_solic["usuario"].values:
            st.warning("Usuário já solicitado")

        else:

            sheet_solic.append_row([
                str(novo_usuario),
                str(nova_senha),
                "operador",
                str(departamento),
                "Pendente"
            ])

            st.success("Solicitação enviada! Aguarde aprovação.")
            st.rerun()

# 🔓 SISTEMA LIBERADO
else:

    st.sidebar.success(f"👤 {st.session_state.usuario}")
    st.sidebar.write(f"🏢 {st.session_state.departamento}")

    if st.sidebar.button("Sair"):
        st.session_state.logado = False
        st.rerun()

    st.title("📦 Sistema Operacional de Bloqueio")

    st.markdown("""
    Use o menu lateral:

    📌 Solicitar  
    🔧 Resolver  
    📊 Dashboard  
    """)

    # 🔐 APROVAÇÃO (ADMIN)
    if st.session_state.perfil == "admin":

        st.divider()
        st.subheader("👤 Aprovação de usuários")

        pendentes = df_solic[df_solic["status"] == "Pendente"]

        if not pendentes.empty:

            usuario_aprovar = st.selectbox(
                "Usuários pendentes",
                pendentes["usuario"]
            )

            perfil_escolhido = st.selectbox(
                "Definir perfil",
                ["operador", "admin"]
            )

            if st.button("Aprovar usuário"):

                dados = pendentes[pendentes["usuario"] == usuario_aprovar].iloc[0]

                sheet_users.append_row([
                    str(dados["usuario"]),
                    str(dados["senha"]),
                    str(perfil_escolhido),
                    str(dados["departamento"])
                ])

                # REMOVE DA LISTA DE PENDENTES
                df_solic = df_solic[df_solic["usuario"] != usuario_aprovar]
                sheet_solic.clear()
                sheet_solic.append_row(df_solic.columns.tolist())

                for i in df_solic.values.tolist():
                    sheet_solic.append_row(i)

                st.success("Usuário aprovado com sucesso!")
                st.rerun()

        else:
            st.info("Nenhuma solicitação pendente.")
