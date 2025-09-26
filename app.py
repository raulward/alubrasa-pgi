import streamlit as st
from sidebar_accordion_menu import sidebar_accordion_menu

st.set_page_config(page_title="PGI - Plataforma de Gestão Integrada", layout="wide")

menu = {
    "🏠 Home": None,  # Main page
    "💼 Administração de Obras": {
        "🏗️ Controle de Obras": "controle_de_obras",
        "💲 Controle de Orçamentos": "controle_de_orcamentos"
    },
    "💰 Financeiro": {
        "🧾 Mapeamento de NFs": "mapeamento_nf",
    },
    "🏪 Comercial": {
        "🏷️ Precificacao": "precificacao"
    }
}

# Render the accordion menu
sidebar_accordion_menu(menu)

# Main page content
st.title("PGI - Plataforma de Gestão Integrada Alubrasa")
st.write("Selecione uma página do menu lateral.")
