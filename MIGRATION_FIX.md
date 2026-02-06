# Fix: Unknown column 'information_project.created_at'

## Problem
The `/my_info/` endpoint fails with:
```
OperationalError: (1054, "Unknown column 'information_project.created_at' in 'field list'")
```

The `Project` model has `created_at` and `updated_at` fields, but the production MySQL database doesn't have these columns because migration `0007_add_project_timestamps` hasn't been applied.

---

## If You Get: "NodeNotFoundError: Migration ... dependencies reference nonexistent parent node ('information', '0005_remove_auth_models')"

This means migration files on PythonAnywhere are **out of sync**. The file `0005_remove_auth_models.py` is missing.

### Fix: Pull Latest Code First

```bash
cd ~/ludmilportifolio
git pull origin main
```

Then proceed to "Solution: Run Migrations" below.

---

## Solution: Run Migrations on PythonAnywhere

### Step 1: Open PythonAnywhere Console
1. Log in to https://www.pythonanywhere.com
2. Go to the **Consoles** tab
3. Open a **Bash** console (or use an existing one)

### Step 2: Navigate to Your Project
```bash
cd ~/ludmilportifolio
# or wherever your project is located
```

### Step 3: Activate Virtual Environment (if you use one)
```bash
source ~/venv/bin/activate
```

### Step 4: Run Migrations
**Important:** Run `migrate` (not `makemigrations`). Migrations are already created locally.

```bash
python manage.py migrate
```

You should see output like:
```
Running migrations:
  Applying information.0007_add_project_timestamps... OK
```

### Step 5: Reload Your Web App
1. Go to the **Web** tab on PythonAnywhere
2. Click the green **Reload** button for your app

### Step 6: Verify
Visit https://ludmil.pythonanywhere.com/my_info/ — it should now return JSON successfully.

---

## Alternative: Manual SQL (if migrate fails)

If `python manage.py migrate` fails, you can add the columns manually in the MySQL console:

```sql
ALTER TABLE information_project 
ADD COLUMN created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
ADD COLUMN updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6);
```

Then mark the migration as applied:
```bash
python manage.py migrate information 0007_add_project_timestamps --fake
```
