from __future__ import annotations
import pandas as pd
import streamlit as st
from container import get_container
from time import sleep

def page():

    c = get_container()

    st.header("Importar itens da Obra 📋")

    obras = c.obra_service.list_itens()

    if not obras:
        st.warning("Cadastre uma obra ativa primeiro.")
        return

    label_to_id = {f"{o['nome']} ({o['codigo']})": o["id"] for o in obras}
    obra_label = st.selectbox("Obra", list(label_to_id.keys()))
    obra_id = label_to_id[obra_label]

    st.subheader("Modelo da planilha 📂")
    st.download_button(
        "Baixar modelo (.xlsx)",
        data=c.itens_orcados_service.build_template_bytes(),
        file_name="modelo_itens_de_obra.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )

    st.divider()

    st.subheader("Upload ⬆️")
    up = st.file_uploader("Selecione o arquivo .xlsx", type=["xlsx"])
    if not up:
        st.info("Faça download do modelo, preencha e depois suba aqui.")
        return

    try:
        preview_df = c.itens_orcados_service.preview_dataframe(up.getvalue(), limit=200)
    except Exception as e:
        st.error(f"Erro ao ler a planilha: {e}")
        return

    st.caption("Pré-visualização (cabeçalhos normalizados)")
    st.dataframe(preview_df, width="stretch", hide_index=True)

    st.info("Clique em 'Importar' para validar e gravar em lote.")
    if st.button("Importar", type="primary"):
        ok, db_errors, val_errors = c.itens_orcados_service.import_file(id_obra=obra_id, file_bytes=up.getvalue())

        if val_errors:
            st.warning(f"{len(val_errors)} linha(s) inválida(s) (validação).")
            with st.expander("Ver erros de validação"):
                for e in val_errors:
                    st.write(f"Linha {e['index']} - código: {e.get('codigo')}")
                    st.write("• " + " | ".join(e["erros"]))

        if db_errors:
            st.warning(f"{len(db_errors)} falha(s) no banco (duplicidade/constraint).")
            with st.expander("Ver erros de banco"):
                for e in db_errors:
                    st.write(f"Linha {e['index']} - código: {e.get('codigo')} - erro: {e['erro']}")


        st.success(f"{ok}  {'item' if ok == 1 else 'itens'} inserido(s).")
        st.toast("Importação concluída.")
        sleep(3)
        st.rerun()
