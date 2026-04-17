# Deploy This App

## Recommended Option: Render

This repository now includes:

- `requirements.txt`
- `wsgi.py`
- `render.yaml`
- `Procfile`

## Steps

1. Push this project to GitHub.
2. Sign in to Render.
3. Create a new `Web Service`.
4. Connect your GitHub repository.
5. If Render asks for commands, use:
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn --bind 0.0.0.0:$PORT wsgi:app`
6. Add an environment variable:
   - `SECRET_KEY` = any long random string
7. Deploy the service.

## Important Note About Database

The app currently falls back to SQLite:

- `sqlite:///skin.db`

That is fine for local development, but for a real live deployment you should use either:

- a persistent disk with SQLite, or
- a managed PostgreSQL database and set `DATABASE_URL`

If you set `DATABASE_URL`, the app will use it automatically.

## Local Run

```bash
python run.py
```

Then open:

- `http://127.0.0.1:5001`
