External Cybersecurity Analyzer

A tool that assesses an organization's security from the outside, the way an attacker with no inside access would see it.

Given a domain you own or are authorized to test, the analyzer discovers what is publicly exposed, checks that exposure against known weaknesses and best practices, and produces a report with severity ratings and remediation guidance.

## Web interface

- `web/App.tsx` is the page you see in the browser.
- `app.py` starts Flask and gets the URL from the form.
- `main.py` runs Dylan's analyzer from the terminal.

You’ll need Node.js and Python. From the repo folder, install the React
packages and build the page.

```bash
npm --prefix web ci
npm --prefix web run build
```

Then start Flask using the commands for your system.

**macOS and Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install Flask
python -m flask --app app run --port 8000
```

**Windows (PowerShell)**

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install Flask
.\.venv\Scripts\python.exe -m flask --app app run --port 8000
```

Open [localhost:8000](http://127.0.0.1:8000/), enter `https://example.com`, and
click **Submit**. Flask sends the URL back so you can check that the form works.
Run `npm --prefix web run build` again after editing the page. Press Ctrl+C
to stop Flask.
