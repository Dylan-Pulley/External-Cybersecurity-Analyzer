External Cybersecurity Analyzer

A tool that assesses an organization's security from the outside, the way an attacker with no inside access would see it.

Given a domain you own or are authorized to test, the analyzer discovers what is publicly exposed, checks that exposure against known weaknesses and best practices, and produces a report with severity ratings and remediation guidance.

## Flask homepage

I added `app.py`, a small Flask app that shows the External Cybersecurity
Analyzer heading in your browser. This first version is the starting point
for the website. Scanning is still handled separately by Dylan's script.

To run the homepage, open a terminal in this repo and follow the commands for your system.

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
shows the URL Flask received.
Press Ctrl+C in the terminal to stop the server.
