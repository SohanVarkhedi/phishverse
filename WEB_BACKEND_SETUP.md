# PHISHVERSE — Web Backend Setup

Minimal Flask bridge that connects the Employee Portal to the pygame RPG.

---

## Architecture

```
Browser (employee.html)
  │
  │  POST http://localhost:5000/api/launch-game
  │
  ▼
backend/app.py  (Flask + Flask-CORS, port 5000)
  │
  │  subprocess.Popen([python, main.py], cwd=PHISHVERSE/)
  │
  ▼
main.py  (pygame RPG — unchanged)
  │
  │  writes analytics/results/{id}.json
  │  writes ai_results/{id}_ai.json
  │
  ▼
backend/app.py  (GET /api/results/<id> reads them back)
  │
  ▼
Browser (employee.html reads results to populate portal)
```

---

## Setup

```bash
# 1. Install backend dependencies
pip install flask flask-cors

# or from the backend/ requirements file:
pip install -r backend/requirements.txt
```

---

## Running

Open **two terminals**, both rooted at `PHISHVERSE/`:

**Terminal 1 — Flask backend**
```bash
python backend/app.py
# → [PHISHVERSE] Backend starting on http://localhost:5000
# → [PHISHVERSE] Game path: C:\...\PHISHVERSE\main.py
```

**Terminal 2 — Static file server**
```bash
python -m http.server 8000
# → Serving HTTP on 0.0.0.0 port 8000
```

Then open: [http://localhost:8000](http://localhost:8000)

Navigate to the Employee Portal → Entrance Exam → click **Launch PHISHVERSE**.
The pygame game window opens. When you finish, results are written to `analytics/results/`.

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/launch-game` | Spawns `main.py` via subprocess. Returns `{status, message, pid}`. |
| GET | `/api/game-status` | Returns `{status: "running"\|"idle"\|"exited", running: bool, pid}`. |
| GET | `/api/results/<employee_id>` | Returns the risk/analytics JSON written by the game. |
| GET | `/api/ai-results/<employee_id>` | Returns the AI analysis JSON (`ai_results/{id}_ai.json`). |

### POST /api/launch-game — Response shapes

**Success:**
```json
{ "status": "ok", "message": "PHISHVERSE launched.", "pid": 12345 }
```

**Already running:**
```json
{ "status": "already_running", "message": "PHISHVERSE is already running.", "pid": 12345 }
```

**Error:**
```json
{ "status": "error", "message": "main.py not found at ..." }
```

---

## Frontend Wiring (employee.html)

The "Confirm & Launch" button now does:

```js
const res = await fetch('http://localhost:5000/api/launch-game', {
  method:  'POST',
  headers: { 'Content-Type': 'application/json' },
  body:    JSON.stringify({ cycle: '2026.Q2' }),
});
const data = await res.json();
```

- `status === 'ok'` or `'already_running'` → unlock portal stages, show success toast
- `status === 'error'` → show error toast with message
- `fetch` throws (backend offline) → toast: *"Launch failed — start the backend first: python backend/app.py"*

---

## Notes

- The backend does **not** modify `main.py` in any way. It is a pure bridge.
- CORS is enabled for all origins (`*`). Restrict to `localhost:8000` in production.
- The game runs as a child process of the Flask server. Closing the Flask terminal also terminates the game.
- Pass employee context to the game by adding CLI args to the `Popen` call in `app.py`:
  ```python
  subprocess.Popen([sys.executable, str(MAIN_PY), '--employee', employee_id], ...)
  ```
  Then read `sys.argv` in `main.py` to pre-fill registration.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "Launch failed — start the backend first" | Run `python backend/app.py` in a second terminal |
| `ModuleNotFoundError: flask` | Run `pip install flask flask-cors` |
| Game launches but portal doesn't see results | Check `analytics/results/` — file is written at game end, not on launch |
| CORS error in browser console | Confirm Flask is on port 5000 and `flask-cors` is installed |
| Game window doesn't appear | Check pygame is installed: `pip install pygame` |

---

*Last updated: 2026-05-22*
