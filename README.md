🔬 ResearchFlow AI
<p align="center"> <b>Multi-Agent Document Research Assistant powered by LangGraph, RAG, Critic-based evaluation, self-correction, and long-term memory.</b> </p>

<p align="center"> <img src="langgraph_workflow.png" alt="ResearchFlow AI LangGraph Workflow" width="430"> </p>

<p align="center"> <img src="https://img.shields.io/badge/Python-3.x-blue?logo=python"> <img src="https://img.shields.io/badge/LangGraph-Agent%20Workflow-purple"> <img src="https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi"> <img src="https://img.shields.io/badge/Streamlit-Frontend-FF4B4B?logo=streamlit"> <img src="https://img.shields.io/badge/ChromaDB-Vector%20Store-orange"> <img src="https://img.shields.io/badge/Groq-LLM-black"> <img src="https://img.shields.io/badge/RAG-Document%20Grounded-blueviolet"> </p>

📌 Overview
ResearchFlow AI is a multi-agent AI research assistant designed to answer questions from a user's document library using a controlled, evidence-grounded workflow.

Instead of using a simple:

Question → Retriever → LLM → Answer
pipeline, ResearchFlow AI uses:

Question
   ↓
Planner
   ↓
Researcher
   ↓
Writer
   ↓
Critic
   ↓
 ┌───────────────┬──────────────────┐
 │               │                  │
 PASS            FAIL               MAX
 │               │                  │
 ▼               ▼                  ▼
Memory      Revision Handler       END
 │               │
 ▼               ▼
END         Researcher
                ↓
              Writer
                ↓
              Critic
The system therefore combines RAG + multi-agent orchestration + evaluation + bounded self-correction + memory.

🎯 Why ResearchFlow AI?
Traditional RAG systems can retrieve relevant chunks and ask an LLM to generate an answer, but that does not explicitly provide:

task planning

independent research and writing responsibilities

answer quality control

evidence-driven revision

bounded self-correction

long-term research memory

structured evaluation

ResearchFlow AI addresses these concerns by turning the research process into a stateful graph.

The goal is not to create a new LLM or a new retrieval algorithm. The main engineering contribution is the orchestration of established AI components into a controlled research workflow.

🧠 Core Workflow
1. Planner
The Planner receives the user's question and creates a research strategy.

Responsibilities:

understand the question

decompose complex questions

generate research queries

determine what information should be investigated

User Question
      ↓
   Planner
      ↓
Research Plan / Queries
2. Researcher
The Researcher performs evidence retrieval from the document collection.

The RAG pipeline is conceptually:

Documents
    ↓
Chunking
    ↓
Embeddings
    ↓
ChromaDB
    ↓
Semantic Retrieval
    ↓
Relevant Evidence
The retrieved evidence is passed to the Writer.

3. Writer
The Writer is responsible for converting retrieved evidence into a readable answer.

It receives:

original question

document evidence

previous research memory when available

research notes

The Writer is instructed to:

prioritize original document evidence

avoid unsupported claims

avoid outside knowledge

avoid inventing facts

state when evidence is insufficient

4. Critic
The Critic acts as a quality-control layer.

It evaluates the generated answer using metrics such as:

Correctness

Completeness

Clarity

Overall quality

Groundedness

Feedback

The Critic also determines whether the workflow should:

PASS
or

FAIL → REVISION
This makes the Critic part of the workflow control logic rather than just a reporting component.

🔄 Self-Correction Loop
One of the key features of ResearchFlow AI is the Critic-driven revision loop.

If the answer fails evaluation:

Critic
   ↓
handle_revision
   ↓
revision_request
   +
revision_count
   ↓
Researcher
   ↓
Writer
   ↓
Critic
The system does not simply ask the Writer to rewrite the same answer.

Instead, it returns to the Researcher, allowing the system to obtain better or stronger evidence before generating another answer.

This gives the workflow a meaningful correction cycle:

Weak Evidence
     ↓
Poor Answer
     ↓
Critic Feedback
     ↓
Better Research
     ↓
Better Answer
     ↓
