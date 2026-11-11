External Cybersecurity Analyzer

A tool that assesses an organization's security from the outside, the way an attacker with no inside access would see it.

Given a domain you own or are authorized to test, the analyzer discovers what is publicly exposed, checks that exposure against known weaknesses and best practices, and produces a report with severity ratings and remediation guidance.

**[Open the live homepage](https://eca-web.onrender.com/)**. The form shows the
URL the server received.

## Web interface

- `web/App.tsx` has the React page and URL form.
- `app.py` uses FastAPI to serve the page and receive the URL.
- `main.py` runs Dylan's analyzer from the terminal.

### How the form works

- `home()` in `app.py` sends the built React page when you open `/`.
- `sendUrl()` in `web/App.tsx` reads the URL you typed, sends it to
  `/api/website`, and shows the reply.
- `receive_website()` in `app.py` removes extra spaces, rejects a blank URL,
  and sends the URL back to the page.

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

Clone the repo once to get a local copy.

```bash
git clone https://github.com/Dylan-Pulley/External-Cybersecurity-Analyzer.git
cd External-Cybersecurity-Analyzer
```

1. Start from an up-to-date `main` and make a branch for one change.
2. Commit and push your branch. Open a pull request to `main` and say what
   changed and how you checked it.
3. Open **Checks** on the pull request. **Homepage check** builds React, asks
   FastAPI for the page, and checks that submitting a URL gets the right reply.
4. Review and merge once the check passes. GitHub runs it again on `main`.

### Team tasks

Use the shared task list for owners and due dates. If we use a GitHub board,
add the issues we’re working on and move them through **Todo**, **In Progress**,
and **Done**. Link the pull request to its issue so we can find the code later.

## Render

Use these settings to run FastAPI on the `eca-web` service.
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

Anyone with the live link can open the page. To give a teammate dashboard
access, a Render workspace admin can go to **Settings → Team members → Invite
members** on a workspace with a Pro plan or higher.
