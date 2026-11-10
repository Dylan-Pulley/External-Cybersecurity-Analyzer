External Cybersecurity Analyzer

A tool that assesses an organization's security from the outside, the way an attacker with no inside access would see it.

Given a domain you own or are authorized to test, the analyzer discovers what is publicly exposed, checks that exposure against known weaknesses and best practices, and produces a report with severity ratings and remediation guidance.

## Web interface

`App.tsx` contains the React page and URL form. Flask serves the built page
and returns the submitted URL so you can see that the form reaches the server.

Open a terminal in this repo with Node.js and Python installed. Build the
React page first. Vite writes the files Flask serves to `dist/`.

```bash
npm ci
npm run build
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

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) to see the page.
Enter a full URL such as `https://example.com` and click **Submit**. The page
shows the URL Flask received. Run `npm run build` again after changing `App.tsx`.
Press Ctrl+C in the terminal to stop the server.
