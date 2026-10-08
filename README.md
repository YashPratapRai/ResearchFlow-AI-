# 🔬 ResearchFlow AI

### Stateful RAG-Based Research Assistant with Multi-Agent Evaluation

ResearchFlow AI is an AI-powered research assistant that transforms the traditional question-answering process into a **stateful, multi-stage research workflow**.

Instead of directly asking an LLM to generate an answer, the system first plans the research, retrieves relevant evidence, generates an evidence-grounded answer, and then evaluates that answer through a dedicated Critic agent.

The goal is **not to build a new LLM or a new retrieval algorithm**. The primary engineering contribution is the orchestration of established AI components into a controlled and stateful research workflow.

---
🚀 Live Demo
Frontend: https://researchflowai1.streamlit.app/

Backend API: https://researchflow-ai-dxh1.onrender.com


📌 Why ResearchFlow AI?
Normal LLM-based research can have problems such as:

Hallucinated information
Unsupported claims
Inconsistent research
No clear research process
Difficulty maintaining previous research
No systematic quality-control step


# 🧠 System Architecture

The overall workflow is:

```text
                         User Question
                              │
                              ▼
                         ┌─────────┐
                         │ Planner │
                         └────┬────┘
                              │
                       Research Queries
                              │
                              ▼
                       ┌────────────┐
                       │ Researcher │
                       └─────┬──────┘
                             │
                      Retrieved Evidence
                             │
                             ▼
                        ┌────────┐
                        │ Writer │
                        └────┬───┘
                             │
                        Draft Answer
                             │
                             ▼
                        ┌────────┐
                        │ Critic │
                        └────┬───┘
                             │
                    ┌────────┴────────┐
                    │                 │
                  PASS              FAIL
                    │                 │
                    ▼                 ▼
               Final Answer      Revision Request
                                      │
                                      ▼
                                  Researcher

The workflow is implemented as a stateful graph, allowing information and revision feedback to flow between different stages.

🚀 Core Workflow
1. Planner

The Planner receives the user's question and creates a research strategy.

Responsibilities
Understand the user's question
Decompose complex questions
Generate targeted research queries
Determine what information needs to be investigated
User Question
      ↓
   Planner
      ↓
Research Plan / Queries

The Planner therefore converts an unstructured question into a structured research strategy.

2. Researcher

The Researcher retrieves evidence from the document collection using the RAG pipeline.

The retrieval process is:

Documents
    ↓
Text Extraction
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

The Researcher can also retrieve information from long-term research memory when previous successful research is available.

                ┌───────────────┐
                │ Document RAG  │
                └───────┬───────┘
                        │
                        ├──────► Retrieved Evidence
                        │
                ┌───────▼───────┐
                │ Research      │
                │ Memory        │
                └───────────────┘

The retrieved evidence is then passed to the Writer.

3. Writer

The Writer converts the retrieved evidence into a readable research answer.

It receives:

Original user question
Retrieved document evidence
Previous research memory, when available
Research notes
Writer principles

The Writer is instructed to:

Prioritize original document evidence
Avoid unsupported claims
Avoid relying on outside knowledge
Avoid inventing facts
Clearly state when available evidence is insufficient
Produce a concise but complete answer

The Writer therefore acts as the evidence-to-answer generation layer.

4. Critic

The Critic acts as the quality-control layer of the workflow.

Instead of treating the first generated answer as final, the Critic evaluates the draft answer.

Evaluation dimensions

The Critic evaluates:

Correctness
Completeness
Clarity
Overall Quality
Groundedness
Feedback

The Critic then determines whether the answer should:

                 Draft Answer
                      │
                      ▼
                   Critic
                      │
              ┌───────┴───────┐
              │               │
            PASS            FAIL
              │               │
              ▼               ▼
        Final Answer      Revision Request
                              │
                              ▼
                          Researcher

If the answer fails evaluation, the Critic generates a revision request.

The Researcher then performs another retrieval cycle focused on the missing or weak information.

This creates an iterative:

Research → Write → Critique → Revise → Research

loop.

🧠 Stateful Research Memory

ResearchFlow AI also maintains long-term research memory using ChromaDB.

Successful research can be stored as:

Question
   +
Answer
   +
Research Notes
   ↓
Embedding
   ↓
ChromaDB
   ↓
Long-Term Memory

When a new question is asked, previous research can be retrieved as supporting context.

However, previous memory is treated as supporting evidence rather than the primary source of truth.

Original document evidence always has higher priority.

🔍 RAG Pipeline

The system uses a semantic retrieval pipeline based on vector embeddings.

PDF / Documents
       ↓
Text Extraction
       ↓
Text Chunking
       ↓
Embedding Model
       ↓
Vector Embeddings
       ↓
ChromaDB
       ↓
Similarity Search
       ↓
Top-K Relevant Chunks
       ↓
Researcher

This allows the system to retrieve semantically relevant passages rather than relying only on keyword matching.

🛠️ Technology Stack
Backend
Python
FastAPI
LangGraph
LangChain
Groq
Retrieval & Memory
ChromaDB
Sentence Transformers
Vector Embeddings
Semantic Search
Document Processing
PyMuPDF
Frontend
Streamlit
Deployment
Render
📁 Project Structure
research_assistant/
│
├── backend/
│   │
│   ├── agents/
│   │   ├── planner.py
│   │   ├── researcher.py
│   │   ├── writer.py
│   │   └── critic.py
│   │
│   ├── api/
│   │   └── routes.py
│   │
│   ├── graph/
│   │   └── workflow.py
│   │
│   ├── rag/
│   │   ├── embeddings.py
│   │   ├── retriever.py
│   │   └── vectorstore.py
│   │
│   ├── memory/
│   │   └── long_term.py
│   │
│   ├── tools/
│   │   └── memory_search.py
│   │
│   └── models/
│       └── llm.py
│
├── app.py
├── app_client.py
├── requirements.txt
└── README.md

🔄 Why This Architecture?

A conventional RAG system often follows:

Question
   ↓
Retrieve
   ↓
Generate
   ↓
Answer

ResearchFlow AI introduces additional control:

Question
   ↓
Plan
   ↓
Research
   ↓
Write
   ↓
Critique
   ↓
Revise if necessary
   ↓
Final Answer

This separates planning, retrieval, generation, and evaluation into dedicated stages.

The Critic is particularly important because it is not only producing an evaluation score. Its output directly influences the workflow by deciding whether the answer should be accepted or sent back for revision.

⭐ Key Features
Stateful multi-agent research workflow
Query decomposition and research planning
Semantic document retrieval
ChromaDB vector storage
Evidence-grounded answer generation
Long-term research memory
Automated answer evaluation
Critic-driven revision loop
FastAPI backend
Streamlit interface
Deployable backend architecture

🎯 Project Objective

ResearchFlow AI demonstrates how established LLM, RAG, vector database, and agent technologies can be combined into a controlled research system.

The key focus is not creating a new foundation model or retrieval algorithm, but designing an orchestration layer that makes the research process:

Plan → Retrieve → Generate → Evaluate → Revise
