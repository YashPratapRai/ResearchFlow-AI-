import requests


BACKEND_URL = "http://127.0.0.1:8000"


def research_question(question: str):
    response = requests.post(
        f"{BACKEND_URL}/research",
        json={
            "question": question
        },
        timeout=300
    )

    response.raise_for_status()

    return response.json()