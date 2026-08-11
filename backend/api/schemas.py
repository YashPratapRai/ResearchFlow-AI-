from pydantic import BaseModel, Field
from typing import List


class ResearchRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=3,
        description="Research question to answer"
    )


class Source(BaseModel):
    source: str
    page: int | None = None
    chunk: int | None = None


class Evaluation(BaseModel):
    correctness: int | None = None
    completeness: int | None = None
    clarity: int | None = None
    groundedness: bool | None = None
    overall: float | None = None
    passed: bool | None = None
    feedback: str | None = None


class ResearchResponse(BaseModel):
    question: str
    answer: str
    sources: List[Source]
    evaluation: Evaluation | None = None