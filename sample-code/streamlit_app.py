import re
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))

st.set_page_config(
    page_title="SAP AI SDK · Demo",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
[data-testid="stSidebar"] { border-right: 1px solid rgba(0,0,0,0.08); }
h1 { font-weight: 700; letter-spacing: -0.3px; }
h2 { font-weight: 600; }
h3 { font-weight: 600; }
[data-testid="stDataFrame"] { border: 1px solid rgba(0,0,0,0.08); border-radius: 6px; }
.tag-fixed  { display:inline-block; padding:1px 7px; border-radius:4px; font-size:0.75rem;
              font-weight:600; background:#f1f3f4; color:#5f6368; border:1px solid #dadce0;
              vertical-align:middle; margin-left:6px; }
.tag-config { display:inline-block; padding:1px 7px; border-radius:4px; font-size:0.75rem;
              font-weight:600; background:#e8f0fe; color:#1a73e8; border:1px solid #c5d6f8;
              vertical-align:middle; margin-left:6px; }
</style>
""", unsafe_allow_html=True)

_FIXED  = '<span class="tag-fixed">fixed</span>'
_CONFIG = '<span class="tag-config">configurable</span>'


# ─── Sidebar ──────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### SAP AI SDK")
    st.caption("Python SDK · Capabilities Demo")
    st.divider()
    page = st.radio(
        "section",
        ["Overview", "SAP RPT", "Document Grounding", "Orchestration"],
        label_visibility="collapsed",
    )
    st.divider()
    st.caption("SAP AI Core  ·  Gen AI Hub")
    st.markdown(f"""
**Legend**

{_FIXED} &nbsp;hard-coded in this demo

{_CONFIG} &nbsp;you can change the value
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# OVERVIEW
# ══════════════════════════════════════════════════════════════════
if page == "Overview":
    st.title("SAP Cloud SDK for AI (Python)")
    st.divider()

    col1, col2, col3 = st.columns(3, gap="large")

    with col1:
        st.subheader("SAP RPT")
        st.markdown("""
Predict missing values in tabular data — no prompts required.

- **Classification** — infer categorical values
- **Regression** — predict numeric values
- Mark any cell `[PREDICT]`, edit rows freely
        """)

    with col2:
        st.subheader("Document Grounding")
        st.markdown("""
Build a vector knowledge base and retrieve content by natural language query.

- **Create collection** — vector store + embedding model
- **Ingest documents** — text chunks with metadata
- **Search** — top-k chunks scoped to the collection
        """)

    with col3:
        st.subheader("Orchestration Service")
        st.markdown("""
Modular pipeline for governed LLM calls.

- Completion, templates, streaming, tool calls, fallback
- **Data masking** — SAP DPI before the LLM
- **Content filtering** — input & output safety
- **Multimodal** — image input
- **Translation** — input/output language pairs
        """)

    st.divider()
    st.subheader("Architecture")
    st.markdown("""
```
sap-ai-sdk-gen
├── gen_ai_hub.proxy.native.sap     →  SAP RPT         (RPTClient)
├── gen_ai_hub.document_grounding   →  Grounding        (VectorAPIClient, RetrievalAPIClient)
└── gen_ai_hub.orchestration_v2     →  Orchestration    (OrchestrationService)
```
Authentication via `AICORE_*` environment variables.
    """)


# ══════════════════════════════════════════════════════════════════
# SAP RPT
# ══════════════════════════════════════════════════════════════════
elif page == "SAP RPT":
    st.title("SAP RPT")
    st.markdown("Mark any cell `[PREDICT]` and the model infers its value from the surrounding rows. No prompts required.")
    st.divider()

    tab_cls, tab_reg = st.tabs(["Classification", "Regression"])

    # ── Classification ─────────────────────────────────────────────
    with tab_cls:
        st.markdown(f"**Classification — Cost Center** {_CONFIG}", unsafe_allow_html=True)
        st.markdown("Edit the table directly, then run prediction. The row with `[PREDICT]` will be classified.")

        default_cls = [
            {"ID": "35",  "PRODUCT": "Couch",        "PRICE": 999.99,  "ORDERDATE": "28-11-2025", "COSTCENTER": "[PREDICT]"},
            {"ID": "44",  "PRODUCT": "Office Chair", "PRICE": 150.80,  "ORDERDATE": "02-11-2025", "COSTCENTER": "Office Furniture"},
            {"ID": "104", "PRODUCT": "Server Rack",  "PRICE": 2200.00, "ORDERDATE": "01-11-2025", "COSTCENTER": "Data Infrastructure"},
        ]
        df_cls_edited = st.data_editor(
            pd.DataFrame(default_cls), use_container_width=True, hide_index=True, key="rpt_cls_editor"
        )

        col_m, _ = st.columns([1, 3])
        with col_m:
            model_rpt_cls = st.selectbox("Model:", ["sap-rpt-1-small"], key="rpt_cls_model")

        if st.button("Run Classification", type="primary", key="rpt_cls_run"):
            with st.spinner("Calling SAP RPT…"):
                try:
                    from gen_ai_hub.proxy.native.sap.client import RPTClient
                    from gen_ai_hub.proxy.native.sap.models import DataType, PredictionConfig, RPTRequest, TargetColumn

                    rows = df_cls_edited.to_dict(orient="records")
                    schema = {
                        "ID": DataType(dtype="string"), "PRODUCT": DataType(dtype="string"),
                        "PRICE": DataType(dtype="numeric"), "ORDERDATE": DataType(dtype="date"),
                        "COSTCENTER": DataType(dtype="string"),
                    }
                    body = RPTRequest(
                        prediction_config=PredictionConfig(target_columns=[
                            TargetColumn(name="COSTCENTER", prediction_placeholder="[PREDICT]", task_type="classification")
                        ]),
                        index_column="ID", rows=rows, data_schema=schema,
                    )
                    result = RPTClient().predict(body=body, model_name=model_rpt_cls)

                    # Inspect the real structure of the first Prediction object
                    with st.expander("Debug — Prediction object structure"):
                        if result.predictions:
                            p0 = result.predictions[0]
                            st.write("type:", type(p0))
                            st.write("root:", p0.root)

                    predictions = {}
                    confidence  = {}
                    for p in result.predictions:
                        root      = p.root
                        row_id    = root.get("ID") or root.get("id")
                        pred_list = root.get("COSTCENTER", [])
                        if row_id is not None and isinstance(pred_list, list) and pred_list:
                            first = pred_list[0]
                            predictions[str(row_id)] = first.prediction
                            confidence[str(row_id)]  = getattr(first, "confidence", None)

                    df_out = df_cls_edited.copy()
                    df_out["ID"] = df_out["ID"].astype(str)
                    for idx, row in df_out.iterrows():
                        if row["COSTCENTER"] == "[PREDICT]" and row["ID"] in predictions:
                            df_out.at[idx, "COSTCENTER"] = predictions[row["ID"]]

                    st.markdown("**Result:**")
                    st.dataframe(df_out, use_container_width=True, hide_index=True)
                    for id_, pred in predictions.items():
                        conf = confidence.get(id_)
                        conf_str = f" (confidence: {conf:.0%})" if conf is not None else ""
                        st.success(f"ID {id_} → **{pred}**{conf_str}")

                    with st.expander("Raw API response"):
                        st.write(result)
                except Exception as e:
                    st.error(str(e))

    # ── Regression ─────────────────────────────────────────────────
    with tab_reg:
        st.markdown(f"**Regression — Discount Rate** {_CONFIG}", unsafe_allow_html=True)
        st.markdown("Rows with `[PREDICT]` will receive a predicted numeric value.")

        default_reg = [
            {"ID": "35",  "PRODUCT": "Couch",           "PRICE": 999.99,  "ORDERDATE": "28-11-2025", "DISCOUNT_RATE": "[PREDICT]"},
            {"ID": "44",  "PRODUCT": "Office Chair",    "PRICE": 150.80,  "ORDERDATE": "02-11-2025", "DISCOUNT_RATE": "0.12"},
            {"ID": "104", "PRODUCT": "Server Rack",     "PRICE": 2200.00, "ORDERDATE": "01-11-2025", "DISCOUNT_RATE": "0.05"},
            {"ID": "205", "PRODUCT": "Standing Desk",   "PRICE": 640.00,  "ORDERDATE": "05-11-2025", "DISCOUNT_RATE": "0.10"},
            {"ID": "306", "PRODUCT": "Monitor 27 inch", "PRICE": 289.99,  "ORDERDATE": "08-11-2025", "DISCOUNT_RATE": "[PREDICT]"},
        ]
        df_reg_edited = st.data_editor(
            pd.DataFrame(default_reg), use_container_width=True, hide_index=True, key="rpt_reg_editor"
        )

        if st.button("Run Regression", type="primary", key="rpt_reg_run"):
            with st.spinner("Calling SAP RPT…"):
                try:
                    from gen_ai_hub.proxy.native.sap.client import RPTClient
                    from gen_ai_hub.proxy.native.sap.models import DataType, PredictionConfig, RPTRequest, TargetColumn

                    rows = []
                    for r in df_reg_edited.to_dict(orient="records"):
                        row = dict(r)
                        if row["DISCOUNT_RATE"] != "[PREDICT]":
                            try:
                                row["DISCOUNT_RATE"] = float(row["DISCOUNT_RATE"])
                            except (ValueError, TypeError):
                                pass
                        rows.append(row)

                    schema = {
                        "ID": DataType(dtype="string"), "PRODUCT": DataType(dtype="string"),
                        "PRICE": DataType(dtype="numeric"), "ORDERDATE": DataType(dtype="date"),
                        "DISCOUNT_RATE": DataType(dtype="numeric"),
                    }
                    body = RPTRequest(
                        prediction_config=PredictionConfig(target_columns=[
                            TargetColumn(name="DISCOUNT_RATE", task_type="regression")
                        ]),
                        index_column="ID", rows=rows, data_schema=schema,
                    )
                    result = RPTClient().predict(body=body, model_name="sap-rpt-1-small")

                    predictions = {}
                    for p in result.predictions:
                        root      = p.root
                        row_id    = root.get("ID") or root.get("id")
                        pred_list = root.get("DISCOUNT_RATE", [])
                        if row_id is not None and isinstance(pred_list, list) and pred_list:
                            predictions[str(row_id)] = pred_list[0].prediction
                    df_out = df_reg_edited.copy()
                    df_out["ID"] = df_out["ID"].astype(str)
                    for idx, row in df_out.iterrows():
                        if row["DISCOUNT_RATE"] == "[PREDICT]" and row["ID"] in predictions:
                            df_out.at[idx, "DISCOUNT_RATE"] = f"{predictions[row['ID']]:.4f}"

                    st.markdown("**Result:**")
                    st.dataframe(df_out, use_container_width=True, hide_index=True)
                    for id_, pred in predictions.items():
                        st.success(f"ID {id_} → **{pred:.4f}**")

                    with st.expander("Raw API response"):
                        st.write(result)
                except Exception as e:
                    st.error(str(e))


# ══════════════════════════════════════════════════════════════════
# DOCUMENT GROUNDING
# ══════════════════════════════════════════════════════════════════
elif page == "Document Grounding":
    st.title("Document Grounding")
    st.markdown("Build a vector knowledge base and retrieve relevant content by natural language query.")
    st.divider()

    for k, v in [("collection_id", None), ("docs_added", False)]:
        if k not in st.session_state:
            st.session_state[k] = v

    done1 = bool(st.session_state.collection_id)
    done2 = st.session_state.docs_added

    c1, c2, c3 = st.columns(3)
    with c1:
        (st.success if done1 else st.info)(f"Step 1 — Create Collection {'✓' if done1 else ''}")
    with c2:
        (st.success if done2 else st.info)(f"Step 2 — Add Documents {'✓' if done2 else ''}")
    with c3:
        (st.success if (done1 and done2) else st.info)(f"Step 3 — Search {'✓' if (done1 and done2) else ''}")
    st.divider()

    # ── Step 1 ──────────────────────────────────────────────────────
    with st.expander("Step 1 — Create Vector Collection", expanded=not done1):
        st.markdown(f"Collection title and embedding model are {_CONFIG}.", unsafe_allow_html=True)
        col_t, col_e = st.columns(2)
        with col_t:
            col_title = st.text_input("Collection title:", value="sample-collection", key="grnd_title")
        with col_e:
            col_model = st.selectbox("Embedding model:", ["text-embedding-3-small", "text-embedding-3-large", "text-embedding-ada-002"], key="grnd_model")

        if done1:
            st.success(f"Active collection: `{st.session_state.collection_id}`")

        left, right = st.columns([1, 2])
        with left:
            if st.button("Create Collection", type="primary", key="grnd_create"):
                with st.spinner("Creating…"):
                    try:
                        from gen_ai_hub.document_grounding.client import VectorAPIClient
                        from gen_ai_hub.document_grounding.models.vector import CollectionCreateRequest, EmbeddingConfig, VectorKeyValueListPair
                        import time as _time
                        client = VectorAPIClient()
                        client.create_collection(
                            CollectionCreateRequest(
                                title=col_title,
                                embeddingConfig=EmbeddingConfig(modelName=col_model),
                                metadata=[VectorKeyValueListPair(key="source", value=["sample-code"])],
                            )
                        )
                        # 202 Accepted — body is empty; poll get_collections until the new one appears
                        cid = None
                        for attempt in range(6):
                            _time.sleep(2)
                            all_cols = client.get_collections()
                            col_list = all_cols if isinstance(all_cols, list) else getattr(all_cols, "resources", getattr(all_cols, "results", []))
                            for c in col_list:
                                t = getattr(c, "title", None) or (c.get("title") if isinstance(c, dict) else None)
                                if t == col_title:
                                    cid = getattr(c, "id", None) or (c.get("id") if isinstance(c, dict) else None)
                                    break
                            if cid:
                                break
                        if cid:
                            st.session_state.collection_id = cid
                            st.success(f"Created — ID: `{cid}`")
                            st.rerun()
                        else:
                            # Show all collections so the user can pick the right one
                            st.warning("Collection was created (202) but not yet visible. Showing all collections — enter the ID manually below.")
                            with st.expander("All collections"):
                                st.write(all_cols)
                    except Exception as e:
                        st.error(str(e))
                    except Exception as e:
                        st.error(str(e))
        with right:
            manual = st.text_input("Or enter an existing collection ID:", key="grnd_manual_id")
            if st.button("Use this ID", key="grnd_use_id") and manual:
                st.session_state.collection_id = manual
                st.rerun()

    # ── Step 2 ──────────────────────────────────────────────────────
    with st.expander("Step 2 — Add Documents", expanded=done1 and not done2):
        if not done1:
            st.warning("Complete Step 1 first.")
        else:
            st.markdown(f"Document content and metadata are {_CONFIG}. Edit before uploading.", unsafe_allow_html=True)

            with st.container(border=True):
                st.markdown("**Document 1**")
                d1_topic   = st.text_input("Topic:", value="BTP", key="d1_topic")
                d1_content = st.text_area("Content:", key="d1_content", height=68,
                    value="SAP BTP provides cloud-native platform services for building enterprise applications.")

            with st.container(border=True):
                st.markdown("**Document 2**")
                d2_topic   = st.text_input("Topic:", value="HANA", key="d2_topic")
                d2_content = st.text_area("Content:", key="d2_content", height=68,
                    value="HANA Vector Store enables semantic search over large document collections using embeddings.")

            if done2:
                st.success("Documents already added.")
            elif st.button("Add Documents", type="primary", key="grnd_add_docs"):
                with st.spinner("Uploading…"):
                    try:
                        from gen_ai_hub.document_grounding.client import VectorAPIClient
                        from gen_ai_hub.document_grounding.models.vector import BaseDocument, DocumentsCreateRequest, TextOnlyBaseChunk, VectorKeyValueListPair
                        VectorAPIClient().create_documents(
                            st.session_state.collection_id,
                            DocumentsCreateRequest(documents=[
                                BaseDocument(
                                    chunks=[TextOnlyBaseChunk(content=d1_content, metadata=[VectorKeyValueListPair(key="language", value=["en"])])],
                                    metadata=[VectorKeyValueListPair(key="topic", value=[d1_topic])],
                                ),
                                BaseDocument(
                                    chunks=[TextOnlyBaseChunk(content=d2_content, metadata=[VectorKeyValueListPair(key="language", value=["en"])])],
                                    metadata=[VectorKeyValueListPair(key="topic", value=[d2_topic])],
                                ),
                            ]),
                        )
                        st.session_state.docs_added = True
                        st.success("Documents added.")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))

    # ── Step 3 ──────────────────────────────────────────────────────
    with st.expander("Step 3 — Semantic Search", expanded=done1 and done2):
        if not (done1 and done2):
            st.warning("Complete Steps 1 and 2 first.")
        else:
            st.markdown(f"Query and max chunks are {_CONFIG}.", unsafe_allow_html=True)
            query      = st.text_input("Query:", value="What are the key features of SAP BTP?", key="grnd_query")
            max_chunks = st.slider("Max chunks:", 1, 10, 3, key="grnd_chunks")

            if st.button("Search", type="primary", key="grnd_search"):
                with st.spinner("Retrieving…"):
                    try:
                        from gen_ai_hub.document_grounding.client import RetrievalAPIClient
                        from gen_ai_hub.document_grounding.models.retrieval import RetrievalSearchConfiguration, RetrievalSearchFilter, RetrievalSearchInput
                        result = RetrievalAPIClient().search(
                            RetrievalSearchInput(
                                query=query,
                                filters=[RetrievalSearchFilter(
                                    id="filter-1",
                                    dataRepositoryType="vector",
                                    dataRepositories=[st.session_state.collection_id],
                                    searchConfiguration=RetrievalSearchConfiguration(maxChunkCount=max_chunks),
                                )],
                            )
                        )
                        # Response: result.results[].results[].dataRepository.documents[].chunks[]
                        with st.expander("Debug — raw response"):
                            st.write(result)

                        st.markdown("**Retrieved chunks:**")
                        found = False
                        for filter_result in result.results:
                            for repo_result in filter_result.results:
                                # SDK uses camelCase: dataRepository
                                repo = (
                                    getattr(repo_result, "dataRepository", None)
                                    or getattr(repo_result, "data_repository", None)
                                )
                                if repo is None:
                                    continue
                                for doc in (getattr(repo, "documents", None) or []):
                                    for chunk in (getattr(doc, "chunks", None) or []):
                                        content = getattr(chunk, "content", None)
                                        if content:
                                            found = True
                                            with st.container(border=True):
                                                st.write(content)
                        if not found:
                            st.info("No chunks returned.")
                            with st.expander("Raw response"):
                                st.write(result)
                    except Exception as e:
                        st.error(str(e))

    st.divider()
    if st.button("Reset state", type="secondary"):
        st.session_state.collection_id = None
        st.session_state.docs_added = False
        st.rerun()


