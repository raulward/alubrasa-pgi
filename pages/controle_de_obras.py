import streamlit as st
from views import cadastro_obras  # sua view real
from sidebar_accordion_menu import sidebar_accordion_menu

menu = {
    "🏠 Home": None,  # Main page
    "💼 Administração de Obras": {
        "🏗️ Controle de Obras": "controle_de_obras",
        "💲 Controle de Orçamentos": "controle_de_orcamentos"
    },
    "💰 Financeiro": {
        "🧾 Mapeamento de NFs": "mapeamento_nf",
    }
}

# Render the accordion menu
sidebar_accordion_menu(menu)

cadastro_obras.page()
