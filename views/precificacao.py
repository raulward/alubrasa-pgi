import streamlit as st
import pandas as pd
from container import get_container
from services.precificacao_service import LinhaMemoria

def render_memoria(linhas: list[LinhaMemoria], titulo: str):
    df = pd.DataFrame([{
        "Etapa": l.etapa,
        "Alíquota": l.aliquota,
        "Δ (R$)": l.delta,
        "Total (R$)": l.total
    } for l in linhas])

    st.subheader(titulo)
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )


def page():

    st.header("🏷️ Precificação")

    c = get_container()

    tab1, tab2 = st.tabs(["Precificação Simples", "Memória de Cálculo"])

    with tab1:
        st.subheader("Precificação Simples")
        with st.form("form_precificacao_simples"):
            custo = st.number_input("Digite o preço custo: ")
            margem_custo_fixo = st.number_input("Insira a margem de contribuição de custo fixo (%): ")
            margem_lucro_bruto = st.number_input("Insira a margem de lucro bruto pretendida (%): ")
            ncms = c.mapeamento_nfs_service.list_ncms()   # <-- CHAME a função
            ncms = [str(x) for x in list(ncms)] # Refatorar
            ncm = st.selectbox("Insira o NCM do produto:", ncms, index=0)
            uf_origem = st.selectbox("Insira a UF de origem:", c.precificacao_service.list_ufs(), index=0)
            submitted = st.form_submit_button("Calcular")
            if submitted:
                try:
                    valor_final = c.precificacao_service.calcular(custo, margem_custo_fixo, margem_lucro_bruto, ncm, uf_origem)
                    if valor_final:
                        st.subheader("Valor de venda final: ")
                        st.success(f"Preço final: R$ {valor_final:,.2f}")
                except Exception as e:
                    st.error(f"Um erro inesperado ocorreu: {e}")

    with tab2:
        st.subheader("Memória de Cálculo:")
        with st.form("form_memoria_calculo", clear_on_submit=False):
            # Entradas
            custo_base = st.number_input("Custo com impostos (R$)", min_value=0.0, step=0.01, value=100.00)
            mcf_pct = st.number_input("Margem Cont. Custo Fixo (%)", min_value=0.0, max_value=100.0, step=0.01, value=10.00)
            mlb_pct = st.number_input("Margem de Lucro Bruta Pretendida (%)", min_value=0.0, max_value=100.0, step=0.01, value=20.00)

            # UF destino
            ufs = c.precificacao_service.list_ufs()
            df_index = ufs.index("DF") if "DF" in ufs else 0
            uf_destino = st.selectbox("UF de destino", ufs, index=df_index)

            # NCM (deixe campo livre para evitar problemas de serialização)
            ncm = st.text_input("NCM (8 dígitos, só números)", value="")

            submitted = st.form_submit_button("Gerar memória")

        if not submitted:
            st.stop()

        # Converte percentuais para fração
        mcf = mcf_pct / 100.0
        mlb = mlb_pct / 100.0

        # Gera memória (usa o mesmo service do cálculo)
        linhas = c.precificacao_service.memoria_calculo(
            custo_base=custo_base,
            margem_custo_fixo=mcf,
            margem_lucro_bruto=mlb,
            ncm=ncm,
            uf_destino=uf_destino,
        )

        # Tabela
        df = pd.DataFrame([{
            "Etapa": l.etapa,
            "Alíquota": l.aliquota,
            "Δ (R$)": l.delta,
            "Total (R$)": l.total
        } for l in linhas])

        st.subheader("Etapas")
        st.dataframe(df, use_container_width=True, hide_index=True)

        # Rótulo do cenário
        ultima = (linhas[-1].etapa or "").lower()
        if "st/convênio" in ultima:
            scen = "Com ST • Convênio (ICMS saída 0%)"
        elif "st s/ convênio" in ultima:
            scen = "Com ST • Sem Convênio (ICMS saída 20%)"
        else:
            scen = "Sem ST (ICMS entrada 12% / saída 13%)"
        st.caption(f"Cenário detectado: {scen}")
