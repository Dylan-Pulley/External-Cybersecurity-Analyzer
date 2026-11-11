External Cybersecurity Analyzer

A tool that assesses an organization's security from the outside, the way an attacker with no inside access would see it.

Given a domain you own or are authorized to test, the analyzer discovers what is publicly exposed, checks that exposure against known weaknesses and best practices, and produces a report with severity ratings and remediation guidance.

## Web interface

- `web/App.tsx` has the React page and URL form.
- `app.py` uses FastAPI to serve the page and receive the URL.
- `main.py` runs Dylan's analyzer from the terminal.

## Run locally

Use Node.js 22.12 or later and Python 3.12. Open a terminal at the top of the
repo, where `app.py` lives. Build the page first. `--prefix web` tells npm
where to find the React files.

```bash
npm --prefix web ci
npm --prefix web run build
```

Then install the Python packages and start the server.

**macOS and Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn app:app --port 8000
```

**Windows (PowerShell)**

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app:app --port 8000
```

Open [localhost:8000](http://127.0.0.1:8000/). The form shows the URL FastAPI
received. After editing the React page, run `npm --prefix web run build` again.
Press Ctrl+C to stop the server.

## GitHub workflow

1. Make your changes on a branch and open a pull request to `main`.
2. Open **Checks** on the pull request. **Homepage check** builds React, asks
   FastAPI for the page, and checks that submitting a URL gets the right reply.
3. Review and merge once the check passes. GitHub runs it again on `main`.

## Render

Use these settings to run FastAPI on [eca-web](https://eca-web.onrender.com/).
Choose **Python 3** and the **`main`** branch. Leave **Root Directory** blank
so Render starts at the top of the repo, where `app.py` lives.

**Build Command** builds the React page and installs the Python packages.

```bash
npm --prefix web ci --include=dev && npm --prefix web run build && python -m pip install -r requirements.txt
```

**Start Command** tells Uvicorn to run the `app` in `app.py`. Render supplies
`$PORT`.

```bash
uvicorn app:app --host 0.0.0.0 --port "$PORT"
```

**Health Check Path** is `/`. Render checks that the homepage responds before
marking the deploy live.

Set **Auto-Deploy** to **After CI Checks Pass** once the FastAPI homepage
check passes on `main` and the first FastAPI deploy is live.
