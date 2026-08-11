import streamlit as st
import requests


# ============================================================
# CONFIG
# ============================================================

BACKEND_URL = "http://127.0.0.1:8000"


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Multi-Agent Research Assistant",
    page_icon="🔬",
    layout="wide"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.html(
    """
    <style>

    /* =====================================================
       APP
       ===================================================== */

    .stApp {
        background-color: #0e1117;
    }


    /* =====================================================
       SIDEBAR
       ===================================================== */

    section[data-testid="stSidebar"] {
        background-color: #20252d;
    }


    /* =====================================================
       HEADER
       ===================================================== */

    .main-title {
        font-size: 34px;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 5px;
    }

    .subtitle {
        color: #9ca3af;
        font-size: 15px;
        margin-bottom: 20px;
    }


    /* =====================================================
       CARDS
       ===================================================== */

    .info-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 18px;
        margin-bottom: 15px;
        color: #ffffff;
    }

    .answer-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 20px;
        margin-top: 10px;
        color: #ffffff;
    }


    /* =====================================================
       EVALUATION
       ===================================================== */

    .evaluation-card {
        background-color: #11161d;
        border: 1px solid #30363d;
        border-radius: 14px;
        padding: 20px;
        margin-top: 15px;
        margin-bottom: 15px;
    }

    .evaluation-title {
        font-size: 21px;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 5px;
    }

    .evaluation-subtitle {
        color: #8b949e;
        font-size: 13px;
        margin-bottom: 18px;
    }

    .evaluation-label {
        color: #8b949e;
        font-size: 12px;
    }

    .evaluation-value {
        color: #ffffff;
        font-size: 22px;
        font-weight: 700;
    }

    .evaluation-success {
        color: #3fb950;
        font-weight: 600;
    }

    .evaluation-warning {
        color: #d29922;
        font-weight: 600;
    }

    .evaluation-danger {
        color: #f85149;
        font-weight: 600;
    }

    .feedback-card {
        background-color: #161b22;
        border-left: 3px solid #58a6ff;
        border-radius: 8px;
        padding: 14px;
        margin-top: 12px;
        color: #c9d1d9;
    }

    </style>
    """
)


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "documents" not in st.session_state:
    st.session_state.documents = []


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def safe_score(value, default=0):
    """
    Safely convert evaluation score to displayable value.
    """
    if value is None:
        return default

    return value


def render_sources(sources):
    """
    Render research sources.
    """

    if not sources:
        return

    with st.expander("📚 Sources", expanded=False):

        for index, source in enumerate(sources, start=1):

            source_name = source.get(
                "source",
                "Unknown source"
            )

            page = source.get("page")
            chunk = source.get("chunk")

            st.markdown(
                f"**{index}. {source_name}**"
            )

            details = []

            if page is not None:
                details.append(f"Page {page}")

            if chunk is not None:
                details.append(f"Chunk {chunk}")

            if details:
                st.caption(" • ".join(details))

            if index < len(sources):
                st.divider()


