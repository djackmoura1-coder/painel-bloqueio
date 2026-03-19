import streamlit as st

# CONFIG
st.set_page_config(
    page_title="Sistema de Bloqueio",
    layout="wide"
)

# 🔐 USUÁRIOS (BASE SIMPLES)
usuarios = {
    "djack": {"senha": "123", "perfil": "admin"},
    "operador1": {"senha": "123", "perfil": "operador"}
}

# SESSION
if "logado" not in st.session_state:
    st.session_state.logado = False

# LOGIN
if not st.session_state.logado:

    st.title("🔐 Login do Sistema")

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):

        if usuario in usuarios and usuarios[usuario]["senha"] == senha:
            st.session_state.logado = True
            st.session_state.usuario = usuario
            st.session_state.perfil = usuarios[usuario]["perfil"]
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos")

else:

    st.sidebar.success(f"Logado como: {st.session_state.usuario}")

    if st.sidebar.button("Sair"):
        st.session_state.logado = False
        st.rerun()

    st.title("📦 Sistema de Bloqueio de Pedidos")

    st.markdown("""
    Use o menu lateral para navegar:

    📌 Solicitar  
    🔧 Resolver  
    📊 Dashboard  
    """)
