from __future__ import annotations
import streamlit as st
from container import get_container

def page():
    c = get_container()

    st.header("Cadastro: Clientes & Obras 🚧🛠️")
    tab1, tab2 = st.tabs(["Clientes", "Obras"])

    with tab1:
        st.subheader("Cadastro de Cliente 👥🤝")
        with st.form("form_cliente"):
            nome = st.text_input("Nome")
            email = st.text_input("E-mail")
            codigo_identificador = st.text_input("CPF/CNPJ")
            telefone = st.text_input("Telefone")
            endereco = st.text_area("Endereço")
            if st.form_submit_button("Cadastrar Cliente"):
                try:
                    rec = c.cliente_service.cadastrar(nome=nome, email=email, cnpj=codigo_identificador, telefone=telefone, endereco=endereco)
                    if not rec:
                        st.success("Cliente salvo.")           # fallback seguro
                    else:
                        st.success(f"Cliente criado: {rec.get('nome')} ({rec.get('cnpj')}).")
                    st.toast("Cliente salvo com sucesso.")
                    st.rerun()
                except ValueError as e:
                      st.error(str(e))
            st.write("\n")
            st.caption("Clientes ativos")
            data = c.cliente_repo.list_clientes()
            st.dataframe(data, use_container_width=True, hide_index=True)

    with tab2:
        st.subheader("Cadastro de Obras 🏗️🏢")
        clientes = c.cliente_repo.list_clientes()
        if not clientes:
            st.warning("Cadastre ao menos um cliente.")
            return
        nome_to_id = {f"{x['nome']} ({x['cnpj']})": x['id'] for x in clientes}
        cli_label = st.selectbox("Clientes", list(nome_to_id.keys()))
        with st.form("form_obra"):
            nome = st.text_input("Nome da obra")
            endereco = st.text_area("Endereço da obra")
            cnpj = st.text_input("CNPJ da obra")
            codigo = st.text_input("Código da obra")
            if st.form_submit_button("Salvar obra"):
                try:
                    rec = c.obra_service.cadastrar(id_cliente=nome_to_id[cli_label], nome=nome, endereco=endereco, cnpj=cnpj, codigo=codigo)
                    st.success(f"Obra criada: {rec['nome']} (código {rec['codigo']}).")
                    st.toast("Obra salva.")
                except ValueError as e:
                    st.error(str(e))
