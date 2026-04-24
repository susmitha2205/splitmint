# 💚 SplitMint — Smart Bill Splitting App

SplitMint is a full-featured Django expense-splitting application with AI-powered natural language expense parsing (MintSense), equal/custom/percentage splits, group management, balance calculation, and settlement suggestions.

---

## 🚀 Quick Setup

### 1. Prerequisites
- Python 3.10.11 or higher
- pip
- Git (optional)

---

### 2. Create & Activate Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Configure Environment Variables

Edit the `.env` file in the project root:

```env
SECRET_KEY=django-insecure-splitmint-dev-secret-key-change-in-production-2024
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
GROQ_API_KEY=your-groq-api-key-here   # Optional — for AI MintSense
```

> **Note:** The app works fully without an Anthropic API key. MintSense will use a smart rule-based fallback parser.

---

### 5. Run Migrations

```bash
python manage.py makemigrations users groups expenses
python manage.py migrate
```

---

### 6. Create a Superuser (Admin)

```bash
python manage.py createsuperuser
```

---

### 7. Start the Development Server

```bash
python manage.py runserver
```

Visit: **http://127.0.0.1:8000**

Admin panel: **http://127.0.0.1:8000/admin/**

---

## 📦 Sample Data Setup

After running migrations, register a few users via the UI:

1. Go to `http://127.0.0.1:8000/users/register/`
2. Create 3–4 test accounts (e.g., alice, bob, charlie, diana)
3. Log in as alice
4. Create a group: **Groups → New Group** → "Goa Trip" (category: Trip) → add bob, charlie
5. Add an expense: **Add Expense** → "Dinner at Fisherman's Wharf" → ₹2400 → Equal split
6. Add another: "Cab to Airport" → ₹850 → Custom split (alice: 300, bob: 300, charlie: 250)
7. View balances and settlement suggestions in the group detail page
8. Try **MintSense AI**: type "Paid 1200 for hotel wifi split equally with 2 friends"

---

## 🗂️ Project Structure

```
splitmint/
├── config/          # Django settings, URLs, wsgi, asgi
├── users/           # Registration, login, logout, UserProfile
├── groups/          # Group CRUD, balance engine, settlement algorithm
├── expenses/        # Expense CRUD, split logic (equal/custom/percentage)
├── ai_mintsense/    # Natural language parser, auto-categorization, group AI summary
├── templates/       # Base, navbar, dashboard, home
├── static/          # CSS (dark theme), JS
└── media/           # Uploaded images
```

---

## ✨ Features

| Feature | Details |
|---|---|
| Authentication | Register, Login, Logout with Django auth |
| Groups | Create, edit, delete groups with categories and member management |
| Expenses | Add, edit, delete expenses with date, category, notes |
| Split Types | **Equal** — auto divided; **Custom** — per-person amount; **Percentage** — percentage-based |
| Balance Engine | Per-member net balance calculated from all expense splits |
| Settlement Suggestions | Greedy algorithm to minimize number of transactions |
| Settle Up | Mark individual splits as settled / unsettled |
| Expense Filters | Filter by keyword, category, split type, date range |
| Dashboard | Net balance summary, recent expenses, group overview |
| AI MintSense | Parse expenses from plain English; auto-categorization; AI group summaries |

---

## 🤖 AI MintSense

MintSense uses the **Anthropic Claude API** (claude-3-haiku) to:
- Parse natural language expense descriptions into structured data
- Auto-categorize expense titles
- Generate friendly group spending summaries

**Without API key:** A smart rule-based fallback parser is used automatically — no errors, no broken UI.

To enable AI: Add your `GROQ_API_KEY` to `.env`.

---

## 🛠️ VS Code Tips

1. Install the **Python** and **Django** extensions
2. Set interpreter to your venv: `Ctrl+Shift+P` → "Python: Select Interpreter" → choose `venv`
3. For terminal, use the integrated terminal (`Ctrl+\``)
4. Recommended launch config (`.vscode/launch.json`):

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Django",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/manage.py",
      "args": ["runserver"],
      "django": true
    }
  ]
}
```

---

## 📋 Requirements

```
Django==4.2.7
python-dotenv==1.0.0
Pillow==10.1.0
groq==0.8.0
django-crispy-forms==2.1
crispy-bootstrap5==0.7
```

---

## 🧪 Running Tests

```bash
python manage.py test
```

---

## 🔐 Production Notes

Before deploying:
- Set `DEBUG=False` in `.env`
- Use a strong `SECRET_KEY`
- Configure `ALLOWED_HOSTS` with your domain
- Run `python manage.py collectstatic`
- Use PostgreSQL instead of SQLite
- Set up proper media file serving

---

## 👨‍💻 Built With

- **Django 4.2** — Web framework
- **SQLite** — Database (dev)
- **Bootstrap 5.3** — UI framework
- **Groq API (llama3-8b-8192) — AI features
- **Plus Jakarta Sans** — Typography

---

*SplitMint — Split bills, not friendships.* 💚


---

## ☁️ Free Deployment Guide

### Option 1 — Railway (Easiest, Recommended)

1. Push your project to GitHub (see below)
2. Go to **railway.app** → Sign in with GitHub
3. Click **New Project → Deploy from GitHub Repo**
4. Select your `splitmint` repo
5. Railway auto-detects Django — click **Deploy**
6. Go to **Variables** tab → Add:
   ```
   SECRET_KEY        = any-long-random-string-here
   DEBUG             = False
   GROQ_API_KEY      = your-groq-api-key
   ALLOWED_HOSTS     = your-app.railway.app
   ```
7. Go to **Settings → Networking → Generate Domain**
8. Your site is live at `https://your-app.railway.app` 🎉

**Free tier:** $5 free credits/month (enough for a small app)

---

### Option 2 — Render (Also Free)

1. Push to GitHub
2. Go to **render.com** → New → Web Service
3. Connect your GitHub repo
4. Set:
   - **Build Command:** `./build.sh`
   - **Start Command:** `gunicorn config.wsgi --log-file -`
   - **Python version:** 3.10.11
5. Add environment variables (same as Railway above)
6. Click **Create Web Service**

**Free tier:** Spins down after 15 min inactivity (first request is slow)

---

### Option 3 — PythonAnywhere (Beginner Friendly)

1. Sign up at **pythonanywhere.com** (free account)
2. Go to **Files** → Upload your ZIP → Extract
3. Open a **Bash console**:
   ```bash
   cd splitmint
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py collectstatic
   ```
4. Go to **Web** tab → Add new web app → Manual config → Python 3.10
5. Set:
   - Source code: `/home/yourusername/splitmint`
   - Virtualenv: `/home/yourusername/splitmint/venv`
   - WSGI file: Edit to point to `config.wsgi`
6. Add env vars in the WSGI file or `.env`

**Free tier:** 1 web app, always on, `yourusername.pythonanywhere.com`

---

### 📤 Push to GitHub (Required for Railway/Render)

```bash
# Inside your splitmint/ folder
git init
git add .
git commit -m "Initial SplitMint commit"

# Create a repo on github.com, then:
git remote add origin https://github.com/YOUR_USERNAME/splitmint.git
git branch -M main
git push -u origin main
```

---

### 🗄️ Database Note

- **Locally:** SQLite (works as-is)
- **Railway/Render:** Add a **PostgreSQL** plugin (free) → they auto-set `DATABASE_URL`
- The `settings.py` already handles this automatically

