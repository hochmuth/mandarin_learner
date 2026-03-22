# mandarin_learner



# Commands
uv run uvicorn app.main:app --reload
uv run python eval/get_langfuse_success_rate.py


# DB set up
uv run python -m app.init_db
uv run python -m app.seed
uv run python -m app.seed app/data/characters_hsk1.csv

# TO DO