import argparse
import csv
from pathlib import Path

from sqlmodel import Session, select

from app.database import engine
from app.models import Character


DEFAULT_CSV_PATH = Path("app/data/characters.csv")


def parse_args():
    parser = argparse.ArgumentParser(description="Seed characters from a CSV file.")
    parser.add_argument(
        "csv_path",
        nargs="?",
        default=str(DEFAULT_CSV_PATH),
        help="Path to the CSV file to import.",
    )
    return parser.parse_args()


def seed_characters(csv_path: str | Path = DEFAULT_CSV_PATH):
    csv_path = Path(csv_path)

    with Session(engine) as session:
        with csv_path.open(newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                # Convert level to int
                row["level"] = int(row["level"])

                # Check if character already exists
                statement = select(Character).where(
                    Character.character == row["character"]
                )
                existing = session.exec(statement).first()

                if existing:
                    continue

                session.add(Character(**row))

        session.commit()


if __name__ == "__main__":
    args = parse_args()
    seed_characters(args.csv_path)
    print(f"Seeding complete from {args.csv_path}")
