from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import random
import httpx

app = FastAPI()

OPENROUTER_API_KEY = "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"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = "meta-llama/llama-3.3-8b-instruct:free"

flashcards_db = []

class FlashcardInput(BaseModel):
    student_id: str
    question: str
    answer: str

class Flashcard(BaseModel):
    question: str
    answer: str
    subject: str

keyword_subject_map = {
    # Biology
    "photosynthesis": "Biology",
    "cell": "Biology",
    "mitochondria": "Biology",
    "osmosis": "Biology",
    "genetics": "Biology",
    "enzyme": "Biology",
    "DNA": "Biology",
    "RNA": "Biology",
    "evolution": "Biology",
    "organism": "Biology",
    "protein": "Biology",
    "chlorophyll": "Biology",
    "bacteria": "Biology",
    "virus": "Biology",

    # Physics
    "Newton": "Physics",
    "gravity": "Physics",
    "velocity": "Physics",
    "acceleration": "Physics",
    "friction": "Physics",
    "force": "Physics",
    "energy": "Physics",
    "momentum": "Physics",
    "thermodynamics": "Physics",
    "optics": "Physics",
    "wave": "Physics",
    "electricity": "Physics",
    "magnetism": "Physics",
    "quantum": "Physics",

    # Chemistry
    "atom": "Chemistry",
    "molecule": "Chemistry",
    "reaction": "Chemistry",
    "acid": "Chemistry",
    "base": "Chemistry",
    "compound": "Chemistry",
    "element": "Chemistry",
    "organic": "Chemistry",
    "inorganic": "Chemistry",
    "periodic": "Chemistry",
    "ion": "Chemistry",
    "electron": "Chemistry",
    "bond": "Chemistry",
    "catalyst": "Chemistry",

    # Mathematics
    "algebra": "Mathematics",
    "integral": "Mathematics",
    "calculus": "Mathematics",
    "derivative": "Mathematics",
    "geometry": "Mathematics",
    "matrix": "Mathematics",
    "probability": "Mathematics",
    "equation": "Mathematics",
    "statistics": "Mathematics",
    "function": "Mathematics",
    "logarithm": "Mathematics",
    "trigonometry": "Mathematics",
    "vector": "Mathematics",
    "series": "Mathematics",

    # Literature
    "Shakespeare": "Literature",
    "sonnet": "Literature",
    "metaphor": "Literature",
    "poem": "Literature",
    "narrative": "Literature",
    "prose": "Literature",
    "drama": "Literature",
    "tragedy": "Literature",
    "verse": "Literature",
    "theme": "Literature",
    "character": "Literature",
    "plot": "Literature",
    "symbolism": "Literature",

    # History
    "war": "History",
    "revolution": "History",
    "independence": "History",
    "empire": "History",
    "treaty": "History",
    "colonialism": "History",
    "civilization": "History",
    "dynasty": "History",
    "constitution": "History",
    "civil war": "History",
    "invasion": "History",
    "ancient": "History",

    # Computer Science
    "algorithm": "Computer Science",
    "binary": "Computer Science",
    "compiler": "Computer Science",
    "recursion": "Computer Science",
    "loop": "Computer Science",
    "inheritance": "Computer Science",
    "object": "Computer Science",
    "array": "Computer Science",
    "database": "Computer Science",
    "network": "Computer Science",
    "encryption": "Computer Science",
    "hash": "Computer Science",
    "machine learning": "Computer Science",

    # Economics
    "inflation": "Economics",
    "demand": "Economics",
    "supply": "Economics",
    "GDP": "Economics",
    "market": "Economics",
    "trade": "Economics",
    "recession": "Economics",
    "interest": "Economics",
    "tax": "Economics",
    "capital": "Economics",
    "unemployment": "Economics",
    "monopoly": "Economics",

    # Geography
    "continent": "Geography",
    "climate": "Geography",
    "longitude": "Geography",
    "latitude": "Geography",
    "ocean": "Geography",
    "river": "Geography",
    "mountain": "Geography",
    "plate tectonics": "Geography",
    "erosion": "Geography",

    # Psychology
    "cognition": "Psychology",
    "behavior": "Psychology",
    "memory": "Psychology",
    "learning": "Psychology",
    "emotion": "Psychology",
    "motivation": "Psychology",
    "intelligence": "Psychology",
    "perception": "Psychology",
    "stress": "Psychology",

    # Political Science
    "democracy": "Political Science",
    "election": "Political Science",
    "parliament": "Political Science",
    "constitution": "Political Science",
    "legislation": "Political Science",
    "policy": "Political Science",
    "government": "Political Science",
    "ideology": "Political Science"
}

def fallback_subject(question: str) -> str:
    question = question.lower()
    for keyword, subject in keyword_subject_map.items():
        if keyword.lower() in question:
            return subject
    return "General"


def infer_subject_ai(question: str) -> str:
    prompt = f"""
Classify the academic subject of the following question into one of these categories:
Biology, Physics, Chemistry, Mathematics, History, Geography, Literature, Computer Science, or General.

Question: "{question}"
Just return the subject name only, no explanation.
"""

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.post(OPENROUTER_URL, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            subject = result["choices"][0]["message"]["content"].strip()
            return subject if subject else fallback_subject(question)
    except Exception as e:
        print("[WARNING] AI failed, using fallback:", e)
        return fallback_subject(question)

@app.post("/flashcard")
def add_flashcard(card: FlashcardInput):
    subject = infer_subject_ai(card.question)
    flashcards_db.append({
        "student_id": card.student_id,
        "question": card.question,
        "answer": card.answer,
        "subject": subject
    })
    return {"message": "Flashcard added successfully", "subject": subject}

@app.get("/get-subject", response_model=List[Flashcard])
def get_flashcards(student_id: str, limit: int):
    student_cards = [c for c in flashcards_db if c["student_id"] == student_id]

    # Group by subject
    subject_groups = {}
    for card in student_cards:
        subject = card["subject"]
        subject_groups.setdefault(subject, []).append(card)

    # Random selection up to limit
    selected = []
    subjects = list(subject_groups.keys())
    random.shuffle(subjects)
    for subject in subjects:
        if len(selected) >= limit:
            break
        random.shuffle(subject_groups[subject])
        selected.append(subject_groups[subject][0])

    return selected