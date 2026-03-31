from core.parsers.update_skills import update_skills
from api import create_app


app = create_app()

if __name__ == "__main__":
    update_skills()
    app.run(debug=True)
