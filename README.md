# Smart Plant Irrigation System Using Mamdani Fuzzy Logic

Academic project: a web dashboard where soil moisture, temperature and humidity are processed
by a hand-written Mamdani fuzzy inference system (17 rules, centroid defuzzification) to give
an irrigation level (0-100 %), a category and a recommendation.

> **Important:** this is an academic fuzzy-logic demonstration. The membership ranges and rules
> are project assumptions. They are NOT scientifically calibrated for any specific plant and
> must not be used as real agronomic advice. They can be calibrated with agricultural data.

## Folder structure
```
smart-irrigation-fuzzy/
├── backend/
│   ├── app/
│   │   ├── main.py                  FastAPI app + endpoints
│   │   ├── fuzzy_engine.py          Mamdani inference + centroid (the core)
│   │   ├── membership_functions.py  fuzzy sets, membership functions, fuzzification
│   │   ├── rules.py                 the 17-rule rule base
│   │   ├── schemas.py               request/response shapes + input validation
│   │   ├── database.py              SQLite connection
│   │   └── models.py                the "predictions" table
│   ├── tests/                       55 pytest tests
│   └── requirements.txt
├── frontend/                        React + Vite + Recharts dashboard
└── docs/
    ├── CODE_WALKTHROUGH.md          how each backend file works
    ├── PROJECT_REPORT.md            the 21 report sections
    └── VIVA_QUESTIONS.md            viva questions and answers
```

## Run it (two terminals)

Requires Python 3.10+ and Node.js 18+.

**Terminal 1 - backend** (from `backend/`)
```bash
python -m venv venv
venv\Scripts\activate            # Windows   (macOS/Linux: source venv/bin/activate)
pip install -r requirements.txt
uvicorn app.main:app --reload
```
API docs: http://127.0.0.1:8000/docs

**Terminal 2 - frontend** (from `frontend/`)
```bash
npm install
npm run dev
```
Open http://localhost:5173

## Run the tests (from `backend/`, venv active)
```bash
python -m pytest -v
```
Expected: `55 passed`.

## Troubleshooting
| Problem | Fix |
|---|---|
| `ModuleNotFoundError: app` | Run commands from inside `backend/`. |
| PowerShell blocks `Activate.ps1` | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, or use CMD. |
| Frontend shows "Cannot reach the backend" | Start uvicorn first (port 8000). |
| Port 8000 busy | `uvicorn app.main:app --reload --port 8001` and change the proxy target in `frontend/vite.config.js`. |
| History empty after deleting `irrigation.db` | Normal; the file is recreated on the next start. |
