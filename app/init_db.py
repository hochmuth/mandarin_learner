from app.database import create_db


def main():
    create_db()
    print("Database initialized")


if __name__ == "__main__":
    main()
