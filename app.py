import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(
    page_title="Sistema de Bloqueio",
    page_icon="assets/logo_petiko.png",
    layout="wide"
)

# ===============================
# 🎨 CSS
# ===============================
st.markdown("""
<style>
.block-container {
    padding-top: 20px !important;
}
</style>
""", unsafe_allow_html=True)

# 🔥 LOGO
st.image("assets/logo_petiko.png", width=180)

# ===============================
# 🔗 CONEXÃO
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
    spreadsheet = client.open_by_key("1IGKJfifqmCdyptPT7INeSjjkW9VnfbQhc4yjKKfwyao")
except:
    st.error("Erro ao conectar com a planilha")
    st.stop()

# ===============================
# 👤 USUÁRIOS
# ===============================
sheet_users = spreadsheet.worksheet("usuarios")
df_users = pd.DataFrame(sheet_users.get_all_records())

if not df_users.empty:
    df_users.columns = df_users.columns.str.strip().str.lower()

    for col in ["usuario", "senha", "email", "perfil", "departamento"]:
        if col not in df_users.columns:
            df_users[col] = ""

    df_users = df_users.fillna("").astype(str).apply(lambda x: x.str.strip())

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
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):

        usuario = usuario.strip()
        senha = senha.strip()

        if usuario == "admin" and senha == "123456":
            st.session_state.logado = True
            st.session_state.usuario = "admin"
            st.session_state.perfil = "admin"
            st.session_state.departamento = "Admin"
            st.session_state.email = "admin@empresa.com"
            st.rerun()

        user = df_users[df_users["usuario"] == usuario]

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

    st.sidebar.image("assets/logo_petiko.png", width=150)

    st.sidebar.success(f"👤 {st.session_state.usuario}")
    st.sidebar.write(f"🏢 {st.session_state.departamento}")
    st.sidebar.write(f"📧 {st.session_state.email}")

    if st.sidebar.button("Sair"):
        st.session_state.clear()
        st.rerun()

    st.markdown(
        "<h4 style='margin-top:-10px; color: gray;'>📦 Sistema Logístico</h4>",
        unsafe_allow_html=True
    )

    st.sidebar.divider()
    st.sidebar.subheader("📂 Menu")

    menu_principal = st.sidebar.radio(
        "Selecione o módulo:",
        ["Atendimento & Logística", "Estoque"]
    )

    if menu_principal == "Atendimento & Logística":
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

    elif menu_principal == "Estoque":
        pagina = st.sidebar.radio(
            "Páginas:",
            [
                "Cadastro de Produtos",
                "Baixa de Estoque",
                "Planejamento Operacional",
                "Contador de Itens"
            ]
        )

    try:

        if pagina == "Endereço - Solicitar":
            exec(open("_pages/endereco_solicitar.py").read())

        elif pagina == "Endereço - Resolver":
            exec(open("_pages/endereco_resolver.py").read())

        elif pagina == "Bloqueio - Solicitar":
            exec(open("_pages/solicitar.py").read())

        elif pagina == "Bloqueio - Resolver":
            exec(open("_pages/resolver.py").read())

        elif pagina == "Cadastro de Produtos":
            exec(open("_pages/cadastro_produtos.py").read())

        elif pagina == "Baixa de Estoque":
            exec(open("_pages/baixa_estoque.py").read())

        elif pagina == "Planejamento Operacional":
            exec(open("_pages/planejamento.py").read())

        elif pagina == "Contador de Itens":
            exec(open("_pages/contador_itens.py").read())

        elif pagina == "Previsão de Postagem":
            exec(open("_pages/previsao_postagem.py").read())

    except Exception as e:
        st.error(f"Erro ao carregar página: {e}")
