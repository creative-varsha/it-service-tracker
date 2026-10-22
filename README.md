# IT Service Request Tracker

A Django + PostgreSQL web app for raising and managing IT support tickets, replacing ad hoc ticket handling.

## Features
- Secure registration, login/logout, password validation (Django auth)
- 3 roles with role-based access control: **Employee**, **IT Agent**, **Admin**
- 4 ticket categories: Hardware, Software, Network, Access & Accounts
- Create tickets, search (title/description), filter (status/category/priority), pagination
- Comments, close/reopen, agent assignment and status updates
- Form validation on registration, tickets and comments

## Roles
| Role | Can do |
|------|--------|
| Employee | Create tickets, view/comment on/close/reopen **own** tickets |
| IT Agent | View all tickets, assign, change status, comment, close/reopen |
| Admin | Everything above + manage users/roles in `/admin/` |

New registrations are Employees. Promote users to Agent/Admin from `/admin/` -> Profiles.

## Database schema (4 models)
- **Profile**: user (1-1), role
- **Category**: name (unique)
- **Ticket**: title, description, category (FK), priority, status, created_by (FK), assigned_to (FK, nullable), timestamps
- **Comment**: ticket (FK), author (FK), body, created_at

## Setup
```bash
git clone <repo-url> && cd it-service-tracker
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

# PostgreSQL: create a database, then set env vars (see .env.example)
export DB_NAME=tracker_db DB_USER=postgres DB_PASSWORD=yourpassword DB_HOST=localhost
# (If DB_NAME is not set, the app falls back to SQLite for quick local runs.)

python manage.py migrate          # also seeds the 4 categories
python manage.py createsuperuser  # becomes an Admin automatically
python manage.py runserver
```
Open http://127.0.0.1:8000/

## Tests
```bash
python manage.py test
```
