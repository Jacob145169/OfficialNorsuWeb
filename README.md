# NORSU Website and Admin Portal

A Django-based website and content management portal for Negros Oriental State University with public-facing pages, a shared admin dashboard, a super admin dashboard, college-specific administration, alumni management, calendar publishing, inquiry handling, and media/content workflows.

## Overview

This repository contains a single Django project, `norsu_dashboard`, with one main app, `dashboard`. It serves two broad use cases:

- Public university website pages for home, news, programs, alumni, about, directory, calendar, and contact flows.
- Internal administration tools for a superadmin and six college admin accounts.

The project uses MySQL or MariaDB, stores uploaded media locally, and includes both Python tests and JavaScript test files for selected client-side behavior.

## Core Features

### Public website

- Home page with aggregated content and scheduled visibility support.
- News listing and detail pages.
- Programs pages and college-specific content.
- Alumni landing page, directory, news, events, gallery, and media upload flow.
- Academic calendar page with image and PDF support.
- About NORSU and university information pages.
- Contact and inquiry submission endpoints.

### Admin and superadmin tools

- Shared admin login flow for college admins and the superadmin.
- Super Admin dashboard for:
  - posts and announcements
  - news and achievements
  - academic calendar management
  - alumni content management
  - media upload approval and rejection
  - inquiries and replies
  - college data management
  - admin account management
  - archive and backup views
- College admin profile system for:
  - CAS
  - CIT
  - CTED
  - CCJE
  - CBA
  - CAF
- Superadmin account self-service username/password updates from the dashboard.
- College admin account provisioning and credential updates from one workspace.

### Content workflow behavior

Several content types support scheduling and expiry behavior through `scheduled_at`, `expires_at`, and helper methods such as `is_live()`.

This pattern is present in models such as:

- `Post`
- `AlumniNews`
- `AlumniEvent`
- `Achievement`
- `AlumniSuccessStory`

## Tech Stack

- Python
- Django 4.2
- MySQL or MariaDB
- PyMySQL
- python-dotenv
- HTML, CSS, and JavaScript
- CKEditor 5 and Cropper.js loaded from CDNs in the admin templates

## Repository Structure

```text
NORSUWESITE/
├── dashboard/                     # Main Django app
│   ├── management/commands/      # Helper management commands
│   ├── migrations/               # Django migrations
│   ├── static/                   # Source static assets used in development
│   ├── templates/                # Django templates
│   ├── tests/                    # Python and JavaScript-oriented test files
│   ├── models.py                 # Main data model definitions
│   ├── urls.py                   # App routes
│   └── views.py                  # Public, admin, and API views
├── media/                        # Uploaded media files
├── norsu_dashboard/              # Project config package
│   ├── __init__.py               # PyMySQL + MariaDB compatibility hooks
│   ├── settings.py               # Django settings
│   ├── urls.py                   # Project URL config
│   └── wsgi.py/asgi.py
├── staticfiles/                  # Collected/generated static output
├── manage.py
├── .env.example
└── README.md
```

## Main Data Models

The `dashboard` app includes models for the site and admin workflows:

- `College`: college metadata, statistics, descriptions, and hero content.
- `AdminProfile`: links one Django user to one college admin role.
- `Post`: general publishing model for announcements, news, updates, awards, and alumni content.
- `Announcement` and `News`: additional content models.
- `AcademicCalendar`: calendar metadata, images, and PDF upload.
- `UniversityInfo`: vision, mission, mandate, strategic goals, and quality policy.
- `Program`: academic programs with college assignment, dress code assets, and secondary imagery.
- `Faculty` and `Facility`: college resource management.
- `Achievement`: award and recognition content.
- `Alumni`, `AlumniAbout`, `AlumniNews`, `AlumniEvent`, `AlumniSuccessStory`, and `MediaUpload`: alumni portal and engagement features.
- `ContactMessage` and `InquiryReply`: inquiry inbox and response workflow.

## Routes and Modules

### Public pages

Examples of the main public routes from `dashboard/urls.py`:

- `/`
- `/home/`
- `/news/`
- `/programs/`
- `/alumni/`
- `/alumni/about/`
- `/alumni/news/`
- `/alumni/events/`
- `/directory/`
- `/academic-calendar/`
- `/about/`
- `/contacts/`

### Admin pages

- `/admin-login/`
- `/super-admin-login/`
- `/admin-dashboard/`
- `/super-admin-dashboard/`

### API groups

The project also exposes multiple JSON or form-driven endpoints for:

- posts
- announcements and news
- programs
- faculty
- facilities
- university info
- academic calendar
- alumni
- achievements
- success stories
- media uploads
- colleges
- contact messages and replies
- admin accounts

## Environment Variables

