# Sagen-Async (SAGEN-Sync)

**SAGEN-Sync: Automated Wealth Orchestrator** — a Flask web application for wealth advisors to manage client profiles, enter quarterly financial data, run standardized calculations, and generate client-ready PDF reports (SACS and TCC).

The application lives in [`aw-client-portal/`](aw-client-portal/).

---

## Overview

SAGEN-Sync streamlines quarterly wealth reporting for advisory teams. Advisors maintain static client profiles (individual or married couples), create quarterly reports, enter balances, and finalize reports to trigger the calculation engine. The app then produces two PDF deliverables per report and keeps full history for re-download.

| Area | Description |
|------|-------------|
| **Client management** | CRUD for client/family profiles with retirement, non-retirement, trust, and liability structures stored as JSON |
| **Quarterly reports** | Draft -> data entry -> finalize workflow per client, quarter (Q1-Q4), and year |
| **Calculation engine** | Deterministic SACS (cash flow) and TCC (total client capital) math with buffer/floor rules |
| **PDF generation** | HTML templates rendered to PDF via `xhtml2pdf` (SACS + TCC) |
| **Report history** | Past reports preserved; PDFs can be downloaded again |
| **V2 roadmap** | Stubs for Canva export, automated transfers, external adapters (Schwab, Plaid, etc.) |

---

## Features

### Dashboard
- Client list with last report date
- Quick stats (client count, report count)
- Recent reports across all clients

### Client profiles
- Primary client and optional spouse (married couples)
- Monthly salary, agreed expense budget, private reserve target
- Multiple retirement and non-retirement accounts
- Trust info and liabilities (up to 5)
- Notes and soft limits (e.g. 20 accounts per client)

### Quarterly reports
1. **Create** — New report for a client/quarter/year (status: `draft`)
2. **Data entry** — Account balances, Zillow home value, private reserve balance
3. **Finalize** — Runs `Calculator.calculate_all()` and sets status to `finalized`
4. **PDFs** — Download SACS and TCC documents
5. **History** — Browse and re-download prior reports

### SACS (cash flow summary)
- **Inflow** = monthly salary (after tax)
- **Outflow** = agreed expense budget
- **Excess** = Inflow - Outflow
- **Private reserve target** = (6 x monthly expenses) + insurance deductibles + ($1,000 x number of accounts)
- Buffer warnings when any account balance is below the $1,000 floor

### TCC (total client capital)
- Client 1 and Client 2 retirement totals (summed separately)
- Non-retirement total (trust excluded from this bucket)
- Trust as its own line item
- Liabilities total (displayed separately, not subtracted from grand total)
- **Grand total** = C1 retirement + C2 retirement + non-retirement + trust

### Security (HTTP headers)
- `X-Frame-Options: SAMEORIGIN`
- `X-Content-Type-Options: nosniff`

---

## Tech stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3, Flask 3.0 |
| Database | SQLite (`instance/sagen_sync.db`) |
| PDF | xhtml2pdf 0.2.17 |
| Production server | gunicorn 21.2 |
| Frontend | Jinja2 templates, vanilla JS, CSS |

---

## Project structure

```
aw-client-portal/
├── run.py                 # Dev entry point (port 5000)
├── seed_data.py           # Sample clients and reports
├── requirements.txt
├── app/
│   ├── __init__.py        # Application factory, blueprint registration
│   ├── config.py          # Env-based settings
│   ├── database.py        # SQLite schema and connection handling
│   ├── models/
│   │   ├── client.py      # Client CRUD
│   │   ├── report.py      # Report lifecycle
│   │   └── calculations.py # SACS/TCC calculator engine
│   ├── routes/
│   │   ├── dashboard.py
│   │   ├── client.py
│   │   ├── report.py
│   │   ├── pdf.py
│   │   ├── history.py
│   │   └── canva.py       # V2 stub
│   ├── pdf_templates/     # SACS and TCC HTML for PDF
│   └── utils/             # Validators, Canva API stub
├── frontend/
│   ├── templates/         # Dashboard, forms, preview, history
│   └── static/            # CSS and JS
├── services/              # V2: automation, buffer manager, change detector
└── adapters/              # V2: Schwab, Plaid, RightCapital, PreciseFP stubs
```

---

## Getting started

### Prerequisites
- Python 3.10+ recommended
- pip

### Installation

```bash
cd aw-client-portal
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

### Run locally (development)

```bash
python run.py
```

Open [http://localhost:5000](http://localhost:5000). The dev server runs with `debug=True` on `0.0.0.0:5000`.

Alternative:

```bash
flask run
```

### Seed sample data (optional)

```bash
python seed_data.py
```

Creates two sample clients (single and married) and a draft report for testing.

---

## Configuration

Environment variables (see `app/config.py`):

| Variable | Purpose | Default |
|----------|---------|---------|
| `SECRET_KEY` | Flask session encryption | Dev key in code |
| `RAILWAY_DATABASE_PATH` | SQLite file path | `instance/sagen_sync.db` |
| `CANVA_API_KEY` | Canva export (V2) | None |
| `FLASK_ENV` | `development` or `production` | — |

Constants include a **$1,000 floor per account**, **6 months** for private reserve targeting, and quarterly month ranges (Q1-Q4).

---

## Production deployment

Recommended process manager command:

```bash
gunicorn -w 4 'app:create_app()'
```

Run from the `aw-client-portal` directory so imports resolve. On [Railway](https://railway.app/) or similar platforms, set `RAILWAY_DATABASE_PATH` to a persistent volume path and provide a strong `SECRET_KEY`.

The `instance/` folder (database) is gitignored; create it on first run or mount persistent storage in production.

---

## Database schema

| Table | Role |
|-------|------|
| `clients` | Static profile data; JSON columns for accounts, trust, liabilities |
| `reports` | Per-quarter balances, calculated totals, PDF paths, status |
| `audit_logs` | Reserved for V2 compliance logging |

Deleting a client cascades to their reports.

---

## API / URL map (web UI)

| Path | Feature |
|------|---------|
| `/` | Dashboard |
| `/client/*` | Create, edit, view, delete clients |
| `/report/*` | Report entry, preview, finalize |
| `/pdf/<id>/sacs`, `/pdf/<id>/tcc` | PDF download |
| `/history/*` | Report history |

---

## Roadmap (V2)

Planned but not fully implemented in V1:

- **AutomationService** — Monthly excess transfers (salary - budget - floor)
- **BufferManagerService** — Real-time floor monitoring and alerts
- **External adapters** — Schwab, Plaid, RightCapital, PreciseFP
- **Canva integration** — Export reports to Canva designs

Adapter and service modules exist as architectural stubs under `adapters/` and `services/`.

---

## License

No license file is included in this repository. Add one if you plan to distribute or open-source the project.

---

## Repository

- **GitHub:** [https://github.com/Mjlee079/Sagen-Async.git](https://github.com/Mjlee079/Sagen-Async.git)
