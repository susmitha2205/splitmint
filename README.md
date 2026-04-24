# SplitMint — Smart Bill Splitting App

SplitMint is a full-featured Django expense-splitting application with AI-powered natural language expense parsing (MintSense), equal/custom/percentage splits, group management, balance calculation, and settlement suggestions.

---

##  Quick Setup

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

> **Note:** The app works fully without an API key. MintSense will use a smart rule-based fallback parser.

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

##  Sample Data Setup

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

##  Project Structure

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

##  Features

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

##  AI MintSense

MintSense uses the **Anthropic Claude API** (claude-3-haiku) to:
- Parse natural language expense descriptions into structured data
- Auto-categorize expense titles
- Generate friendly group spending summaries

**Without API key:** A smart rule-based fallback parser is used automatically — no errors, no broken UI.

To enable AI: Add your `GROQ_API_KEY` to `.env`.

---

*SplitMint — Split bills, not friendships.* 💚

---

- The `settings.py` already handles this automatically

