# Vector Academy — Interactive Physics Platform

A working full-stack prototype for a detailed Grades 7–9 physics learning and tutoring platform.

## Current production lesson

**Lesson 1: Position and Reference Points** has been rebuilt as the standard for future lessons. It contains:

- Five measurable learning objectives and prerequisite review
- Diagnostic opening question
- Seven precise vocabulary entries
- Nine connected deep-theory chapters
- Ten immediate understanding checks
- Video storyboard and filming requirements
- Interactive reference-frame laboratory
- Five fully reasoned worked examples
- Five explicitly corrected misconceptions
- Twelve differentiated practice problems
- Galileo AI scientist guide with Explain, Guide, and Check modes
- Eight-question mastery assessment
- Seven-part real-world homework investigation
- Summary and exit reflection

Other lessons remain visible in the course map but are intentionally marked as not yet built to the new production standard.

## Platform features already present

- Parent-facing landing page
- Student dashboard and course map
- Ten-lesson Motion and Graphs sequence
- Persistent lesson progress in SQLite
- Browser voice input when supported
- Homework submission and creator review
- Tutor booking with simulated payment and demo Google Meet link
- Focused lesson player with one section or theory chapter per page
- Persistent sidebar navigation, section progress, and Previous/Continue controls
- Assessment question cards with corrected accessible layout
- Responsive mobile and desktop layout
- Automated API and page tests

## First-time GitHub upload

The ChatGPT GitHub connector is read-only. To seed the repository once from this folder, run:

```bash
chmod +x publish_to_github.sh
./publish_to_github.sh
```

The script initializes Git, preserves the existing repository history, and pushes the project to `Daavetisyan/physics-learning-platform`. GitHub may request browser authentication.

## Run locally

```bash
git clone https://github.com/Daavetisyan/physics-learning-platform.git
cd physics-learning-platform
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Open `http://127.0.0.1:8000` and select **Lesson 1: Position and Reference Points**. The lesson now opens as a sequence of focused sections rather than one extremely long page.

## Update an existing local copy

After the first clone, future platform updates do not require another ZIP download:

```bash
cd ~/Downloads/physics-learning-platform
git pull
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

Stop the server with `Ctrl+C`.

## Test

```bash
PYTHONPATH=. pytest -q
```

On Windows PowerShell:

```powershell
$env:PYTHONPATH="."
pytest -q
```

## Content workflow

Read `LESSON_PRODUCTION_STANDARD.md` before building another lesson. A lesson must remain a draft until it passes the academic, interaction, assessment, accessibility, and student-testing quality gates in that document.

## Important production gaps

This is not ready to accept real US customers. A public launch still requires:

- Secure authentication and the parent-payer/student-learner relationship
- Real payment processing, refunds, webhooks, and tax handling
- Google Calendar OAuth and real Meet creation
- Production AI model integration grounded only in approved course material
- Child privacy, consent, terms, and legal review
- Moderation, audit logs, rate limits, and security hardening
- Production hosting, backups, email delivery, and monitoring
- A content-authoring interface for the two course creators

## Architecture

- FastAPI
- Jinja server-rendered pages
- Vanilla JavaScript interactions and simulations
- SQLAlchemy and SQLite
- Migration path to PostgreSQL and a component frontend later
