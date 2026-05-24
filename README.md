# ⚖️ Law In — Legal Knowledge Testing Platform

A Django-based platform for testing legal knowledge. Admins create tests, students (abituriyents) take them.

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Apply migrations
python manage.py migrate

# 3. Seed database with sample data + users
python manage.py seed

# 4. Collect static files
python manage.py collectstatic --noinput

# 5. Run server
python manage.py runserver
```

Then open: http://127.0.0.1:8000

---

## Default Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `admin123` |
| Student | `student1` | `student123` |
| Student | `student2` | `student123` |
| Student | `student3` | `student123` |

---

## Deployment (Render.com)

**Build Command:**
```
pip install -r requirements.txt && python manage.py migrate && python manage.py seed && python manage.py collectstatic --noinput
```

**Start Command:**
```
gunicorn law_in.wsgi:application
```

---

## Features

### Admin
- Django admin panel with **Jazzmin** (light theme)
- Create/edit tests manually via admin
- **Bulk upload** tests from `.xlsx`, `.csv`, `.pdf`, `.docx`
- Download sample templates for each format
- View all student attempts and scores
- Dashboard with stats

### Student (Abituriyent)
- Register & login
- Browse available tests
- Take timed tests with progress tracking
- View detailed results with answer review
- Track history in "My Results"

### UI
- ⚖️ Law-themed design — Navy + Gold palette
- Dark/Light mode toggle (persisted in localStorage)
- Fully responsive (mobile-friendly)
- Smooth CSS animations

---

## Bulk Upload Format

All files must contain a table with these columns:

| Column | Description |
|--------|-------------|
| `test_title` | Groups questions into one test |
| `question_text` | The question |
| `option_a` | Answer option A |
| `option_b` | Answer option B |
| `option_c` | Answer option C |
| `option_d` | Answer option D |
| `correct_answer` | A, B, C, or D |

Download templates from: `/admin/bulk-upload/`

---

## Project Structure

```
law_in/
├── law_in/              # Django project settings & URLs
├── accounts/            # User model, auth views (login/register)
├── tests_app/           # Tests, questions, attempts, bulk upload
│   ├── parsers.py       # xlsx/csv/pdf/docx parsers
│   ├── bulk_views.py    # Bulk upload view + template downloads
│   └── management/
│       └── commands/
│           └── seed.py  # Database seeder
├── templates/           # HTML templates
├── static/
│   ├── css/main.css     # Main styles + dark mode
│   ├── css/auth.css     # Login/register styles
│   └── js/main.js       # Theme toggle, animations
└── requirements.txt
```
