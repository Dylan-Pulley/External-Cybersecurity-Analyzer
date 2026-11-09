External Cybersecurity Analyzer

A tool that assesses an organization's security from the outside, the way an attacker with no inside access would see it.

Given a domain you own or are authorized to test, the analyzer discovers what is publicly exposed, checks that exposure against known weaknesses and best practices, and produces a report with severity ratings and remediation guidance.


## Web app and deployment

The Flask frontend and TLS API live in `eca/`. The root-level port analyzer
remains a separate local prototype and is not invoked by the web service.

### Local setup (Python 3.12)

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r eca/requirements-dev.txt
cd eca
../.venv/bin/python -m flask --app app.main run --port 8000
```

Run tests from `eca/` with `../.venv/bin/python -m pytest`.

### Existing Render service settings

- Repository: https://github.com/Dylan-Pulley/External-Cybersecurity-Analyzer
- Branch: `main`
- Root directory: leave blank
- Runtime: Python 3.12
- Build: `pip install -r eca/requirements.txt`
- Start: `gunicorn --chdir eca app.main:app --bind 0.0.0.0:$PORT --workers 2 --access-logfile -`
- Health check: `/api/health`
- Auto-deploy: After CI Checks Pass

The root `render.yaml` provides equivalent settings for new Blueprint deployments,
using `eca` as the root directory and commands relative to that directory.
The existing service uses the repository root with explicit `eca` paths.
Auto Sync on the old seed0x Blueprint is disabled to prevent it overwriting
the service settings; do not manually sync that old Blueprint.
Existing manually configured services must be updated in Render; adding this
file alone does not reconfigure them. GitHub Actions runs tests for pull requests
and main pushes. Render deploys passing main commits directly, without a deploy
hook secret.

The API checks one HTTPS TLS connection. The port scanner is not exposed over
HTTP, and the web app does not provide a complete vulnerability assessment.
