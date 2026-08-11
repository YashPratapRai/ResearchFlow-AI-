import streamlit as st


def display_sources(sources):
    st.subheader("📚 Sources")

    if not sources:
        st.info("No sources found.")
        return

    # Remove duplicate sources
    seen = set()

    for source in sources:
        name = source.get("source", "Unknown source")
        page = source.get("page", "N/A")
        chunk = source.get("chunk", "N/A")

        key = (name, page, chunk)

        if key in seen:
            continue

        seen.add(key)

        st.markdown(
            f"""
            **{name}**

            - Page: `{page}`
            - Chunk: `{chunk}`
            """
        )


def display_evaluation(evaluation):
    st.subheader("📊 Evaluation")

    if not evaluation:
        st.info("No evaluation available.")
        return

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Correctness",
            f"{evaluation.get('correctness', 0)}/5"
        )

    with col2:
        st.metric(
            "Completeness",
            f"{evaluation.get('completeness', 0)}/5"
        )

    with col3:
        st.metric(
            "Clarity",
            f"{evaluation.get('clarity', 0)}/5"
        )

    col1, col2 = st.columns(2)

    with col1:
        grounded = evaluation.get("groundedness", False)

        if grounded:
            st.success("✅ Grounded")
        else:
            st.error("❌ Not Grounded")

    with col2:
        st.metric(
            "Overall",
            f"{evaluation.get('overall', 0)}/5"
        )

    if evaluation.get("feedback"):
        st.write("**Critic Feedback:**")
        st.info(evaluation["feedback"])