def render_evaluation(evaluation, expanded=False):
    """
    Render complete critic evaluation.
    """

    if not evaluation:
        st.info(
            "No evaluation data was returned by the Critic agent."
        )
        return


    # ========================================================
    # MAIN EVALUATION CARD
    # ========================================================

    with st.expander(
        "📊 Research Evaluation",
        expanded=expanded
    ):

        st.markdown(
            "### 📊 Critic Evaluation"
        )

        st.caption(
            "Quality assessment generated by the Critic agent."
        )


        # ====================================================
        # CORE SCORES
        # ====================================================

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "Correctness",
                f"{safe_score(evaluation.get('correctness'))}/5"
            )

        with col2:

            st.metric(
                "Completeness",
                f"{safe_score(evaluation.get('completeness'))}/5"
            )

        with col3:

            st.metric(
                "Clarity",
                f"{safe_score(evaluation.get('clarity'))}/5"
            )

        with col4:

            st.metric(
                "Overall",
                f"{safe_score(evaluation.get('overall'))}/5"
            )


        st.divider()


        # ====================================================
        # QUALITY / GROUNDING
        # ====================================================

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            grounded = evaluation.get(
                "groundedness",
                False
            )

            st.metric(
                "Groundedness",
                "✓ Yes" if grounded else "✗ No"
            )

        with col2:

            passed = evaluation.get(
                "passed",
                False
            )

            st.metric(
                "Critic Status",
                "✓ Passed" if passed else "✗ Failed"
            )

        with col3:

            revision_count = evaluation.get(
                "revision_count",
                0
            )

            st.metric(
                "Revisions",
                revision_count
            )

        with col4:

            critic_passes = evaluation.get(
                "critic_passes",
                0
            )

            st.metric(
                "Critic Passes",
                critic_passes
            )


        # ====================================================
        # EXTRA STATS
        # ====================================================

        critic_failures = evaluation.get(
            "critic_failures",
            0
        )

        if (
            critic_failures
            or "critic_failures" in evaluation
        ):

            st.divider()

            col1, col2 = st.columns(2)

            with col1:

                st.metric(
                    "Critic Failures",
                    critic_failures
                )

            with col2:

                # Calculate score percentage
                scores = [
                    evaluation.get("correctness"),
                    evaluation.get("completeness"),
                    evaluation.get("clarity"),
                    evaluation.get("overall")
                ]

                valid_scores = [
                    x for x in scores
                    if isinstance(x, (int, float))
                ]

                if valid_scores:

                    percentage = (
                        sum(valid_scores)
                        / (len(valid_scores) * 5)
                    ) * 100

                    st.metric(
                        "Quality Score",
                        f"{percentage:.0f}%"
                    )


        # ====================================================
        # FEEDBACK
        # ====================================================

        feedback = evaluation.get(
            "feedback",
            ""
        )

        if feedback:

            st.divider()

            st.markdown(
                "#### 💬 Critic Feedback"
            )

            st.info(
                feedback
            )


        # ====================================================
        # REVISION REQUEST
        # ====================================================

        revision_request = evaluation.get(
            "revision_request",
            ""
        )

        if revision_request:

            st.markdown(
                "#### 🔄 Revision Request"
            )

            st.warning(
                revision_request
            )


        # ====================================================
        # ADDITIONAL EVALUATION FIELDS
        # ====================================================

        known_fields = {
            "correctness",
            "completeness",
            "clarity",
            "overall",
            "groundedness",
            "passed",
            "feedback",
            "revision_request",
            "revision_count",
            "critic_passes",
            "critic_failures"
        }

        additional_fields = {
            key: value
            for key, value in evaluation.items()
            if key not in known_fields
            and value not in [None, "", [], {}]
        }

        if additional_fields:

            st.divider()

            st.markdown(
                "#### 📋 Additional Evaluation Details"
            )

            for key, value in additional_fields.items():

                label = key.replace(
                    "_",
                    " "
                ).title()

                st.write(
                    f"**{label}:** {value}"
                )