New Evaluation
🛑 Bounded Revisions
ResearchFlow AI uses:

MAX_REVISIONS = 2
This is an important guardrail.

Without a revision limit, an agentic system could theoretically enter:

Critic
  ↓
Revision
  ↓
Researcher
  ↓
Writer
  ↓
Critic
  ↓
Revision
  ↓
...
forever.

A bounded revision count prevents:

infinite execution

unnecessary LLM calls

excessive latency

uncontrolled API costs

difficult debugging

When the maximum number of revisions is reached, the workflow terminates.

🔀 LangGraph Architecture
The actual ResearchFlow AI graph is:


The graph contains these nodes:

START
  ↓
planner
  ↓
researcher
  ↓
writer
  ↓
critic
After the Critic:

                 ┌── pass ──→ memory ──→ END
                 │
critic ──────────┼── fail ──→ handle_revision
                 │                  ↓
                 │             researcher
                 │
                 └── max_revisions ──→ END
This conditional routing is one of the main reasons LangGraph is useful for this project.

🧩 Shared Research State
All graph nodes operate around a shared ResearchState.

Important state fields include:

Field	Purpose
question	Original user question
plan	Planner output
research_queries	Queries generated for research
retrieved_documents	Retrieved document evidence
research_notes	Research findings
draft_answer	Writer output
critique	Critic evaluation
revision_request	Critic feedback used for revision
revision_count	Number of revisions
final_answer	Final response
This shared state allows information to move through the workflow without manually passing every value between components.

📚 Retrieval-Augmented Generation
ResearchFlow AI uses RAG to ground responses in the document library.

Why RAG?
An LLM's pretrained knowledge is not necessarily the same as the information contained in a user's research papers.

RAG allows the system to retrieve relevant document evidence first:

User Question
      ↓
Semantic Search
      ↓
Relevant Chunks
      ↓
LLM
      ↓
Evidence-Grounded Answer
This reduces the dependency on unsupported model knowledge and makes document-specific question answering possible.

🧠 Long-Term Research Memory
When the Critic accepts the answer:

Critic PASS
     ↓
Memory
     ↓
END
The memory node stores research information using the project's long-term memory implementation backed by ChromaDB.

Stored information includes:

question

answer

research notes

This creates a distinction between:

Session State
Used by Streamlit for UI/session information.

Long-Term Memory
Used by the backend research system for persistent research context.

📊 Evaluation System
ResearchFlow AI does not only return an answer.

The Critic can provide structured evaluation such as:

Correctness    → 5/5
Completeness   → 5/5
Clarity        → 5/5
Overall        → 5/5
Groundedness   → True
Feedback       → ...
This makes the system easier to inspect and improve.

Instead of:

"The LLM generated an answer."

the system can communicate:

"The LLM generated an answer, and an independent Critic evaluated its correctness, completeness, clarity and grounding."

🔌 Backend — FastAPI
FastAPI provides the API boundary between the Streamlit interface and the LangGraph workflow.

Streamlit
    ↓
HTTP Request
    ↓
FastAPI
    ↓
LangGraph
    ↓
Agents / RAG / Memory
    ↓
FastAPI Response
    ↓
Streamlit
API Endpoints
GET /
Backend health/root endpoint.

POST /upload
Accepts PDF files and saves them under:

data/uploads/
The endpoint validates that the uploaded file is a PDF and safely handles the filename.

Note: the shown upload route is responsible for receiving/saving the PDF. The complete parsing, chunking and indexing pipeline may be implemented elsewhere in the repository.

POST /research
Accepts a research question:

{
  "question": "What is the main contribution of this paper?"
}
The backend creates the initial graph state and executes the LangGraph workflow.

The response contains:

question
answer
sources
evaluation
🎨 Frontend — Streamlit
The frontend provides a clean research workspace.

💬 Ask
Users can:

ask research questions

read generated answers

inspect sources

inspect evaluation results

📚 Library
Users can:

upload PDF documents

view documents available in the current session

📊 Evaluate
Users can review Critic-generated evaluation metrics across research questions.

🧠 Memory
Users can view research questions maintained by the current UI session while backend long-term memory is handled separately.

