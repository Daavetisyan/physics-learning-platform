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

## Account and academic-profile foundation

Vector Academy now uses authenticated accounts instead of a global demo student.

Roles:

- `student`: owns one academic profile, enrollments, progress, submissions, tutor sessions, and saved AI conversations
- `tutor`: can view only students connected through an active tutor assignment
- `admin`: can view account, curriculum, enrollment, tutor-assignment, and lesson-publication operations

Guardians are contact/billing-owner records attached to a student profile. They do not receive login accounts in this version.

### Registration and onboarding

1. `GET/POST /register` creates a student account with a salted scrypt password hash.
2. The signed, HTTP-only session continues to `GET/POST /onboarding`.
3. The student independently selects grade 7, 8, or 9 and a `foundation`, `standard`, or `advanced` learning level.
4. Onboarding records the curriculum, timezone, unit preference, guardian contact, consent preference, and initial course enrollment.
5. The personalized dashboard uses that profile and enrollment.

Account routes:

- `GET/POST /register`
- `GET/POST /login`
- `POST /logout`
- `GET/POST /onboarding`
- `GET/POST /account`
- `GET /tutor/students`
- `GET /tutor/students/{student_id}`
- `GET /admin`

Password-reset tokens have a dedicated hashed-token model and expiry fields. Email delivery is not configured, so the platform does not claim that reset mail is sent.

### Curriculum and lesson variants

Seeded curricula:

- US Physical Science — Grades 7–9
- Vector Academy Physics Pathway

The US pathway represents the intended academic market, not standards certification or a claim of complete compliance. Courses are connected through enrollments. A lesson keeps one shared concept record and may expose curriculum/grade/learning-level variants without copying the shared lesson title and assets. `Position and Reference Points` remains published for grades 7–9 at all three learning levels.

### Development accounts

These credentials are seeded only when `APP_ENV` is not `production`:

| Role | Email | Password |
|---|---|---|
| Grade 7 student | `grade7@student.local` | `VectorDemo7!` |
| Grade 8 student | `grade8@student.local` | `VectorDemo8!` |
| Grade 9 student | `grade9@student.local` | `VectorDemo9!` |
| Tutor | `tutor@vector.local` | `VectorTutor1!` |
| Administrator | `admin@vector.local` | `VectorAdmin1!` |

Production startup requires `SESSION_SECRET` and does not seed these weak development credentials.

## Platform features

- Parent-facing landing page
- Student dashboard and course map
- Ten-lesson Motion and Graphs sequence
- Authenticated, student-owned lesson progress in SQLite
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

## Database migration behavior

Startup runs an idempotent, additive SQLite migration before creating missing tables and seeding records. It:

- preserves the existing `students` table and its IDs so progress, tutor, and future homework foreign keys remain valid;
- adds account/profile columns without dropping legacy columns;
- adds lesson concept/course/publication columns and tutor ownership;
- links a legacy `demo@student.example` row to a migrated student account;
- creates users, curricula, courses, enrollments, variants, guardian contacts, tutor assignments, reset tokens, and AI-conversation ownership tables;
- uses unique lookups so repeated startup does not duplicate seeds.

Limitations: this is a lightweight additive migration suitable for the current SQLite application. It does not provide downgrade support, a migration-history table, or complex cross-database transformations. Back up a production database before migration and adopt Alembic before PostgreSQL deployment.

## Security notes

- Passwords are salted and hashed with `hashlib.scrypt`; plaintext passwords are never stored.
- Sessions are signed and use HTTP-only, same-site cookies. Production cookies are secure-only.
- State-changing HTML forms use per-session CSRF tokens.
- Backend route checks enforce roles, enrollment access, student ownership, and tutor assignments.
- Password hashes, guardian billing references, and session data are not rendered in templates.

## Important production gaps

This is not ready to accept real US customers. A public launch still requires:

- Transactional email and a user-facing password-reset delivery flow
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
