from langgraph.graph import StateGraph, START, END

from backend.graph.state import ResearchState

from backend.agents.planner import planner_agent
from backend.agents.researcher import researcher_agent
from backend.agents.writer import writer_agent
from backend.agents.critic import critic_agent

from backend.memory.long_term import LongTermMemory


MAX_REVISIONS = 2


# ============================================================
# EXECUTION TRACKING HELPERS
# ============================================================


def record_node_execution(
    state: ResearchState,
    node_name: str,
    status: str = "completed",
    extra: dict | None = None
):
    """
    Record execution of a LangGraph node.

    This information can later be shown in the Streamlit UI.
    """

    current_counts = dict(
        state.get("node_counts", {})
    )

    current_counts[node_name] = (
        current_counts.get(node_name, 0) + 1
    )

    event = {
        "node": node_name,
        "status": status
    }

    if extra:
        event.update(extra)

    return {
        "execution_history": [event],
        "node_counts": current_counts
    }


# ============================================================
# PLANNER NODE
# ============================================================


def planner_node(state: ResearchState):

    """
    Execute the existing Planner agent
    and record its execution.
    """

    result = planner_agent(state)

    tracking = record_node_execution(
        state=state,
        node_name="planner",
        status="completed"
    )

    return {
        **result,
        **tracking
    }


# ============================================================
# RESEARCHER NODE
# ============================================================


def researcher_node(state: ResearchState):

    """
    Execute the existing Researcher agent
    and record its execution.
    """

    result = researcher_agent(state)

    tracking = record_node_execution(
        state=state,
        node_name="researcher",
        status="completed"
    )

    return {
        **result,
        **tracking
    }


# ============================================================
# WRITER NODE
# ============================================================


def writer_node(state: ResearchState):

    """
    Execute the existing Writer agent
    and record its execution.
    """

    result = writer_agent(state)

    tracking = record_node_execution(
        state=state,
        node_name="writer",
        status="completed"
    )

    return {
        **result,
        **tracking
    }


# ============================================================
# CRITIC NODE
# ============================================================


def critic_node(state: ResearchState):

    """
    Execute the existing Critic agent.

    In addition to normal critic output, record:

    - critic execution count
    - pass count
    - failure count
    """

    result = critic_agent(state)

    critique = result.get(
        "critique",
        {}
    )

    passed = bool(
        critique.get(
            "passed",
            False
        )
    )

    # --------------------------------------------------------
    # Existing counts
    # --------------------------------------------------------

    current_counts = dict(
        state.get(
            "node_counts",
            {}
        )
    )

    current_counts["critic"] = (
        current_counts.get(
            "critic",
            0
        ) + 1
    )

    # --------------------------------------------------------
    # Pass / Fail counters
    # --------------------------------------------------------

    current_passes = state.get(
        "critic_passes",
        0
    )

    current_failures = state.get(
        "critic_failures",
        0
    )

    if passed:

        current_passes += 1

        status = "passed"

    else:

        current_failures += 1

        status = "failed"

    # --------------------------------------------------------
    # Execution event
    # --------------------------------------------------------

    event = {
        "node": "critic",
        "status": status,
        "passed": passed,
        "revision_count": state.get(
            "revision_count",
            0
        )
    }

    return {
        **result,

        "execution_history": [
            event
        ],

        "node_counts": current_counts,

        "critic_passes": current_passes,

        "critic_failures": current_failures
    }


# ============================================================
# HANDLE CRITIC FEEDBACK / REVISION
# ============================================================