def render_answer_message(message):
    """
    Render an assistant response.
    """

    answer = message.get(
        "content",
        ""
    )

    if answer:
        st.markdown(answer)

    render_sources(
        message.get(
            "sources",
            []
        )
    )

    render_evaluation(
        message.get(
            "evaluation",
            {}
        )
    )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        "## Multi-Agent Research Assistant"
    )

    st.caption(
        "LangGraph powered research assistant"
    )

    st.divider()


    # ========================================================
    # STACK
    # ========================================================

    st.markdown(
        "### Stack"
    )

    st.markdown(
        """
        **Graph:** LangGraph  
        **Backend:** FastAPI  
        **LLM:** Groq  
        **Embeddings:** Sentence Transformers  
        **Vector Store:** ChromaDB
        """
    )


    st.divider()


    # ========================================================
    # COLLECTIONS
    # ========================================================

    st.markdown(
        "### Collections"
    )

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Documents",
            len(
                st.session_state.documents
            )
        )

    with col2:

        st.metric(
            "Messages",
            len(
                st.session_state.messages
            )
        )


    st.divider()


    # ========================================================
    # SESSION
    # ========================================================

    st.markdown(
        "### Session"
    )

    if st.button(
        "Clear Chat",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.rerun()


# ============================================================
# MAIN HEADER
# ============================================================

st.markdown(
    """
    <div class="main-title">
        Multi-Agent Research Assistant
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="subtitle">
        Research, retrieve, write and evaluate answers
        over your document library
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# TABS
# ============================================================

tab_ask, tab_library, tab_evaluate, tab_memory = st.tabs(
    [
        "💬 Ask",
        "📚 Library",
        "📊 Evaluate",
        "🧠 Memory"
    ]
)


# ============================================================
# ASK TAB
# ============================================================

with tab_ask:

    st.markdown(
        "### Ask a Research Question"
    )

    st.caption(
        "Ask questions based on the documents available "
        "in your research library."
    )


    # ========================================================
    # PREVIOUS CONVERSATION
    # ========================================================

    for message in st.session_state.messages:

        if message["role"] == "user":

            with st.chat_message("user"):

                st.write(
                    message["content"]
                )

        else:

            with st.chat_message("assistant"):

                render_answer_message(
                    message
                )


    # ========================================================
    # QUESTION INPUT
    # ========================================================

    question = st.chat_input(
        "Ask a question about your documents..."
    )


    if question:

        # ====================================================
        # SAVE USER QUESTION
        # ====================================================

        st.session_state.messages.append(
            {
                "role": "user",
                "content": question
            }
        )


        # ====================================================
        # SHOW USER QUESTION
        # ====================================================

        with st.chat_message("user"):

            st.write(
                question
            )


        # ====================================================
        # CALL BACKEND
        # ====================================================

        with st.chat_message("assistant"):

            with st.spinner(
                "Researching your question..."
            ):

                try:

                    response = requests.post(
                        f"{BACKEND_URL}/research",
                        json={
                            "question": question
                        },
                        timeout=300
                    )


                    # ========================================
                    # SUCCESS
                    # ========================================

                    if response.status_code == 200:

                        data = response.json()


                        answer = data.get(
                            "answer",
                            "No answer generated."
                        )

                        sources = data.get(
                            "sources",
                            []
                        )

                        evaluation = data.get(
                            "evaluation",
                            {}
                        )


                        # ====================================
                        # ANSWER
                        # ====================================

                        st.markdown(
                            answer
                        )


                        # ====================================
                        # SOURCES
                        # ====================================

                        render_sources(
                            sources
                        )


                        # ====================================
                        # EVALUATION
                        # ====================================

                        render_evaluation(
                            evaluation,
                            expanded=True
                        )


                        # ====================================
                        # SAVE RESPONSE
                        # ====================================

                        st.session_state.messages.append(
                            {
                                "role": "assistant",
                                "content": answer,
                                "sources": sources,
                                "evaluation": evaluation
                            }
                        )


                    # ========================================
                    # BACKEND ERROR
                    # ========================================

                    else:

                        st.error(
                            f"Research request failed "
                            f"({response.status_code})."
                        )

                        try:

                            error_data = response.json()

                            detail = error_data.get(
                                "detail",
                                "The research request failed."
                            )

                            st.warning(
                                detail
                            )

                        except Exception:

                            st.warning(
                                "Check the FastAPI terminal "
                                "for the detailed error."
                            )


                # ============================================
                # TIMEOUT
                # ============================================

                except requests.exceptions.Timeout:

                    st.error(
                        "Research request timed out."
                    )

                    st.info(
                        "The research workflow is taking "
                        "longer than expected."
                    )


                # ============================================
                # CONNECTION ERROR
                # ============================================

                except requests.exceptions.ConnectionError:

                    st.error(
                        "Could not connect to FastAPI backend."
                    )

                    st.info(
                        "Make sure FastAPI is running on "
                        "http://127.0.0.1:8000"
                    )


                # ============================================
                # UNKNOWN ERROR
                # ============================================

                except Exception:

                    st.error(
                        "Something went wrong while "
                        "processing the research request."
                    )

                    st.info(
                        "Check the FastAPI terminal "
                        "for the detailed error."
                    )


# ============================================================
# LIBRARY TAB
# ============================================================

with tab_library:

    st.markdown(
        "### 📚 Document Library"
    )

    st.caption(
        "Upload research papers and documents "
        "to your workspace."
    )


    # ========================================================
    # PDF UPLOAD
    # ========================================================

    uploaded_file = st.file_uploader(
        "Upload PDF",
        type=["pdf"],
        help="Upload a research paper or PDF document."
    )


    if uploaded_file is not None:

        st.markdown(
            f"**Selected:** `{uploaded_file.name}`"
        )


        if st.button(
            "⬆️ Upload to Library",
            use_container_width=True
        ):

            with st.spinner(
                "Uploading PDF..."
            ):

                try:

                    files = {
                        "file": (
                            uploaded_file.name,
                            uploaded_file.getvalue(),
                            "application/pdf"
                        )
                    }


                    response = requests.post(
                        f"{BACKEND_URL}/upload",
                        files=files,
                        timeout=120
                    )


                    if response.status_code == 200:

                        data = response.json()

                        filename = data.get(
                            "filename",
                            uploaded_file.name
                        )


                        if filename not in (
                            st.session_state.documents
                        ):

                            st.session_state.documents.append(
                                filename
                            )


                        st.success(
                            f"'{filename}' uploaded successfully."
                        )


                    else:

                        st.error(
                            f"Upload failed "
                            f"({response.status_code})."
                        )

                        st.warning(
                            "Check the FastAPI terminal "
                            "for details."
                        )


                except requests.exceptions.ConnectionError:

                    st.error(
                        "Could not connect to FastAPI backend."
                    )


                except requests.exceptions.Timeout:

                    st.error(
                        "Upload request timed out."
                    )


                except Exception:

                    st.error(
                        "Upload failed. "
                        "Check the FastAPI terminal."
                    )


    st.divider()


    # ========================================================
    # DOCUMENT LIST
    # ========================================================

    st.markdown(
        "### Documents"
    )


    if not st.session_state.documents:

        st.info(
            "No documents uploaded in this session."
        )


    else:

        for index, document in enumerate(
            st.session_state.documents,
            start=1
        ):

            st.html(
                f"""
                <div class="info-card">
                    📄 <b>{index}. {document}</b>
                </div>
                """
            )


# ============================================================
# EVALUATE TAB
# ============================================================

with tab_evaluate:

    st.markdown(
        "### 📊 Research Evaluation"
    )

    st.caption(
        "Complete quality evaluation generated by "
        "the Critic agent."
    )


    # ========================================================
    # NO QUESTIONS
    # ========================================================

    if not st.session_state.messages:

        st.info(
            "No research questions have been evaluated yet."
        )


    else:

        assistant_messages = [
            message
            for message in st.session_state.messages
            if message["role"] == "assistant"
        ]


        if not assistant_messages:

            st.info(
                "No evaluation results available."
            )


        else:

            evaluation_count = 0


            for index, message in enumerate(
                assistant_messages,
                start=1
            ):

                evaluation = message.get(
                    "evaluation",
                    {}
                )


                if not evaluation:
                    continue


                evaluation_count += 1


                st.markdown(
                    f"### Question {evaluation_count}"
                )


                # ============================================
                # QUESTION
                # ============================================

                question_number = 0

                for m in st.session_state.messages:

                    if m["role"] == "user":

                        question_number += 1

                    if m is message:

                        break


                if question_number:

                    # Find matching user question
                    user_questions = [
                        m["content"]
                        for m in st.session_state.messages
                        if m["role"] == "user"
                    ]

                    if (
                        evaluation_count
                        <= len(user_questions)
                    ):

                        st.info(
                            user_questions[
                                evaluation_count - 1
                            ]
                        )


                # ============================================
                # CORE SCORE ROW
                # ============================================

                col1, col2, col3, col4 = st.columns(4)

                with col1:

                    st.metric(
                        "Correctness",
                        f"{safe_score(evaluation.get('correctness'))}/5"
                    )

                with col2:

                    st.metric(
                        "Completeness",
                        f"{safe_score(evaluation.get('completeness'))}/5"
                    )

                with col3:

                    st.metric(
                        "Clarity",
                        f"{safe_score(evaluation.get('clarity'))}/5"
                    )

                with col4:

                    st.metric(
                        "Overall",
                        f"{safe_score(evaluation.get('overall'))}/5"
                    )


                # ============================================
                # SECOND STATS ROW
                # ============================================

                col1, col2, col3, col4 = st.columns(4)

                with col1:

                    st.metric(
                        "Groundedness",
                        "✓ Yes"
                        if evaluation.get(
                            "groundedness",
                            False
                        )
                        else "✗ No"
                    )

                with col2:

                    st.metric(
                        "Critic Status",
                        "✓ Passed"
                        if evaluation.get(
                            "passed",
                            False
                        )
                        else "✗ Failed"
                    )

                with col3:

                    st.metric(
                        "Revisions",
                        evaluation.get(
                            "revision_count",
                            0
                        )
                    )

                with col4:

                    st.metric(
                        "Critic Passes",
                        evaluation.get(
                            "critic_passes",
                            0
                        )
                    )


                # ============================================
                # QUALITY PERCENTAGE
                # ============================================

                scores = [
                    evaluation.get("correctness"),
                    evaluation.get("completeness"),
                    evaluation.get("clarity"),
                    evaluation.get("overall")
                ]

                valid_scores = [
                    score
                    for score in scores
                    if isinstance(
                        score,
                        (int, float)
                    )
                ]


                if valid_scores:

                    quality_percentage = (
                        sum(valid_scores)
                        / (
                            len(valid_scores)
                            * 5
                        )
                    ) * 100


                    st.progress(
                        min(
                            max(
                                quality_percentage / 100,
                                0
                            ),
                            1
                        )
                    )

                    st.caption(
                        f"Overall Quality Score: "
                        f"{quality_percentage:.0f}%"
                    )


                # ============================================
                # FEEDBACK
                # ============================================

                feedback = evaluation.get(
                    "feedback",
                    ""
                )


                if feedback:

                    st.markdown(
                        "#### 💬 Critic Feedback"
                    )

                    st.info(
                        feedback
                    )


                # ============================================
                # REVISION REQUEST
                # ============================================

                revision_request = evaluation.get(
                    "revision_request",
                    ""
                )


                if revision_request:

                    st.markdown(
                        "#### 🔄 Revision Request"
                    )

                    st.warning(
                        revision_request
                    )


                # ============================================
                # ADDITIONAL FIELDS
                # ============================================

                known_fields = {
                    "correctness",
                    "completeness",
                    "clarity",
                    "overall",
                    "groundedness",
                    "passed",
                    "feedback",
                    "revision_request",
                    "revision_count",
                    "critic_passes",
                    "critic_failures"
                }


                extra = {
                    key: value
                    for key, value in evaluation.items()
                    if key not in known_fields
                    and value not in [
                        None,
                        "",
                        [],
                        {}
                    ]
                }


                if extra:

                    st.markdown(
                        "#### 📋 Additional Metrics"
                    )

                    for key, value in extra.items():

                        label = key.replace(
                            "_",
                            " "
                        ).title()

                        st.write(
                            f"**{label}:** {value}"
                        )


                st.divider()


# ============================================================
# MEMORY TAB
# ============================================================

with tab_memory:

    st.markdown(
        "### 🧠 Research Memory"
    )

    st.info(
        "Memory is maintained by the backend "
        "research workflow."
    )


    st.markdown(
        "#### Questions asked in this session"
    )


    user_questions = [
        message["content"]
        for message in st.session_state.messages
        if message["role"] == "user"
    ]


    if not user_questions:

        st.write(
            "No questions asked yet."
        )


    else:

        for index, question in enumerate(
            user_questions,
            start=1
        ):

            st.markdown(
                f"**{index}.** {question}"
            )