import unicodedata

import streamlit as st
import pandas as pd
import gspread

from google.oauth2.service_account import Credentials


# ===============================
# ⚙️ CONFIGURAÇÃO DA PÁGINA
# ===============================
st.set_page_config(
    page_title="Sistema de Bloqueio",
    page_icon="assets/logo_petiko.png",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ===============================
# 🎨 CSS
# ===============================
st.markdown(
    """
    <style>

    /* Remove somente o fundo da faixa superior */
    [data-testid="stHeader"] {
        background: transparent;
    }

    /* Mantém o botão de abrir/fechar a sidebar */
    [data-testid="collapsedControl"] {
        display: block;
    }

    /* Ajusta o espaçamento superior */
    .block-container {
        padding-top: 20px !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ===============================
# 🧰 FUNÇÕES AUXILIARES
# ===============================
def normalizar_texto(valor):
    """
    Remove acentos, espaços e converte o texto para minúsculo.

    Exemplos:
    Mandaê -> mandae
    MANDAÊ -> mandae
    """
    texto = str(valor or "").strip().lower()

    texto = unicodedata.normalize(
        "NFKD",
        texto
    ).encode(
        "ascii",
        "ignore"
    ).decode(
        "utf-8"
    )

    return texto


@st.cache_resource
def conectar_google():
    """
    Cria e mantém uma única conexão autenticada com o Google.
    """
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scope
    )

    return gspread.authorize(credentials)


# ===============================
# 🖼️ LOGO PRINCIPAL
# ===============================
st.markdown(
    "<div style='margin-top: 10px;'></div>",
    unsafe_allow_html=True
)

st.image(
    "assets/logo_petiko.png",
    width=220
)


# ===============================
# 🔗 CONEXÃO COM GOOGLE SHEETS
# ===============================
client = conectar_google()

try:
    spreadsheet = client.open_by_key(
        "1IGKJfifqmCdyptPT7INeSjjkW9VnfbQhc4yjKKfwyao"
    )

except Exception:
    st.error(
        "Não foi possível conectar com a planilha do sistema."
    )
    st.stop()


# ===============================
# 👤 CARREGAR USUÁRIOS
# ===============================
try:
    sheet_users = spreadsheet.worksheet("usuarios")

    df_users = pd.DataFrame(
        sheet_users.get_all_records()
    )

except Exception:
    st.error(
        "Não foi possível carregar os usuários do sistema."
    )
    st.stop()


# ===============================
# 🔄 NORMALIZAR BASE DE USUÁRIOS
# ===============================
colunas_usuarios = [
    "usuario",
    "senha",
    "email",
    "perfil",
    "departamento"
]

if df_users.empty:
    df_users = pd.DataFrame(
        columns=colunas_usuarios
    )

else:
    df_users.columns = (
        df_users.columns
        .astype(str)
        .str.strip()
        .str.lower()
    )

    for coluna in colunas_usuarios:
        if coluna not in df_users.columns:
            df_users[coluna] = ""

    df_users = (
        df_users
        .fillna("")
        .astype(str)
        .apply(lambda coluna: coluna.str.strip())
    )


# ===============================
# 🔐 SESSION STATE
# ===============================
if "logado" not in st.session_state:
    st.session_state.logado = False


# ===============================
# 🔐 TELA DE LOGIN
# ===============================
if not st.session_state.logado:

    st.title("🔐 Login do Sistema")

    usuario_digitado = st.text_input(
        "Usuário"
    )

    senha_digitada = st.text_input(
        "Senha",
        type="password"
    )

    if st.button(
    "🔐 Entrar",
    type="primary",
    use_container_width=True
):
        usuario_digitado = usuario_digitado.strip()
        senha_digitada = senha_digitada.strip()

        # ===============================
        # LOGIN ADMINISTRATIVO
        # ===============================
        if (
            usuario_digitado == "admin"
            and senha_digitada == "123456"
        ):
            st.session_state.logado = True
            st.session_state.usuario = "admin"
            st.session_state.perfil = "admin"
            st.session_state.departamento = "Admin"
            st.session_state.email = "admin@empresa.com"

            st.rerun()

        # ===============================
        # LOGIN PELA PLANILHA
        # ===============================
        usuario_encontrado = df_users[
            df_users["usuario"] == usuario_digitado
        ]

        if usuario_encontrado.empty:
            st.error("Usuário não encontrado.")

        else:
            dados_usuario = usuario_encontrado.iloc[0]

            if dados_usuario["senha"] != senha_digitada:
                st.error("Senha incorreta.")

            else:
                st.session_state.logado = True
                st.session_state.usuario = usuario_digitado
                st.session_state.perfil = dados_usuario["perfil"]
                st.session_state.departamento = dados_usuario["departamento"]
                st.session_state.email = dados_usuario["email"]

                st.rerun()


# ===============================
# 🚀 SISTEMA LOGADO
# ===============================
else:

    # ===============================
    # 👤 INFORMAÇÕES DA SIDEBAR
    # ===============================
    st.sidebar.image(
        "assets/logo_petiko.png",
        width=150
    )

    st.sidebar.success(
        f"👤 {st.session_state.get('usuario', '')}"
    )

    st.sidebar.write(
        f"🏢 {st.session_state.get('departamento', '')}"
    )

    st.sidebar.write(
        f"📧 {st.session_state.get('email', '')}"
    )

    if st.sidebar.button(
        "Sair",
        use_container_width=True
    ):
        st.session_state.clear()
        st.rerun()


    # ===============================
    # 📦 TÍTULO DO SISTEMA
    # ===============================
    st.markdown(
        """
        <h4 style="
            margin-top: -10px;
            color: gray;
        ">
            📦 Sistema Logístico
        </h4>
        """,
        unsafe_allow_html=True
    )


    # ===============================
    # 🔒 IDENTIFICAR DEPARTAMENTO
    # ===============================
    departamento = normalizar_texto(
        st.session_state.get(
            "departamento",
            ""
        )
    )

    usuario_mandae = departamento == "mandae"


    # ===============================
    # 📂 MENU
    # ===============================
    st.sidebar.divider()
    st.sidebar.subheader("📂 Menu")


    # ===============================
    # MENU EXCLUSIVO PARA MANDAÊ
    # ===============================
    if usuario_mandae:

        st.sidebar.caption(
            "Atendimento & Logística"
        )

        pagina = st.sidebar.radio(
            "Páginas:",
            [
                "Endereço - Resolver",
                "Bloqueio - Resolver"
            ],
            key="pagina_mandae"
        )


    # ===============================
    # MENU DOS DEMAIS DEPARTAMENTOS
    # ===============================
    else:

        menu_principal = st.sidebar.radio(
            "Selecione o módulo:",
            [
                "Atendimento & Logística",
                "Estoque"
            ],
            key="menu_principal"
        )

        # ===============================
        # ATENDIMENTO & LOGÍSTICA
        # ===============================
        if menu_principal == "Atendimento & Logística":

            pagina = st.sidebar.radio(
                "Páginas:",
                [
                    "Endereço - Solicitar",
                    "Endereço - Resolver",
                    "Bloqueio - Solicitar",
                    "Bloqueio - Resolver",
                    "Previsão de Postagem"
                ],
                key="pagina_atendimento"
            )

        # ===============================
        # ESTOQUE
        # ===============================
        else:

            pagina = st.sidebar.radio(
                "Páginas:",
                [
                    "Cadastro de Produtos",
                    "Baixa de Estoque",
                    "Planejamento Operacional",
                    "Contador de Itens"
                ],
                key="pagina_estoque"
            )


    # ===============================
    # 🛡️ PROTEÇÃO ADICIONAL DO MANDAÊ
    # ===============================
    paginas_permitidas_mandae = [
        "Endereço - Resolver",
        "Bloqueio - Resolver"
    ]

    if (
        usuario_mandae
        and pagina not in paginas_permitidas_mandae
    ):
        st.error(
            "🚫 Você não possui permissão para acessar esta página."
        )
        st.stop()


    # ===============================
    # 🚀 ABRIR PÁGINAS
    # ===============================
    try:

        if pagina == "Endereço - Solicitar":
            exec(
                open(
                    "_pages/endereco_solicitar.py",
                    encoding="utf-8"
                ).read()
            )

        elif pagina == "Endereço - Resolver":
            exec(
                open(
                    "_pages/endereco_resolver.py",
                    encoding="utf-8"
                ).read()
            )

        elif pagina == "Bloqueio - Solicitar":
            exec(
                open(
                    "_pages/solicitar.py",
                    encoding="utf-8"
                ).read()
            )

        elif pagina == "Bloqueio - Resolver":
            exec(
                open(
                    "_pages/resolver.py",
                    encoding="utf-8"
                ).read()
            )

        elif pagina == "Previsão de Postagem":
            exec(
                open(
                    "_pages/previsao_postagem.py",
                    encoding="utf-8"
                ).read()
            )

        elif pagina == "Cadastro de Produtos":
            exec(
                open(
                    "_pages/cadastro_produtos.py",
                    encoding="utf-8"
                ).read()
            )

        elif pagina == "Baixa de Estoque":
            exec(
                open(
                    "_pages/baixa_estoque.py",
                    encoding="utf-8"
                ).read()
            )

        elif pagina == "Planejamento Operacional":
            exec(
                open(
                    "_pages/planejamento.py",
                    encoding="utf-8"
                ).read()
            )

        elif pagina == "Contador de Itens":
            exec(
                open(
                    "_pages/contador_itens.py",
                    encoding="utf-8"
                ).read()
            )

        else:
            st.error(
                "A página selecionada não foi encontrada."
            )

    except FileNotFoundError as erro:
        st.error(
            f"Arquivo da página não encontrado: {erro}"
        )

    except Exception as erro:
        st.error(
            f"Erro ao carregar página: {erro}"
        )
