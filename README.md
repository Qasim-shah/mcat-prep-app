# MCAT Prep Web App (Flask)

This is a small web app I built to make MCAT practice less scattered. It helps me do timed sets, review answers, and keep track of progress without getting stuck wiring tools together.

What it does
- User accounts and basic auth
- Add/manage questions and explanations
- Timed practice sessions and review flow
- Saves results so I can see patterns over time

Stack and structure
- Flask app with blueprints (`auth/`, `main/`, `admin/`)
- SQLite locally (simple to set up); can swap to Postgres later
- Templates for a clean, minimal UI; a few helpers and decorators to keep routes tidy

How I approached it
- Keep friction low: start a session fast, see the result fast
- Store just enough data to learn from mistakes (topic, difficulty, time)
- Keep the code straightforward so it’s easy to extend (new sections or tags)

Run locally
1) Python 3.10+ and a virtual env:
   - `python -m venv .venv && source .venv/bin/activate`
   - `pip install -r requirements.txt`
2) Set Flask app and run:
   - `export FLASK_APP=wsgi.py`
   - `flask run`

Notes
- The goal was consistency over complexity. I focused on a smooth practice → review loop rather than packing in every feature from day one.