def handle_revision(
    state: ResearchState
):

    """
    Handle Critic feedback and start a new revision cycle.
    """

    critique = state.get(
        "critique",
        {}
    )

    feedback = critique.get(
        "feedback",
        "Improve the answer using stronger evidence."
    )

    current_count = state.get(
        "revision_count",
        0
    )

    new_revision_count = (
        current_count + 1
    )

    # --------------------------------------------------------
    # Update node count
    # --------------------------------------------------------

    current_counts = dict(
        state.get(
            "node_counts",
            {}
        )
    )

    current_counts["revision"] = (
        current_counts.get(
            "revision",
            0
        ) + 1
    )

    # --------------------------------------------------------
    # Execution event
    # --------------------------------------------------------

    event = {
        "node": "revision",
        "status": "completed",
        "revision": new_revision_count,
        "feedback": feedback
    }

    return {

        "revision_request": feedback,

        "revision_count": new_revision_count,

        "execution_history": [
            event
        ],

        "node_counts": current_counts
    }


# ============================================================
# DECIDE WHAT HAPPENS AFTER CRITIC
# ============================================================


def route_after_critic(
    state: ResearchState
):

    critique = state.get(
        "critique",
        {}
    )

    revision_count = state.get(
        "revision_count",
        0
    )

    # --------------------------------------------------------
    # Critic accepted answer
    # --------------------------------------------------------

    if critique.get(
        "passed",
        False
    ):

        return "pass"

    # --------------------------------------------------------
    # Still have revision attempts
    # --------------------------------------------------------

    if revision_count < MAX_REVISIONS:

        return "fail"

    # --------------------------------------------------------
    # Maximum revisions reached
    # --------------------------------------------------------

    return "max_revisions"


# ============================================================
# LONG-TERM MEMORY NODE
# ============================================================


def memory_node(
    state: ResearchState
):

    """
    Save the successful research result
    into ChromaDB long-term memory.
    """

    memory = LongTermMemory()

    question = state.get(
        "question",
        ""
    )

    answer = state.get(
        "draft_answer",
        ""
    )

    research_notes = state.get(
        "research_notes",
        []
    )

    memory_id = memory.save(
        question=question,
        answer=answer,
        research_notes=research_notes
    )

    print(
        "\n" + "=" * 60
    )

    print(
        "MEMORY SAVED"
    )

    print(
        "=" * 60
    )

    print(
        "Memory ID:",
        memory_id
    )

    # --------------------------------------------------------
    # Update node count
    # --------------------------------------------------------

    current_counts = dict(
        state.get(
            "node_counts",
            {}
        )
    )

    current_counts["memory"] = (
        current_counts.get(
            "memory",
            0
        ) + 1
    )

    # --------------------------------------------------------
    # Execution event
    # --------------------------------------------------------

    event = {
        "node": "memory",
        "status": "completed",
        "memory_id": memory_id
    }

    return {

        "final_answer": answer,

        "execution_history": [
            event
        ],

        "node_counts": current_counts
    }


# ============================================================
# BUILD LANGGRAPH
# ============================================================


def build_graph():

    graph = StateGraph(
        ResearchState
    )

    # ========================================================
    # NODES
    # ========================================================

    graph.add_node(
        "planner",
        planner_node
    )

    graph.add_node(
        "researcher",
        researcher_node
    )

    graph.add_node(
        "writer",
        writer_node
    )

    graph.add_node(
        "critic",
        critic_node
    )

    graph.add_node(
        "handle_revision",
        handle_revision
    )

    graph.add_node(
        "memory",
        memory_node
    )

    # ========================================================
    # MAIN FLOW
    # ========================================================

    graph.add_edge(
        START,
        "planner"
    )

    graph.add_edge(
        "planner",
        "researcher"
    )

    graph.add_edge(
        "researcher",
        "writer"
    )

    graph.add_edge(
        "writer",
        "critic"
    )

    # ========================================================
    # CRITIC CONDITIONAL ROUTING
    # ========================================================

    graph.add_conditional_edges(

        "critic",

        route_after_critic,

        {

            "pass": "memory",

            "fail": "handle_revision",

            "max_revisions": END
        }
    )

    # ========================================================
    # REVISION LOOP
    # ========================================================

    graph.add_edge(
        "handle_revision",
        "researcher"
    )

    # ========================================================
    # MEMORY → END
    # ========================================================

    graph.add_edge(
        "memory",
        END
    )

    # ========================================================
    # COMPILE
    # ========================================================

    return graph.compile()