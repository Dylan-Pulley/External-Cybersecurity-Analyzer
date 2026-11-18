External Cybersecurity Analyzer

A tool that assesses an organization's security from the outside, the way an attacker with no inside access would see it.

Given a domain you own or are authorized to test, the analyzer discovers what is publicly exposed, checks that exposure against known weaknesses and best practices, and produces a report with severity ratings and remediation guidance.

**[Open the live homepage](https://eca-web.onrender.com/)**. The form shows the
submitted URL and port/TLS scan results in a terminal-style results box.

## Web interface

- `web/App.tsx` has the React page and URL form.
- `app.py` uses FastAPI to serve the page and receive the URL.
- `main.py` coordinates the port and TLS tools and returns their results. It can
  also run from the terminal.

### How the form works

- `home()` in `app.py` sends the built React page when you open `/`.
- `sendUrl()` in `web/App.tsx` sends the URL and the checkbox value to
  `/api/scan`, then displays the returned JSON in the results box.
- `receive_website()` in `app.py` checks that you entered a URL and confirmed
  you have permission, validates the HTTPS URL, and calls `main.main(website_url)`.
- The coordinator runs port and TLS checks concurrently. Each tool returns its
  findings; a tool failure becomes an `error` in that tool's result.
- FastAPI returns `{"website": "https://example.com", "results": {"ports": [], "tls": {}}}`
  with the actual findings. `/api/website` remains an alias for the same scan route.
- The browser shows a loading message while the request runs, then displays the
  results or an API error. This waits for both tools; it does not stream Python
  `print()` output or create a background job.

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
received and the returned scan results. After editing the React page, run
`npm --prefix web run build` again.
Press Ctrl+C to stop the server.

Port scanning also requires the Nmap executable installed on the server and
available on PATH; `python-nmap` is its Python wrapper.

### Integration notes — November 17, 2026

The React form, FastAPI route, and existing port/TLS coordinator are connected.
`Port_Analyzer()` returns its analysis and `main()` returns the combined results.
The API validates blank targets, HTTPS URL syntax, permission confirmation, and
hostname resolution. The TLS tool currently checks certificate expiration.

Validation: React production build and mocked API/tool checks passed, including
both route names, rejected requests, combined results, and partial tool failure.
The GitHub homepage check mocks scanning so CI does not scan external targets.
Live scanner execution and the hosted deployment still need verification.

Follow-up work: background jobs with status/cancellation and timeouts; target
control verification and scan scope enforcement; structured finding presentation.
The permission checkbox records an affirmation, not proof of target control.

## GitHub workflow

Use the [shared task list](https://docs.google.com/spreadsheets/d/1F9M5YKT3g6U5BnnFlEZnJIwIQvLR8aKla8udMgQ3K4g/edit)
for owners, due dates, and progress.

1. Make one change on a branch and open a pull request to `main`.
2. Check that **Homepage check** passes. It builds React and checks that the
   page loads and the form gets a reply.
3. Review and merge. GitHub runs the check again on `main`.

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
