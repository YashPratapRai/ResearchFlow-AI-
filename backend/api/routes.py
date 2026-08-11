import os
import shutil

from fastapi import (
    FastAPI,
    UploadFile,
    File,
    HTTPException
)

from backend.graph.workflow import build_graph
from backend.api.schemas import (
    ResearchRequest,
    ResearchResponse
)


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="AI Research Assistant",
    description="LangGraph powered research assistant",
    version="1.0.0"
)


# ============================================================
# BUILD LANGGRAPH
# ============================================================

graph = build_graph()


# ============================================================
# UPLOAD DIRECTORY
# ============================================================

UPLOAD_DIR = "data/uploads"

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "message": "AI Research Assistant API is running"
    }


# ============================================================
# CLEAN ANSWER
# ============================================================

def clean_answer(answer: str) -> str:

    """
    Remove internal writer metadata
    from the final answer.
    """

    if not answer:
        return ""


    # --------------------------------------------------------
    # Remove Research Notes
    # --------------------------------------------------------

    if "Research Notes:" in answer:

        answer = answer.split(
            "Research Notes:",
            1
        )[0]


    # --------------------------------------------------------
    # Remove internal source summary
    # --------------------------------------------------------

    if (
        "This answer is supported by multiple documents"
        in answer
    ):

        answer = answer.split(
            "This answer is supported by multiple documents",
            1
        )[0]


    # --------------------------------------------------------
    # Remove internal memory explanation
    # --------------------------------------------------------

    memory_text = (
        "Note that this answer is consistent "
        "with the previous research memory"
    )

    if memory_text in answer:

        answer = answer.split(
            memory_text,
            1
        )[0]


    # --------------------------------------------------------
    # Remove internal opening sentence
    # --------------------------------------------------------

    prefix = (
        "Based on the ORIGINAL DOCUMENT EVIDENCE, "
        "the answer to the question"
    )

    if prefix in answer:

        parts = answer.split(
            "is:",
            1
        )

        if len(parts) == 2:

            answer = parts[1]


    return answer.strip()


# ============================================================
# CLEAN SOURCES
# ============================================================

def extract_sources(result):

    """
    Extract unique document sources
    from the final LangGraph state.
    """

    unique_sources = set()

    sources = []


    for doc in result.get(
        "retrieved_documents",
        []
    ):

        metadata = doc.get(
            "metadata",
            {}
        )


        source = metadata.get(
            "source"
        )

        page = metadata.get(
            "page"
        )

        chunk = metadata.get(
            "chunk"
        )


        if not source:
            continue


        source_key = (
            source,
            page,
            chunk
        )


        if source_key in unique_sources:
            continue


        unique_sources.add(
            source_key
        )


        sources.append(
            {
                "source": source,
                "page": page,
                "chunk": chunk
            }
        )


    return sources


# ============================================================
# UPLOAD PDF
# ============================================================

@app.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...)
):

    """
    Upload a PDF research document.

    The PDF is saved inside:
        data/uploads/
    """


    # --------------------------------------------------------
    # Validate filename
    # --------------------------------------------------------

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No file selected."
        )


    # --------------------------------------------------------
    # Validate PDF
    # --------------------------------------------------------

    if not file.filename.lower().endswith(".pdf"):

        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )


    # --------------------------------------------------------
    # Safe filename
    # --------------------------------------------------------

    filename = os.path.basename(
        file.filename
    )


    file_path = os.path.join(
        UPLOAD_DIR,
        filename
    )


    # --------------------------------------------------------
    # Save file
    # --------------------------------------------------------

    try:

        with open(
            file_path,
            "wb"
        ) as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )


        return {
            "message": "PDF uploaded successfully.",
            "filename": filename
        }


    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload PDF: {str(e)}"
        )


    finally:

        await file.close()


# ============================================================
# NORMAL RESEARCH ENDPOINT
# ============================================================

@app.post(
    "/research",
    response_model=ResearchResponse
)
def research(
    request: ResearchRequest
):

    """
    Execute the complete LangGraph research workflow.

    The endpoint waits for the workflow to finish
    and returns the final answer, sources and
    critic evaluation.
    """


    # ========================================================
    # INITIAL STATE
    # ========================================================

    initial_state = {

        "question": request.question,

        "plan": {},

        "research_queries": [],

        "retrieved_documents": [],

        "research_notes": [],

        "draft_answer": "",

        "critique": {},

        "revision_request": "",

        "revision_count": 0,

        "final_answer": ""
    }


    # ========================================================
    # RUN LANGGRAPH
    # ========================================================

    result = graph.invoke(
        initial_state
    )


    # ========================================================
    # ANSWER
    # ========================================================

    raw_answer = (
        result.get("final_answer")
        or result.get("draft_answer")
        or ""
    )


    answer = clean_answer(
        raw_answer
    )


    # ========================================================
    # SOURCES
    # ========================================================

    sources = extract_sources(
        result
    )


    # ========================================================
    # EVALUATION
    # ========================================================

    evaluation = result.get(
        "critique",
        {}
    )


    # ========================================================
    # OPTIONAL EVALUATION METADATA
    # ========================================================
    #
    # These values are added only if the LangGraph state
    # already contains them.
    #
    # They allow the Streamlit frontend to display more
    # useful evaluation statistics without creating a
    # separate streaming endpoint.
    # ========================================================

    if isinstance(
        evaluation,
        dict
    ):

        evaluation = dict(
            evaluation
        )


        if (
            "revision_count"
            not in evaluation
        ):

            evaluation["revision_count"] = result.get(
                "revision_count",
                0
            )


        if (
            "critic_passes"
            not in evaluation
        ):

            evaluation["critic_passes"] = result.get(
                "critic_passes",
                0
            )


        if (
            "critic_failures"
            not in evaluation
        ):

            evaluation["critic_failures"] = result.get(
                "critic_failures",
                0
            )


    # ========================================================
    # RESPONSE
    # ========================================================

    return ResearchResponse(

        question=result.get(
            "question",
            request.question
        ),

        answer=answer,

        sources=sources,

        evaluation=evaluation
    )