🧹 Answer Cleaning
The backend contains a cleaning layer before returning the final answer.

Conceptually:

Writer Output
     ↓
clean_answer()
     ↓
User-Facing Answer
This prevents internal Writer metadata, research-note sections, and internal explanations from leaking into the final response.

📑 Source Deduplication
Retrieved chunks can sometimes contain repeated:

source + page + chunk
combinations.

ResearchFlow AI creates a unique source key:

(source, page, chunk)
and removes duplicates before sending the sources to the frontend.

This keeps the final Sources section cleaner.

🛡️ Engineering Guardrails
Guardrail	Purpose
MAX_REVISIONS	Prevent infinite Critic loops
Source deduplication	Avoid repeated citations
clean_answer()	Remove internal metadata
PDF validation	Reject unsupported uploads
Safe filename handling	Avoid unsafe paths
Request timeout	Prevent indefinite frontend waits
Structured state	Keep agent communication consistent
🚧 Development Challenges
1. Revision Loop
Problem
A Critic can repeatedly reject an answer.

Solution
A maximum revision count was introduced:

MAX_REVISIONS = 2
Lesson
Agentic workflows need bounded autonomy.

2. Why Not Simply Rewrite?
A naive design could do:

Critic
  ↓
Writer
  ↓
Critic
But if the original problem is weak retrieval, rewriting the same evidence does not solve the problem.

ResearchFlow AI instead uses:

Critic
  ↓
Revision Handler
  ↓
Researcher
This gives the system another opportunity to improve its evidence.

3. Live Execution Visualization
A real-time Planner → Researcher → Writer → Critic UI was explored during development.

The important architectural issue is that a standard:

graph.invoke(...)
execution returns after the graph finishes.

Therefore, a frontend cannot honestly claim to receive genuine real-time node events unless the backend exposes execution events/streaming.

The project ultimately prioritizes a stable:

Answer + Sources + Evaluation
experience instead of simulating real-time execution.

4. Streamlit Reruns
Streamlit reruns the application script after interactions.

Session information is therefore maintained through:

st.session_state
This is used for information such as:

messages

uploaded documents

session UI state

5. Raw HTML Rendering
During development, custom HTML for the pipeline UI appeared literally on the page instead of being rendered.

This demonstrated that custom HTML in Streamlit needs to be handled carefully.

The final interface does not depend on a fake live execution pipeline.

🆚 ResearchFlow AI vs Basic RAG
Basic RAG	ResearchFlow AI
Retrieve → Generate	Plan → Research → Write → Critique
Mostly linear	Conditional graph
No explicit quality gate	Critic quality gate
Usually no self-correction	Bounded revision loop
Answer-focused	Answer + sources + evaluation
Limited workflow state	Shared LangGraph state
Basic retrieval	Multi-agent research workflow
Usually no research memory	ChromaDB long-term memory
The important distinction is workflow intelligence, not claiming a new foundation model.

🔄 Complete End-to-End Example
Suppose the user asks:

"What is the main contribution of this research paper?"

ResearchFlow AI executes:

1. User asks question
             ↓
2. Streamlit sends POST /research
             ↓
3. FastAPI creates ResearchState
             ↓
4. Planner creates research strategy
             ↓
5. Researcher retrieves relevant evidence
             ↓
6. Writer creates draft answer
             ↓
7. Critic evaluates the draft
             ↓
       ┌─────┴─────────┐
       │               │
      PASS            FAIL
       │               │
       ▼               ▼
    Memory       Revision Handler
       │               │
       ▼               ▼
      END          Researcher
                       ↓
                     Writer
                       ↓
                     Critic
Finally:

FastAPI
   ↓
Answer
Sources
Evaluation
   ↓
Streamlit
🏗️ Project Structure
ResearchFlow-AI/
│
├── app.py
├── requirements.txt
├── README.md
├── langgraph_workflow.png
│
├── backend/
│   ├── api/
│   │   └── schemas.py
│   │
│   ├── agents/
│   │   ├── planner.py
│   │   ├── researcher.py
│   │   ├── writer.py
│   │   └── critic.py
│   │
│   ├── graph/
│   │   ├── state.py
│   │   └── workflow.py
│   │
│   ├── memory/
│   │   └── long_term.py
│   │
│   └── routes.py
│
└── data/
    └── uploads/