# ══════════════════════════════════════════════════════════════════
# ORCHESTRATION
# ══════════════════════════════════════════════════════════════════
elif page == "Orchestration":
    st.title("Orchestration Service")
    st.markdown("A modular pipeline for enterprise LLM calls. Swap models, inject safety, mask PII, stream — configured in Python.")
    st.divider()

    MODELS = ["gpt-5.4-nano", "gpt-4o", "anthropic--claude-4.6-sonnet", "gemini-3.5-flash"]

    (tab_basic, tab_tmpl, tab_mask, tab_filter,
     tab_stream, tab_tool, tab_fallback, tab_fixed) = st.tabs([
        "Completion", "Template", "Data Masking", "Content Filtering",
        "Streaming", "Tool Calls", "Fallback", "Multimodal & Translation",
    ])

    # ── Completion ─────────────────────────────────────────────────
    with tab_basic:
        st.markdown(f"**Basic Completion** — message {_CONFIG} · model {_CONFIG}", unsafe_allow_html=True)

        model_basic = st.selectbox("Model:", MODELS, key="basic_model")
        question    = st.text_input("Prompt:", value="What is the longest river on planet earth?", key="basic_q")

        if st.button("Run", type="primary", key="basic_run"):
            with st.spinner("Calling LLM…"):
                try:
                    from gen_ai_hub.orchestration_v2 import LLMModelDetails, ModuleConfig, OrchestrationConfig, OrchestrationService, PromptTemplatingModuleConfig, Template, UserMessage
                    svc = OrchestrationService(config=OrchestrationConfig(
                        modules=ModuleConfig(prompt_templating=PromptTemplatingModuleConfig(
                            prompt=Template(template=[UserMessage(content=question)]),
                            model=LLMModelDetails(name=model_basic),
                        ))
                    ))
                    res = svc.run()
                    svc.close_http_connection()
                    with st.chat_message("user"):    st.write(question)
                    with st.chat_message("assistant"): st.write(res.final_result.choices[0].message.content)
                except Exception as e:
                    st.error(str(e))

    # ── Template ───────────────────────────────────────────────────
    with tab_tmpl:
        st.markdown(f"**Prompt Templates** — template {_CONFIG} · placeholder values {_CONFIG} · model {_CONFIG}", unsafe_allow_html=True)
        st.markdown("Use `{{?variable}}` syntax. Placeholders are detected automatically from the template string.")

        template_str = st.text_input("Template:", value="What is the capital of {{?country}}?", key="tmpl_str")
        model_tmpl   = st.selectbox("Model:", MODELS, key="tmpl_model")

        placeholders = re.findall(r"\{\{\?(\w+)\}\}", template_str)
        ph_values = {}
        if placeholders:
            cols = st.columns(min(len(placeholders), 4))
            for i, ph in enumerate(placeholders):
                with cols[i % 4]:
                    ph_values[ph] = st.text_input(f"`{{{{?{ph}}}}}`", value="Denmark", key=f"ph_{ph}")

        if st.button("Run", type="primary", key="tmpl_run"):
            with st.spinner("Calling LLM…"):
                try:
                    from gen_ai_hub.orchestration_v2 import LLMModelDetails, ModuleConfig, OrchestrationConfig, OrchestrationService, PromptTemplatingModuleConfig, Template, UserMessage
                    svc = OrchestrationService(config=OrchestrationConfig(
                        modules=ModuleConfig(prompt_templating=PromptTemplatingModuleConfig(
                            prompt=Template(template=[UserMessage(content=template_str)]),
                            model=LLMModelDetails(name=model_tmpl),
                        ))
                    ))
                    filled = template_str
                    for k, v in ph_values.items():
                        filled = filled.replace(f"{{{{?{k}}}}}", v)
                    st.caption(f"Resolved: *{filled}*")
                    res = svc.run(placeholder_values=ph_values)
                    svc.close_http_connection()
                    with st.chat_message("assistant"):
                        st.write(res.final_result.choices[0].message.content)
                except Exception as e:
                    st.error(str(e))

    # ── Data Masking ───────────────────────────────────────────────
    with tab_mask:
        st.markdown(f"**Data Masking** — input prompt {_CONFIG} · masking method {_CONFIG} · model {_CONFIG}", unsafe_allow_html=True)

        col_mm, col_mo = st.columns([1, 2])
        with col_mm:
            mask_method_label = st.selectbox(
                "Masking method:",
                ["Anonymization", "Pseudonymization"],
                key="mask_method",
                help="Anonymization: replaces with generic tokens ([PERSON_1]).\nPseudonymization: replaces with consistent fake data (looks real, but isn't).",
            )
        with col_mo:
            model_mask = st.selectbox("Model:", MODELS, key="mask_model")

        pii_text = st.text_area(
            "Input (may contain PII):",
            height=80,
            key="mask_input",
            value=(
                "List all personal details from this text: "
                "Jane Doe, born 1975-03-05, living at 10 Downing Street, London UK, "
                "email jane.doe@mailprovider.com, phone +4902044123221."
            ),
        )

        anon_preview = (
            pii_text
            .replace("Jane Doe",                    "[PERSON_1]")
            .replace("1975-03-05",                  "MASKED_DATE")
            .replace("10 Downing Street, London UK", "[ADDRESS_1]")
            .replace("jane.doe@mailprovider.com",   "[EMAIL_1]")
            .replace("+4902044123221",              "[PHONE_1]")
        )
        pseudo_preview = (
            pii_text
            .replace("Jane Doe",                    "Maria Schmidt")
            .replace("1975-03-05",                  "MASKED_DATE")
            .replace("10 Downing Street, London UK", "5 Oak Avenue, Berlin DE")
            .replace("jane.doe@mailprovider.com",   "m.schmidt@example.de")
            .replace("+4902044123221",              "+493012345678")
        )

        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown("**Original** — what you send")
            st.code(pii_text, language=None)
        with col_r:
            st.markdown(f"**After {mask_method_label}** — what the LLM sees")
            st.code(anon_preview if mask_method_label == "Anonymization" else pseudo_preview, language=None)

        if mask_method_label == "Pseudonymization":
            st.caption("Pseudonymization creates consistent fake data — the LLM response will look real but contain different (fictional) values.")
        else:
            st.caption("Anonymization replaces PII with generic tokens — the LLM response will clearly show [PERSON_1], [EMAIL_1] etc.")

        if st.button("Run with Masking", type="primary", key="mask_run"):
            with st.spinner("Masking PII then calling LLM…"):
                try:
                    from gen_ai_hub.orchestration_v2 import (
                        DPICustomEntity, DPIMethodConstant, DPIStandardEntity, LLMModelDetails,
                        MaskingMethod, MaskingModuleConfig, MaskingProviderConfig, ModuleConfig,
                        OrchestrationConfig, OrchestrationService, ProfileEntity,
                        PromptTemplatingModuleConfig, Template, UserMessage,
                    )
                    method = MaskingMethod.ANONYMIZATION if mask_method_label == "Anonymization" else MaskingMethod.PSEUDONYMIZATION
                    svc = OrchestrationService(config=OrchestrationConfig(
                        modules=ModuleConfig(
                            prompt_templating=PromptTemplatingModuleConfig(
                                prompt=Template(template=[UserMessage(content=pii_text)]),
                                model=LLMModelDetails(name=model_mask),
                            ),
                            masking=MaskingModuleConfig(providers=[MaskingProviderConfig(
                                method=method,
                                entities=[
                                    DPIStandardEntity(type=ProfileEntity.ADDRESS),
                                    DPIStandardEntity(type=ProfileEntity.EMAIL),
                                    DPIStandardEntity(type=ProfileEntity.PHONE),
                                    DPIStandardEntity(type=ProfileEntity.PERSON),
                                    DPICustomEntity(regex=r"[0-9]{4}[-/][0-9]{2}[-/][0-9]{2}", replacement_strategy=DPIMethodConstant(value="MASKED_DATE")),
                                ],
                            )]),
                        )
                    ))
                    res = svc.run()
                    svc.close_http_connection()
                    st.markdown("**LLM response** *(original PII was never sent to the model)*")
                    with st.chat_message("assistant"):
                        st.write(res.final_result.choices[0].message.content)
                except Exception as e:
                    st.error(str(e))

    # ── Content Filtering ──────────────────────────────────────────
    with tab_filter:
        st.markdown(f"**Content Filtering** — test prompt {_CONFIG}", unsafe_allow_html=True)

        col_a, col_b = st.columns(2)
        with col_a:
            with st.container(border=True):
                st.markdown("**Input filter** — LlamaGuard (privacy)")
                in_prompt = st.text_area("Prompt:", value="My social insurance number is ABC123456789.", height=68, key="flt_in")
                if st.button("Test input filter", type="primary", key="flt_in_run"):
                    with st.spinner("Running…"):
                        try:
                            from gen_ai_hub.orchestration_v2 import (
                                FilteringModuleConfig, InputFiltering, LlamaGuard38bFilter,
                                LlamaGuard38bFilterConfig, LLMModelDetails, ModuleConfig,
                                OrchestrationConfig, OrchestrationError, OrchestrationService,
                                PromptTemplatingModuleConfig, Template, UserMessage,
                            )
                            svc = OrchestrationService(config=OrchestrationConfig(
                                modules=ModuleConfig(
                                    prompt_templating=PromptTemplatingModuleConfig(
                                        prompt=Template(template=[UserMessage(content=in_prompt)]),
                                        model=LLMModelDetails(name="gpt-5.4-nano"),
                                    ),
                                    filtering=FilteringModuleConfig(input=InputFiltering(filters=[
                                        LlamaGuard38bFilterConfig(config=LlamaGuard38bFilter(privacy=True))
                                    ])),
                                )
                            ))
                            raw_in = None
                            blocked = False
                            try:
                                raw_in = svc.run()
                                st.warning("Not filtered — prompt may be safe.")
                            except OrchestrationError as e:
                                if e.code == 400:
                                    st.success("Blocked — input violated the privacy policy.")
                                    blocked = True
                                else:
                                    raise
                                with st.expander("Raw response"):
                                    st.code(str(e), language=None)
                            finally:
                                svc.close_http_connection()
                            if raw_in is not None:
                                with st.expander("Raw response"):
                                    st.code(repr(raw_in), language=None)
                        except Exception as e:
                            st.error(str(e))

        with col_b:
            with st.container(border=True):
                st.markdown("**Output filter** — Azure Content Safety")
                out_prompt = st.text_area("Prompt:", value="Reparaphrase the sentence in 30 ways with strong feelings: 'I hate you!'.", height=68, key="flt_out")
                if st.button("Test output filter", type="primary", key="flt_out_run"):
                    with st.spinner("Running…"):
                        try:
                            from gen_ai_hub.orchestration_v2 import (
                                AzureContentSafetyOutput, AzureContentSafetyOutputFilterConfig,
                                AzureThreshold, FilteringModuleConfig, LLMModelDetails,
                                ModuleConfig, OrchestrationConfig, OrchestrationService,
                                OutputFiltering, PromptTemplatingModuleConfig, Template, UserMessage,
                            )
                            svc = OrchestrationService(config=OrchestrationConfig(
                                modules=ModuleConfig(
                                    prompt_templating=PromptTemplatingModuleConfig(
                                        prompt=Template(template=[UserMessage(content=out_prompt)]),
                                        model=LLMModelDetails(name="gpt-5.4-nano"),
                                    ),
                                    filtering=FilteringModuleConfig(output=OutputFiltering(filters=[
                                        AzureContentSafetyOutputFilterConfig(config=AzureContentSafetyOutput(
                                            hate=AzureThreshold.ALLOW_SAFE, violence=AzureThreshold.ALLOW_SAFE,
                                        ))
                                    ])),
                                )
                            ))
                            res = svc.run()
                            svc.close_http_connection()
                            if not res.final_result.choices[0].message.content:
                                st.success("Suppressed — output violated the content safety policy.")
                            else:
                                st.warning("Output was not filtered.")
                                with st.chat_message("assistant"):
                                    st.write(res.final_result.choices[0].message.content)
                            with st.expander("Raw response"):
                                st.code(repr(res), language=None)
                        except Exception as e:
                            st.error(str(e))
                            with st.expander("Raw error"):
                                st.code(str(e), language=None)

    # ── Streaming ──────────────────────────────────────────────────
    with tab_stream:
        st.markdown(f"**Streaming** — message {_CONFIG} · model {_CONFIG}", unsafe_allow_html=True)

        model_stream = st.selectbox("Model:", MODELS, key="stream_model")
        stream_q     = st.text_input("Prompt:", value="Explain SAP BTP in 3 sentences.", key="stream_q")

        if st.button("Run (streaming)", type="primary", key="stream_run"):
            try:
                from gen_ai_hub.orchestration_v2 import (
                    GlobalStreamOptions, LLMModelDetails, ModuleConfig, OrchestrationConfig,
                    OrchestrationService, PromptTemplatingModuleConfig, Template, UserMessage,
                )
                svc = OrchestrationService(config=OrchestrationConfig(
                    modules=ModuleConfig(prompt_templating=PromptTemplatingModuleConfig(
                        prompt=Template(template=[UserMessage(content=stream_q)]),
                        model=LLMModelDetails(name=model_stream),
                    )),
                    stream=GlobalStreamOptions(enabled=True),
                ))
                with st.chat_message("assistant"):
                    placeholder = st.empty()
                    full = ""
                    for chunk in svc.stream():
                        if chunk.final_result:
                            token = chunk.final_result.choices[0].delta.content
                            if token:
                                full += token
                                placeholder.markdown(full + "▌")
                    placeholder.markdown(full)
                svc.close_http_connection()
            except Exception as e:
                st.error(str(e))

    # ── Tool Calls ─────────────────────────────────────────────────
    with tab_tool:
        st.markdown(f"**Tool Calls** — operands a and b {_CONFIG}", unsafe_allow_html=True)
        st.markdown("The LLM decides when to invoke `add(a, b)` and uses the result to answer.")

        st.code("@function_tool\ndef add(x: int, y: int) -> int:\n    \"\"\"Add two numbers.\"\"\"\n    return x + y", language="python")

        c1, c2 = st.columns(2)
        with c1: num_a = st.number_input("a:", value=279, step=1, key="tool_a")
        with c2: num_b = st.number_input("b:", value=929, step=1, key="tool_b")

        if st.button("Run tool call", type="primary", key="tool_run"):
            with st.spinner("Running…"):
                try:
                    from gen_ai_hub.orchestration_v2 import (
                        LLMModelDetails, ModuleConfig, OrchestrationConfig, OrchestrationService,
                        PromptTemplatingModuleConfig, SystemMessage, Template, ToolChatMessage,
                        UserMessage, function_tool,
                    )

                    @function_tool
                    def add(x: int, y: int) -> int:
                        """Add two numbers."""
                        return x + y

                    question_tool = f"What is {int(num_a)} + {int(num_b)}?"
                    config = OrchestrationConfig(modules=ModuleConfig(prompt_templating=PromptTemplatingModuleConfig(
                        prompt=Template(template=[
                            SystemMessage(content="You are a helpful AI that performs addition."),
                            UserMessage(content=question_tool),
                        ], tools=[add]),
                        model=LLMModelDetails(name="gpt-4o"),
                    )))
                    svc = OrchestrationService()
                    res = svc.run(config=config)
                    tool_calls = res.final_result.choices[0].message.tool_calls
                    if not tool_calls:
                        st.warning("No tool call was made.")
                    else:
                        history = list(res.intermediate_results.templating or [])
                        history.append(res.final_result.choices[0].message)
                        for tc in tool_calls:
                            val = add.execute(**tc.function.parse_arguments())
                            history.append(ToolChatMessage(content=str(val), tool_call_id=tc.id))
                            st.caption(f"Tool called: `{tc.function.name}({tc.function.arguments})` → `{val}`")
                        final = svc.run(config=config, history=history)
                        svc.close_http_connection()
                        with st.chat_message("user"):      st.write(question_tool)
                        with st.chat_message("assistant"): st.write(final.final_result.choices[0].message.content)
                except Exception as e:
                    st.error(str(e))

    # ── Fallback ───────────────────────────────────────────────────
    with tab_fallback:
        st.markdown(f"**Fallback** — primary model {_CONFIG} · fallback model {_CONFIG} · message {_CONFIG}", unsafe_allow_html=True)
        st.markdown("If the primary model fails, the service automatically retries with the fallback.")

        fallback_q = st.text_input("Prompt:", value="What is the longest river on planet earth?", key="fallback_q")
        c1, c2 = st.columns(2)
        with c1: primary_model  = st.text_input("Primary model (will fail):", value="dummy-model", key="fb_primary")
        with c2: fallback_model = st.selectbox("Fallback model:", MODELS, index=2, key="fb_fallback")

        if st.button("Run with fallback", type="primary", key="fallback_run"):
            with st.spinner(f"Trying `{primary_model}` → then `{fallback_model}`…"):
                try:
                    from gen_ai_hub.orchestration_v2 import LLMModelDetails, ModuleConfig, OrchestrationConfig, OrchestrationService, PromptTemplatingModuleConfig, Template, UserMessage
                    svc = OrchestrationService(config=OrchestrationConfig(modules=[
                        ModuleConfig(prompt_templating=PromptTemplatingModuleConfig(
                            prompt=Template(template=[UserMessage(content=fallback_q)]),
                            model=LLMModelDetails(name=primary_model),
                        )),
                        ModuleConfig(prompt_templating=PromptTemplatingModuleConfig(
                            prompt=Template(template=[UserMessage(content=fallback_q)]),
                            model=LLMModelDetails(name=fallback_model),
                        )),
                    ]))
                    res = svc.run()
                    svc.close_http_connection()
                    st.success(f"Fallback triggered — response from `{fallback_model}`")
                    with st.chat_message("assistant"):
                        st.write(res.final_result.choices[0].message.content)
                except Exception as e:
                    st.error(str(e))

    # ── Fixed Demos ────────────────────────────────────────────────
    with tab_fixed:
        st.subheader("Multimodal — Image Input")
        st.markdown(f"Model {_CONFIG} · image URL {_CONFIG} · question {_CONFIG}", unsafe_allow_html=True)

        img_model = st.selectbox("Model:", ["gpt-5.4-nano", "gpt-4o"], key="img_model")
        img_url   = st.text_input("Image URL:", value="https://picsum.photos/id/1/200/300", key="img_url")
        img_q     = st.text_input("Question:", value="What objects are prominent in this image?", key="img_q")

        if img_url:
            try:
                st.image(img_url, width=240, caption="Preview")
            except Exception:
                st.caption("(Could not preview image)")

        if st.button("Run image completion", type="primary", key="img_run"):
            with st.spinner("Calling LLM with image…"):
                try:
                    from gen_ai_hub.orchestration_v2 import (
                        ImageItem, LLMModelDetails, ModuleConfig, OrchestrationConfig,
                        OrchestrationService, PromptTemplatingModuleConfig, Template, UserMessage,
                    )
                    image = ImageItem(url=img_url)
                    svc = OrchestrationService(config=OrchestrationConfig(
                        modules=ModuleConfig(prompt_templating=PromptTemplatingModuleConfig(
                            prompt=Template(template=[UserMessage(content=[image, img_q])]),
                            model=LLMModelDetails(name=img_model),
                        ))
                    ))
                    res = svc.run()
                    svc.close_http_connection()
                    with st.chat_message("assistant"):
                        st.write(res.final_result.choices[0].message.content)
                except Exception as e:
                    st.error(str(e))

        st.markdown("---")
        st.subheader("Translation")
        st.markdown(f"Input and output are each translated independently. Language codes {_CONFIG} · prompt {_CONFIG}", unsafe_allow_html=True)

        LANG_CODES = ["en-US", "de-DE", "fr-FR", "es-ES", "ja-JP", "zh-CN", "pt-BR", "it-IT", "ko-KR", "nl-NL"]

        trans_q = st.text_input("Prompt (in source language):", value="What is the longest river on planet earth?", key="trans_q")
        trans_model = st.selectbox("Model:", MODELS, key="trans_model")

        col_ti, col_to = st.columns(2)
        with col_ti:
            st.markdown("**Input translation** (user → model)")
            in_src = st.selectbox("Source language:", LANG_CODES, index=0, key="in_src")
            in_tgt = st.selectbox("Target language:", LANG_CODES, index=1, key="in_tgt")
        with col_to:
            st.markdown("**Output translation** (model → user)")
            out_src = st.selectbox("Source language:", LANG_CODES, index=1, key="out_src")
            out_tgt = st.selectbox("Target language:", LANG_CODES, index=2, key="out_tgt")

        if st.button("Run translation", type="primary", key="trans_run"):
            with st.spinner("Calling LLM with translation…"):
                try:
                    from gen_ai_hub.orchestration_v2 import (
                        InputTranslationConfig, LLMModelDetails, ModuleConfig, OrchestrationConfig,
                        OrchestrationService, OutputTranslationConfig, PromptTemplatingModuleConfig,
                        SAPDocumentTranslationInput, SAPDocumentTranslationOutput, Template,
                        TranslationModuleConfig, UserMessage,
                    )
                    svc = OrchestrationService(config=OrchestrationConfig(
                        modules=ModuleConfig(
                            prompt_templating=PromptTemplatingModuleConfig(
                                prompt=Template(template=[UserMessage(content=trans_q)]),
                                model=LLMModelDetails(name=trans_model),
                            ),
                            translation=TranslationModuleConfig(
                                input=SAPDocumentTranslationInput(
                                    config=InputTranslationConfig(source_language=in_src, target_language=in_tgt)
                                ),
                                output=SAPDocumentTranslationOutput(
                                    config=OutputTranslationConfig(source_language=out_src, target_language=out_tgt)
                                ),
                            ),
                        )
                    ))
                    res = svc.run()
                    svc.close_http_connection()
                    st.caption(f"Pipeline: prompt `{in_src}` → translated to `{in_tgt}` for LLM → LLM responds in `{out_src}` → translated to `{out_tgt}`")
                    with st.chat_message("assistant"):
                        st.write(res.final_result.choices[0].message.content)
                except Exception as e:
                    st.error(str(e))
