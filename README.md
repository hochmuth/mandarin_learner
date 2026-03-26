# mandarin_learner

## Purpose
When learning new characters in Mandarin, one common hurdle is that one character can be used in different context (or even be part of different words). It is therefore very helpful to see the character in a variety of different contexts. The goal of this small POC is to help with just that - it doesn't pretend to be a full-scale learning app or anything of the sort. It is nothing but a simple LLM wrapper focused on generating Mandarin sentences that will include a character that the user is trying to learn.
### How do I use this?
There is a list of characters that the user is trying to learn. Out of these you can pick 1-3 (as some words consist of multiple characters) and the LLM will return a few example sentences that you can then either try to translate on your own or see their English translation and pinyin transcription.
### What are the limitations?
At this stage, there are many. But most importantly - the app only uses a small subset of about 150 HSK 1 characters. Some of these are hardcoded as "already learned" (=the LLM can freely use them to generate sentences), while others are "new" - those are the ones the LLM will be generating sample sentences for. Currently there is no possibility of moving characters between these two groups or adding new characters.
- 
### But do we need an LLM for this? Wouldn't a simple sentence library be enough?
The problem with a static library of sentences is that once the learner reads through them once or twice, it doesn't serve as a useful learning tool anymore. It's much better to see a fresh set of practice sentences every time we're facing the challenge of learning a particularly difficult character. The LLMs can be useful for this.

## Installation instructions

This project uses [`uv`](https://docs.astral.sh/uv/) for dependency management.
It was tested on Python 3.13

1. Install `uv` if you do not have it yet:
   `curl -LsSf https://astral.sh/uv/install.sh | sh`

2. Clone the repository and move into it:
   `git clone <your-repo-url>`
   `cd mandarin_learner`

3. Create the virtual environment and install dependencies from `pyproject.toml` / `uv.lock`:
   `uv sync`

4. The project requires OpenAI API key. However, under normal conditions the token count should be low. (Running several dozen test requests approximated to about 1$.) 
Optionally, the project also uses LangFuse for tracing. LangFuse offers a free tier which is more than adequate for testing. (It is possible to run the project without LangFuse but tracing will not work.)
API keys should be set in the `.env` file in the project root, for example:
   `OPENAI_API_KEY=...`
   `LANGFUSE_PUBLIC_KEY=...`
   `LANGFUSE_SECRET_KEY=...`
   `LANGFUSE_HOST=...`

5. Initialize and seed the local database:
   `uv run python -m app.init_db`
   `uv run python -m app.seed app/data/characters_hsk1.csv`

6. After that, you can start the app with:
`uv run uvicorn app.main:app --reload`
Go to http://127.0.0.1:8000/ in your browser to use the tool.
(If you've set up LangFuse keys the trace data should start to flow automatically once you generate your first sentences.)


## Repo structure (high-level overview)

- `app/main.py`: FastAPI entry point. Loads environment variables and registers the API and UI routes.
- `app/routes/`: HTTP endpoints.
  `ui.py` serves the HTML pages.
  `generate.py` exposes the sentence-generation API.
  `characters.py` exposes character-related endpoints.
- `app/services/`: core application logic.
  `generation_service.py` builds the prompt, calls the model, and validates retries.
  `validator.py` checks that generated sentences only use allowed Chinese characters.
  `vocabulary_service.py` fetches character sets used by the routes.
- `app/prompts/generation_prompt.txt`: prompt template used for sentence generation.
- `app/templates/`: Jinja templates for the web UI.
  `index.html` is the home page and sentence-generation flow.
  `result.html` renders generated sentences and error states.
  `known_characters.html` shows the learner’s known-character list.
- `app/models.py`: SQLModel database models.
- `app/schemas.py`: request and response schemas.
- `app/database.py`: database engine and session setup.
- `app/config.py`: app-level configuration such as model names and retry limits.
- `app/init_db.py`: creates the database tables.
- `app/seed.py`: seeds the database with character data.
- `app/data/`: source data files used for seeding.
- `eval/get_langfuse_success_rate.py`: evaluation script for checking Langfuse trace success rates.
- `notebooks/`: exploratory notebooks for data work and trace analysis.
- `pyproject.toml`: project metadata and dependencies.
- `uv.lock`: locked dependency versions for reproducible installs.
- `mandarin.db`: local SQLite database used by the app.