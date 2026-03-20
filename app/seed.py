import csv
from sqlmodel import Session, select

from app.database import engine
from app.models import Character


CSV_PATH = "app/data/characters.csv"


def seed_characters():
    with Session(engine) as session:
        with open(CSV_PATH, newline="", encoding="utf-8") as csvfile:
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
    seed_characters()
    print("Seeding complete")