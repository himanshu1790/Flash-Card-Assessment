# Flash-Card-Assessment
This project is a *Flashcard Web API* built using *FastAPI* that allows students to create and retrieve flashcards. It uses *OpenRouter's Meta-LLaMA 3.3 8B* model to infer the academic subject of each question.

If the AI API fails for any reason, the app *automatically falls back* to a hardcoded rule-based subject mapping.

---

## Features

- Add flashcards with AI-detected subject classification
- Retrieve flashcards by mixed subjects
- Fallback mechanism using keyword-based subject mapping
- Built with FastAPI and OpenRouter AI

---

## Installation

### 1. Clone the Repository

```git clone https://github.com/himanshu1790/Flash-Card-Assessment.git``` 


### 2. Install Dependencies

```pip install -r requirements.txt```


## Running the Server

```uvicorn FlashCardAssessment:app --reload```


### Open your browser at:

```http://127.0.0.1:8000/docs```<br>
You’ll see the interactive Swagger UI to test APIs.
