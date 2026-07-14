import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(
    page_title="Sistema de Bloqueio",
    page_icon="assets/logo_petiko.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===============================
# 🎨 CSS FINAL
# ===============================
st.markdown("""
<style>

/* 🔥 REMOVE SOMENTE A FAIXA */
[data-testid="stHeader"] {
    background: transparent;
}

/* 🔥 MANTÉM BOTÃO DA SIDEBAR */
[data-testid="collapsedControl"] {
    display: block;
}

/* 🔥 AJUSTA TOPO */
.block-container {
    padding-top: 20px !important;
}

</style>
""", unsafe_allow_html=True)

# 🔥 ESPAÇAMENTO CONTROLADO
st.markdown(
    "<div style='margin-top: 10px;'></div>",
    unsafe_allow_html=True
)

# 🔥 LOGO AJUSTADA
st.image(
    "assets/logo_petiko.png",
    width=220
)

# ===============================
# 🔗 CONEXÃO (OTIMIZADA)
# ===============================
@st.cache_resource
def conectar_google():

    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scope
    )

    client = gspread.authorize(credentials)

    return client

client = conectar_google()

try:

    spreadsheet = client.open_by_key(
        "1IGKJfifqmCdyptPT7INeSjjkW9VnfbQhc4yjKKfwyao"
    )

except:

    st.error("Erro ao conectar com a planilha")
    st.stop()

# ===============================
# 👤 USUÁRIOS
# ===============================
sheet_users = spreadsheet.worksheet("usuarios")

df_users = pd.DataFrame(
    sheet_users.get_all_records()
)

if not df_users.empty:

    df_users.columns = (
        df_users.columns
        .str.strip()
        .str.lower()
    )

    for col in [
        "usuario",
        "senha",
        "email",
        "perfil",
        "departamento"
    ]:

        if col not in df_users.columns:
            df_users[col] = ""

    df_users = (
        df_users
        .fillna("")
        .astype(str)
        .apply(lambda x: x.str.strip())
    )

# ===============================
# 🔐 SESSION
# ===============================
if "logado" not in st.session_state:
    st.session_state.logado = False

# ===============================
# 🔐 LOGIN
# ===============================
if not st.session_state.logado:

    st.title("🔐 Login do Sistema")

    usuario = st.text_input("Usuário")

    senha = st.text_input(
        "Senha",
        type="password"
    )

    if st.button("Entrar"):

        usuario = usuario.strip()
        senha = senha.strip()

        # 🔥 LOGIN ADMIN
        if usuario == "admin" and senha == "123456":

            st.session_state.logado = True
            st.session_state.usuario = "admin"
            st.session_state.perfil = "admin"
            st.session_state.departamento = "Admin"
            st.session_state.email = "admin@empresa.com"

            st.rerun()

        user = df_users[
            df_users["usuario"] == usuario
        ]

        if not user.empty:

            user = user.iloc[0]

            if user["senha"] == senha:

                st.session_state.logado = True
                st.session_state.usuario = usuario
                st.session_state.perfil = user["perfil"]
                st.session_state.departamento = user["departamento"]
                st.session_state.email = user["email"]

                st.rerun()

            else:
                st.error("Senha incorreta")

        else:
            st.error("Usuário não encontrado")

# ===============================
# 🚀 SISTEMA
# ===============================
else:

    # 🔥 SIDEBAR
    st.sidebar.image(
        "assets/logo_petiko.png",
        width=150
    )

    st.sidebar.success(
        f"👤 {st.session_state.usuario}"
    )

    st.sidebar.write(
        f"🏢 {st.session_state.departamento}"
    )

    st.sidebar.write(
        f"📧 {st.session_state.email}"
    )

    if st.sidebar.button("Sair"):

        st.session_state.clear()
        st.rerun()

    # 🔥 TÍTULO
    st.markdown(
        """
        <h4 style='margin-top:-10px; color: gray;'>
        📦 Sistema Logístico
        </h4>
        """,
        unsafe_allow_html=True
    )

        # 🔥 MENU
    st.sidebar.divider()

    st.sidebar.subheader("📂 Menu")

    menu_principal = st.sidebar.radio(
        "Selecione o módulo:",
        [
            "Atendimento & Logística",
            "Estoque"
        ]
    )

    departamento = (
        st.session_state.get("departamento", "")
        .strip()
        .lower()
    )

# ===============================
# 🔒 DEPARTAMENTO DO USUÁRIO
# ===============================
departamento = (
    st.session_state.get("departamento", "")
    .strip()
    .lower()
)

    
    # ===============================
    # 📦 LOGÍSTICA
    # ===============================
    departamento = (
        st.session_state.get("departamento", "")
        .strip()
        .lower()
    )

    if menu_principal == "Atendimento & Logística":

    # Apenas o departamento Mandaê possui menu reduzido
    if departamento in ["mandae", "mandaê"]:

        pagina = st.sidebar.radio(
            "Páginas:",
            [
                "Endereço - Resolver",
                "Bloqueio - Resolver"
            ]
        )

    # Todos os demais continuam iguais
    else:

        pagina = st.sidebar.radio(
            "Páginas:",
            [
                "Endereço - Solicitar",
                "Endereço - Resolver",
                "Bloqueio - Solicitar",
                "Bloqueio - Resolver",
                "Previsão de Postagem"
            ]
        )

    # ===============================
    # 📦 ESTOQUE
    # ===============================
    elif menu_principal == "Estoque":

    # Apenas o departamento Mandaê não possui acesso
    if departamento in ["mandae", "mandaê"]:
        st.error("🚫 Você não possui permissão para acessar este módulo.")
        st.stop()

    pagina = st.sidebar.radio(
        "Páginas:",
        [
            "Cadastro de Produtos",
            "Baixa de Estoque",
            "Planejamento Operacional",
            "Contador de Itens"
        ]
    )