Copy `.env.example` to `.env` and adjust the values for your local database:

```env
DB_NAME=norsu_dashboard
DB_USER=root
DB_PASSWORD=
DB_HOST=127.0.0.1
DB_PORT=3306
```

## Database Notes

The project is configured for Django's MySQL backend.

`norsu_dashboard/__init__.py` installs `PyMySQL` as `MySQLdb` and includes compatibility overrides for MariaDB 10.4 and XAMPP-style environments.

That means local development is expected to use a MySQL-compatible database, even though the low-level driver is provided through PyMySQL.

## Local Setup

### 1. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

`requirements.txt` is currently empty in this repository, so install the core packages manually:

```powershell
pip install django==4.2.28 python-dotenv pymysql pillow
```

If you use a different MySQL driver in your environment, adjust accordingly.

### 3. Configure environment variables

```powershell
Copy-Item .env.example .env
```

Then edit `.env` with your local database credentials.

### 4. Apply migrations

```powershell
python manage.py migrate
```

### 5. Optional seed/reset commands

Populate college records and summary stats:

```powershell
python manage.py populate_college_stats
```

Create or reset the primary superadmin account:

```powershell
python manage.py reset_admin_password
```

Current behavior of that command:

- Username: `superadmin`
- Password: `admin123`

Change those credentials immediately from the Super Admin dashboard before using the project outside local development.

### 6. Run the server

```powershell
python manage.py runserver
```

Then open `http://127.0.0.1:8000/`.

## Authentication and Admin Accounts

The admin account system currently supports:

- one superadmin account
- six college admin accounts

### Superadmin paths and credentials

- Superadmin login path: `/super-admin-login/`
- Superadmin dashboard path: `/super-admin-dashboard/`
- Admin account management tab: `/super-admin-dashboard/?tab=admin-accounts`
- Default username after running `python manage.py reset_admin_password`: `superadmin`
- Default password after running `python manage.py reset_admin_password`: `admin123`

### College admin paths and default accounts

- College admin login path: `/admin-login/`
- College admin dashboard path after login: `/admin-dashboard/`

The six college admin accounts are auto-provisioned by the admin account management workflow. Their initial usernames are based on the college key:

- CAS admin: `cas_admin`
- CBA admin: `cba_admin`
- CCJE admin: `ccje_admin`
- CAF admin: `caf_admin`
- CIT admin: `cit_admin`
- CTED admin: `cted_admin`

Important notes:

- These six college admin accounts do not have a usable default password when first provisioned.
- A superadmin must open `/super-admin-dashboard/?tab=admin-accounts` and set each account password manually before that college admin can sign in.
- If one of the default usernames already exists in the database, the system will automatically append a number such as `cas_admin2`.

The superadmin dashboard can:

- view and manage college admin credentials
- update the superadmin's own username and password
- manage platform-wide content and administrative workflows

College admin accounts are backed by `AdminProfile` and are automatically provisioned when needed by the admin account snapshot workflow.

## Static and Media Files

- Source static assets live under `dashboard/static/`.
- Collected or generated static assets live under `staticfiles/`.
- Uploaded user content is stored under `media/`.

During development, media is served when `DEBUG = True`.

## Tests

### Python tests

Run all Django tests:

```powershell
python manage.py test
```

Run the admin account test file only:

```powershell
python manage.py test dashboard.tests.test_admin_auth_and_account_management
```

The repository includes Python tests for areas such as:

- admin authentication and account management
- post visibility and preservation
- university info APIs
- alumni news image consistency
- program APIs
- index styling preservation

### JavaScript test files

The repository also contains JavaScript test files and documentation under `dashboard/tests/`, including:

- `test_achievements_bug.test.js`
- `test_ccje_program_bug.test.js`
- `test_ccje_program_preservation.test.js`
- `README_JAVASCRIPT_TESTS.md`

At the moment, this repository does not include a checked-in `package.json` or Node test configuration at the root, so treat the JavaScript testing guide as documentation for that workflow rather than a fully wired install in the current tree.

## Useful Files to Review

If you are continuing development, these files are the best starting points:

- `dashboard/views.py`
- `dashboard/models.py`
- `dashboard/urls.py`
- `dashboard/templates/dashboard/super-admin-dashboard.html`
- `dashboard/templates/dashboard/admin-dashboard.html`
- `dashboard/static/dashboard/css/super-admin-dashboard.css`
- `dashboard/tests/`

## Current Repo Notes

- `README.md` was previously a placeholder and has now been expanded.
- `requirements.txt` is present but currently empty.
- `staticfiles/` contains generated assets alongside source assets in `dashboard/static/`.
- There are helper scratch files and notes in the repo that appear to support active development and debugging.

## License

No license file is currently included in this repository.