Additional ingestion/retrieval modules may exist depending on the repository implementation.

⚙️ Tech Stack
Technology	Role
Python	Core development
LangGraph	Stateful agent workflow
Groq	LLM
FastAPI	Backend API
Streamlit	Frontend
Sentence Transformers	Text embeddings
ChromaDB	Vector store / memory
Pydantic	API schemas
Uvicorn	ASGI server
🚀 Run Locally
1. Clone
git clone <your-repository-url>
cd ResearchFlow-AI
2. Create virtual environment
Windows
python -m venv venv
.env\Scripts\Activate.ps1
macOS / Linux
python -m venv venv
source venv/bin/activate
3. Install dependencies
pip install -r requirements.txt
4. Configure environment variables
Create a .env file and add the API credentials required by your backend/LLM configuration.

Do not commit API keys to GitHub.

5. Start FastAPI
uvicorn backend.routes:app --reload
Backend:

http://127.0.0.1:8000
6. Start Streamlit
Open another terminal:

streamlit run app.py
🎤 Interview Explanation
"Tell me about your project."
ResearchFlow AI is a multi-agent document research assistant built using LangGraph and RAG. The system takes a user question, creates a research plan using a Planner agent, retrieves relevant document evidence through the Researcher, generates an answer through the Writer, and then evaluates that answer using a Critic agent. If the Critic rejects the answer, its feedback is converted into a revision request and the workflow goes back to the Researcher for another evidence-gathering cycle. I bounded this revision loop to two attempts to prevent infinite execution and control LLM cost. Once the answer passes evaluation, the research result is stored in long-term ChromaDB memory. FastAPI handles the backend API and Streamlit provides the frontend.

Why LangGraph?
"The workflow has shared state, conditional routing and a Critic-driven revision loop. LangGraph is well suited for representing this kind of stateful graph rather than forcing everything into a simple sequential chain."

Why RAG?
"The assistant needs to answer based on the user's document collection. RAG retrieves relevant evidence and grounds the generated answer in those documents."

Why a Critic?
"The Critic provides an explicit quality gate. Instead of trusting the first generated answer, the system evaluates it and can trigger another research cycle."

Why return to Researcher?
"If the answer is weak because the evidence is insufficient, simply rewriting the same evidence is not enough. Returning to the Researcher allows the system to retrieve stronger evidence."

What happens if the Critic keeps failing?
"The revision counter reaches the maximum allowed revisions and the workflow terminates. This prevents an infinite agent loop."

What is innovative about the project?
"The project is primarily an engineering and orchestration contribution rather than a new ML algorithm. It combines RAG, specialized agents, LangGraph state management, Critic-based evaluation, bounded self-correction and long-term memory into a single research workflow."

🔮 Future Improvements
Possible extensions include:

genuine LangGraph execution streaming

per-node execution timing

structured workflow logging

retrieval evaluation such as Recall@K

answer-quality benchmark datasets

document indexing status

persistent conversation history

authentication

rate limiting

production monitoring

LLM tracing

retry policies

better document ingestion pipelines

automated workflow tests

🧠 Key Takeaway
ResearchFlow AI can be understood as:

RAG
 ↓
Evidence

Agents
 ↓
Specialized Responsibilities

LangGraph
 ↓
Workflow Control

Critic
 ↓
Quality Control

Revision
 ↓
Self-Correction

ChromaDB
 ↓
Long-Term Memory

FastAPI
 ↓
Backend

Streamlit
 ↓
User Interface
So the project is more than an LLM chatbot.

ResearchFlow AI is a controlled, evidence-grounded, multi-agent research workflow built around an LLM.

The LLM is only one component.

The complete system is:

Retrieval + State + Agents + Routing + Evaluation + Revision + Memory + API + UI.

⭐ If you find this project useful
Feel free to explore the repository, experiment with the workflow, and improve the research pipeline.

