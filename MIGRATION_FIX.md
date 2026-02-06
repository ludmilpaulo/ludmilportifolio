# Migration Fix Guide for PythonAnywhere

**Note:** Migrations were reset (Feb 2026). Each app now has a single `0001_initial.py` migration.

---

## Solution: Run Migrations on PythonAnywhere

### Step 1: Pull Latest Code
```bash
cd ~/ludmilportifolio
git pull origin main
```

### Step 2: Open PythonAnywhere Console
1. Log in to https://www.pythonanywhere.com
2. Go to the **Consoles** tab
3. Open a **Bash** console (or use an existing one)

### Step 3: Navigate to Your Project
```bash
cd ~/ludmilportifolio
# or wherever your project is located
```

### Step 4: Activate Virtual Environment (if you use one)
```bash
source ~/venv/bin/activate
```

### Step 5: Run Migrations
**Important:** Run `migrate` (not `makemigrations`). Migrations are already in the repo.

```bash
python manage.py migrate
```

If tables already exist, use:
```bash
python manage.py migrate --fake-initial
```

### Step 6: Reload Your Web App
1. Go to the **Web** tab on PythonAnywhere
2. Click the green **Reload** button for your app

### Step 7: Verify
Visit https://ludmil.pythonanywhere.com/my_info/ — it should now return JSON successfully.

---

## If Migrate Fails

**Tables already exist?** Use `--fake-initial` so Django marks migrations as applied without changing the DB:
```bash
python manage.py migrate --fake-initial
```

**Inconsistent migration history?** You may need to reset the `django_migrations` table and re-run with `--fake-initial`. See PYTHONANYWHERE_MIGRATION_FIX.md for admin/accounts ordering.
