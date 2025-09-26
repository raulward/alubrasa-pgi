import streamlit as st
import pandas as pd
from services.mapeamento_nfs_service import MapeamentoNFSService
from container import get_container


def page():
    st.header("Mapeamento de campos essenciais de Nota Fiscal 🧾")

    c = get_container()
    svc = c.mapeamento_nfs_service

    descricoes = svc.list_descricoes()
    estados = svc.list_estados()
    ncms = svc.list_ncms()

    desc = st.selectbox("Descrição da operação (natureza):", descricoes, index = 0 if descricoes else None)
    estado = st.selectbox("Estado de destino:", estados, index=(estados.index("DF")) if "DF" in estados else None)
    ncm = st.selectbox("Digite o NCM do produto:", ncms, index = 0 if ncms else None)

    if st.button("Consultar Mapeamento"):
        if not desc or not estado or not ncm:
            st.warning("Preencha os campos corretamente.")
            return

        try:
            combination = svc.combination(desc=desc, ncm=ncm, estado=estado)
        except RuntimeError as e:
            st.error(str(e))
            return
        except Exception as e:
            st.error(f"Erro inesperado: {e}")
            return

        cfop_col, st_col, cest_col, cst_col, aliquota_col = st.columns(5)

        with cfop_col:
            st.subheader("CFOP")
            cfop_val = combination.get("cfop")
            if cfop_val:
                # suporta dict ou string
                if isinstance(cfop_val, dict):
                    st.success(cfop_val.get("cfop") or "-")
                else:
                    st.success(str(cfop_val))
            else:
                st.error("CFOP não encontrado")

        with st_col:
            st.subheader("S.T.")
            st_label = combination.get("subs_trib")  # "SIM" / "NÃO" (string)
            if st_label == "SIM":
                st.success("SIM")
            elif st_label == "NÃO":
                st.info("NÃO")
            else:
                st.warning("-")

        with cest_col:
            st.subheader("CEST")
            cest_val = combination.get("cest")
            if cest_val:
                st.info(str(cest_val))
            else:
                st.warning("-")

        with cst_col:
            st.subheader("CST")
            cst_val = combination.get("cst")
            if cst_val is not None and cst_val != "":
                st.info(str(cst_val))
            else:
                st.warning("-")

        with aliquota_col:
            st.subheader("Alíquota")
            aliq = combination.get("aliquota")
            if aliq is not None:
                try:
                    st.success(f"{float(aliq) * 100:.2f}%")
                except Exception:
                    st.success(str(aliq))
            else:
                st.warning("-")



        with st.expander("Detalhes (debug)"):
            # não repete a descrição nem o NCM conforme pedido
            debug = {
                "cfop": (combination.get("cfop").get("cfop")
                         if isinstance(combination.get("cfop"), dict)
                         else combination.get("cfop")),
                "cest": combination.get("cest"),
                "cst": combination.get("cst"),
                "aliquota": combination.get("aliquota"),
                "st": combination.get("st")
            }
            st.json(debug)
