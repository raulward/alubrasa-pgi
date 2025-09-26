import streamlit as st
import pandas as pd
from container import get_container

def page():

    st.title("Controle de Orçamentos 🕹️")

    dashboard, novo_orc, atualizar_orc = st.tabs(["Dashboard", "Novo Orçamento", "Atualizar Orçamento"])

    return
